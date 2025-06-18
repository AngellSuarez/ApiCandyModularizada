from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.timezone import now
from django.db.models import Count
from datetime import timedelta
from django.db import models

from ..models.cita_venta import CitaVenta
from ..models.estado_cita import EstadoCita
from ..models.servicio_cita import ServicioCita

from ..serializers.servicio_cita import ServicioCitaSerializer

from servicio.models import Servicio

from utils.email_utils import enviar_correo_confirmacion

class ServicioCitaViewSet(viewsets.ModelViewSet):
    queryset = ServicioCita.objects.all()
    serializer_class = ServicioCitaSerializer
    
    def get_queryset(self):
        cita_id = self.request.query_params.get('cita_id')
        if cita_id:
            return ServicioCita.objects.filter(cita_id=cita_id)
        return ServicioCita.objects.all()

    def create(self, request, *args, **kwargs):
        # Si es un solo objeto
        data = request.data.copy()
        if 'servicio_id' in data and 'subtotal' not in data:
            try:
                servicio_id = data['servicio_id']
                servicio = Servicio.objects.get(id=servicio_id)
                data['subtotal'] = servicio.precio
            except Servicio.DoesNotExist:
                pass
            except Exception as e:
                return Response(
                    {"error": f"Error al obtener precio del servicio: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'], url_path='batch')
    def create_batch(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({"error": "Se esperaba una lista de objetos"}, status=status.HTTP_400_BAD_REQUEST)

        created_items = []
        errors = []
        citas_servicios = {}  # agrupamos servicios por cita_id

        for entry in data:
            try:
                # Obtener precio si no viene incluido
                if 'servicio_id' in entry and 'subtotal' not in entry:
                    servicio_id = entry['servicio_id']
                    servicio = Servicio.objects.get(id=servicio_id)
                    entry['subtotal'] = servicio.precio

                serializer = self.get_serializer(data=entry)
                if serializer.is_valid():
                    servicio_cita = serializer.save()

                    cita = servicio_cita.cita_id
                    cliente = cita.cliente_id

                    if cita.id not in citas_servicios:
                        citas_servicios[cita.id] = {
                            "cita": cita,
                            "cliente": cliente,
                            "servicios": []
                        }

                    citas_servicios[cita.id]["servicios"].append({
                        "nombre": servicio_cita.servicio_id.nombre,
                        "subtotal": servicio_cita.subtotal
                    })

                    created_items.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            except Exception as e:
                errors.append({"error": str(e)})

        for data in citas_servicios.values():
            cita = data["cita"]
            cliente = data["cliente"]
            servicios = data["servicios"]

            enviar_correo_confirmacion(
                destinatario=cliente.correo,
                nombre_cliente=cliente.nombre,
                fecha=cita.Fecha,
                hora=cita.Hora,
                servicios=servicios 
            )

        if errors:
            return Response({"created": created_items, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"created": created_items}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'], url_path='servicios-mas-vendidos-mes')
    def servicios_mas_vendidos_mes(self, request):
       try:
         hoy = now().date()
         inicio_mes = hoy.replace(day=1)
         estado_terminada = EstadoCita.objects.get(Estado='Terminada')

         servicios = (
            ServicioCita.objects
            .filter(
                cita_id__Fecha__gte=inicio_mes,
                cita_id__Fecha__lte=hoy,
                cita_id__estado_id=estado_terminada.id
            )
            .values('servicio_id', 'servicio_id__nombre')
            .annotate(ventas=Count('id'))
            .order_by('-ventas')[:3]
         )

         data = [
            {
                "name": item['servicio_id__nombre'],
                "ventas": item['ventas']
            }
            for item in servicios
         ]

         return Response(data, status=status.HTTP_200_OK)
       except Exception as e:
         return Response(
            {"error": f"Error al obtener los servicios más vendidos: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
         
    @action(detail=False, methods=['get'], url_path='servicios-semana-manicurista')
    def servicios_semana_manicurista(self, request):
        try:
          manicurista_id = request.query_params.get('manicurista_id')
          if not manicurista_id:
             return Response({"error": "Se requiere el parámetro 'manicurista_id'."}, status=status.HTTP_400_BAD_REQUEST)

          hoy = now().date()
          inicio_semana = hoy - timedelta(days=hoy.weekday())  # lunes
          fin_semana = inicio_semana + timedelta(days=6)       # domingo

          estado_terminada = EstadoCita.objects.get(Estado='Terminada')

          servicios = (
            ServicioCita.objects
            .filter(
                cita_id__Fecha__gte=inicio_semana,
                cita_id__Fecha__lte=fin_semana,
                cita_id__estado_id=estado_terminada.id,
                cita_id__manicurista_id=manicurista_id
            )
            .values('servicio_id', 'servicio_id__nombre')
            .annotate(cantidad=Count('id'))
            .order_by('-cantidad')[:5]
          ) 

          data = [
            {
                "servicio": item['servicio_id__nombre'],
                "cantidad": item['cantidad']
            }
            for item in servicios
          ]

          return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
          return Response(
            {"error": f"Error al obtener los servicios de la semana: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
          )
        

    def destroy(self, request, *args, **kwargs):
        # Obtener el servicio antes de eliminarlo
        servicio_cita = self.get_object()
        cita = servicio_cita.cita_id
        
        # Eliminar el servicio
        response = super().destroy(request, *args, **kwargs)
        
        if response.status_code == status.HTTP_204_NO_CONTENT:
            nuevo_total = ServicioCita.objects.filter(cita_id=cita).aggregate(
                total=models.Sum('subtotal')
            )['total'] or 0
            
            cita.Total = nuevo_total
            cita.save()
            
            print(f"✅ Total actualizado para cita {cita.id}: ${nuevo_total}")
        
        return response



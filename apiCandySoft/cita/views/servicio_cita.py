from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models.cita_venta import CitaVenta
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

                    # Agrupar los servicios por cita
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

        # Enviar un solo correo por cita
        for data in citas_servicios.values():
            cita = data["cita"]
            cliente = data["cliente"]
            servicios = data["servicios"]

            enviar_correo_confirmacion(
                destinatario=cliente.correo,
                nombre_cliente=cliente.nombre,
                fecha=cita.Fecha,
                hora=cita.Hora,
                servicios=servicios  # nuevo parámetro
            )

        if errors:
            return Response({"created": created_items, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"created": created_items}, status=status.HTTP_201_CREATED)




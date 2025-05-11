from rest_framework import viewsets, status
from datetime import timedelta, date
from django.db.models import Count, Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.cita_venta import CitaVenta
from ..models.estado_cita import EstadoCita
from ..serializers.cita_venta import CitaVentaSerializer
from usuario.models.cliente import Cliente
from usuario.models.manicurista import Manicurista
from collections import defaultdict
import calendar

# from utils.email_utils import enviar_correo

class CitaVentaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaVentaSerializer
    queryset = CitaVenta.objects.all()

    def get_queryset(self):
        queryset = CitaVenta.objects.all()
        manicurista_id = self.request.query_params.get('manicurista_id')
        cliente_id = self.request.query_params.get('cliente_id')
        if manicurista_id is not None:
            queryset = queryset.filter(manicurista_id=manicurista_id)
        if cliente_id is not None:
            queryset = queryset.filter(cliente_id=cliente_id)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            cita = serializer.save()

            cliente = Cliente.objects.get(pk=cita.cliente_id)
            manicurista = Manicurista.objects.get(pk=cita.manicurista_id)

            asunto = "Confirmación de Cita - Servicio de Manicura"
            mensaje = f"""
Estimado/a {cliente.nombre} {cliente.apellido},

Su cita ha sido programada exitosamente.

Detalles de la cita:
- Fecha: {cita.Fecha}
- Hora: {cita.Hora}
- Manicurista: {manicurista.nombre if hasattr(manicurista, 'nombre') else "Su profesional asignado"}
- Descripción: {cita.Descripcion}
- Total: ${cita.Total}

Le esperamos en nuestra ubicación. Si necesita modificar o cancelar su cita, por favor contáctenos con anticipación.

¡Gracias por confiar en nuestros servicios!
            """

            # enviar_correo(cliente.correo, asunto, mensaje)

            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": "Cita creada correctamente y notificación enviada al cliente",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except Cliente.DoesNotExist:
            return Response(
                {"error": "No se encontró información del cliente para enviar la notificación."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": f"Error al crear la cita: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        try:
            cita_venta = self.get_object()
            estado_cancelado = EstadoCita.objects.get(Estado='Cancelada')
            cita_venta.estado_id = estado_cancelado
            cita_venta.save()

            cliente = Cliente.objects.get(pk=cita_venta.cliente_id)

            asunto = "Cancelación de cita - Servicio de Manicura"
            mensaje = f"""
Estimado/a {cliente.nombre} {cliente.apellido},

Le informamos que su cita programada para el {cita_venta.Fecha} a las {cita_venta.Hora} ha sido cancelada.

Si tiene alguna pregunta o desea reprogramar, por favor contáctenos.

Gracias por su comprensión.
            """

            # enviar_correo(cliente.correo, asunto, mensaje)

            return Response(
                {"message": "Cita de venta cancelada correctamente y notificación enviada al cliente"},
                status=status.HTTP_200_OK
            )
        except EstadoCita.DoesNotExist:
            return Response(
                {"error": "El estado 'cancelada' no existe."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Cliente.DoesNotExist:
            return Response(
                {"error": "No se encontró información del cliente para enviar la notificación."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": f"Error al cancelar la cita: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['patch'])
    def cambiar_estado(self, request, pk=None):
        cita_venta = self.get_object()
        estado_pendiente = EstadoCita.objects.get(Estado='Pendiente')
        estado_terminada = EstadoCita.objects.get(Estado='Terminada')
        estado_reprogramada = EstadoCita.objects.get(Estado='Re programada')

        if cita_venta.estado_id == estado_pendiente:
            nuevo_estado = estado_terminada
        else:
            nuevo_estado = estado_reprogramada

        cita_venta.estado_id = nuevo_estado
        cita_venta.save()
        serializer = self.get_serializer(cita_venta)
        return Response({
            "message": f"Estado de la cita de venta cambiado a {nuevo_estado.Estado}",
            "data": serializer.data
        })

    @action(detail=False, methods=['get'], url_path='ganancia-semanal')
    def ganancia_semanal(self, request):
        try:
            hoy = date.today()
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fin_semana = inicio_semana + timedelta(days=6)

            estado_terminada = EstadoCita.objects.get(Estado='Terminada')

            citas = CitaVenta.objects.filter(
                Fecha__range=[inicio_semana, fin_semana],
                estado_id=estado_terminada.id
            )

            total_ganancia = citas.aggregate(total=Sum('Total'))['total'] or 0

            return Response({
                "ganancia_total": total_ganancia,
                "fecha_inicio": inicio_semana.strftime("%d/%m/%Y"),
                "fecha_fin": fin_semana.strftime("%d/%m/%Y")
            }, status=status.HTTP_200_OK)
        except EstadoCita.DoesNotExist:
            return Response({"error": "El estado 'terminada' no existe."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": f"Error al calcular la ganancia semanal: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='servicios-dia')
    def servicios_del_dia(self, request):
        try:
            hoy = date.today()
            estado_terminada = EstadoCita.objects.get(Estado='Terminada')

            citas_hoy = CitaVenta.objects.filter(
                Fecha=hoy,
                estado_id=estado_terminada.id
            )

            resumen = citas_hoy.values('manicurista_id__nombre', 'manicurista_id__apellido') \
                .annotate(servicios=Count('id')) \
                .order_by('-servicios')

            data = [
                {
                    "name": f"{item['manicurista_id__nombre']} {item['manicurista_id__apellido']}",
                    "servicios": item['servicios']
                }
                for item in resumen
            ]

            return Response(data, status=status.HTTP_200_OK)
        except EstadoCita.DoesNotExist:
            return Response({"error": "El estado 'Terminada' no existe."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": f"Error al obtener los servicios del día: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='clientes-top')
    def clientes_top(self, request):
        try:
            estado_terminada = EstadoCita.objects.get(Estado='Terminada')

            top_clientes = CitaVenta.objects.filter(estado_id=estado_terminada.id) \
                .values('cliente_id__nombre', 'cliente_id__apellido') \
                .annotate(citas=Count('id')) \
                .order_by('-citas')[:3]

            data = [
                {
                    "nombre": f"{item['cliente_id__nombre']} {item['cliente_id__apellido']}",
                    "citas": item['citas']
                }
                for item in top_clientes
            ]

            return Response(data, status=status.HTTP_200_OK)
        except EstadoCita.DoesNotExist:
            return Response({"error": "El estado 'Terminada' no existe."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": f"Error al obtener los clientes con más citas: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='citas-semana')
    def citas_semana(self, request):
        try:
            hoy = date.today()
            inicio_semana = hoy - timedelta(days=hoy.weekday())
            fin_semana = inicio_semana + timedelta(days=6)

            estado_pendiente = EstadoCita.objects.get(Estado='Pendiente')
            estado_terminada = EstadoCita.objects.get(Estado='Terminada')

            citas = CitaVenta.objects.filter(
                Fecha__range=[inicio_semana, fin_semana]
            ).values('Fecha', 'estado_id')

            dias = {i: {"name": calendar.day_name[i], "Pendiente": 0, "Terminada": 0} for i in range(7)}

            for cita in citas:
                dia_idx = cita['Fecha'].weekday()
                if cita['estado_id'] == estado_pendiente.id:
                    dias[dia_idx]["Pendiente"] += 1
                elif cita['estado_id'] == estado_terminada.id:
                    dias[dia_idx]["Terminada"] += 1

            resultado = [dias[i] for i in range(7)]

            return Response(resultado, status=status.HTTP_200_OK)
        except EstadoCita.DoesNotExist:
            return Response({"error": "Estados 'Pendiente' o 'Terminada' no existen."},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"error": f"Error al obtener las citas de la semana: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

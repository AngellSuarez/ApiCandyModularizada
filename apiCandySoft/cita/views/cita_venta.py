from rest_framework import viewsets, status
from datetime import timedelta, date
from django.db.models import Sum
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from ..models.cita_venta import CitaVenta
from ..models.estado_cita import EstadoCita

from ..serializers.cita_venta import CitaVentaSerializer

from usuario.models.cliente import Cliente
from usuario.models.manicurista import Manicurista

#from utils.email_utils import enviar_correo

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

            # Obtener los datos necesarios para el correo
            cliente = Cliente.objects.get(pk=cita.cliente_id)
            manicurista = Manicurista.objects.get(pk=cita.manicurista_id)  # Asumiendo que manicurista es un Usuario

            # Preparar el contenido del correo
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

            # Enviar el correo
            #enviar_correo(cliente.correo, asunto, mensaje)

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
            estado_cancelado = EstadoCita.objects.get(Estado='cancelada')
            cita_venta.estado_id = estado_cancelado  # Asume que estado_id almacena el ID del estado
            cita_venta.save()

            # Obtener el cliente para enviar el correo
            cliente = Cliente.objects.get(pk=cita_venta.cliente_id)

            # Preparar el contenido del correo
            asunto = "Cancelación de cita - Servicio de Manicura"
            mensaje = f"""
Estimado/a {cliente.nombre} {cliente.apellido},

Le informamos que su cita programada para el {cita_venta.Fecha} a las {cita_venta.Hora} ha sido cancelada.

Si tiene alguna pregunta o desea reprogramar, por favor contáctenos.

Gracias por su comprensión.
            """

            # Enviar el correo
            enviar_correo(cliente.correo, asunto, mensaje)

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
        estado_pendiente = EstadoCita.objects.get(estado='pendiente')
        estado_terminada = EstadoCita.objects.get(estado='terminada')
        estado_reprogramada = EstadoCita.objects.get(estado='re programada')

        if cita_venta.estado == estado_pendiente:
            nuevo_estado = estado_terminada
        else:
            nuevo_estado = estado_reprogramada

        cita_venta.estado = nuevo_estado
        cita_venta.save()
        serializer = self.get_serializer(cita_venta)
        return Response({
            "message": f"Estado de la cita de venta cambiado a {nuevo_estado.estado}",
            "data": serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='ganancia-semanal')
    def ganancia_semanal(self, request):
        try:
            hoy = date.today()
            inicio_semana = hoy - timedelta(days=hoy.weekday())  # lunes
            fin_semana = inicio_semana + timedelta(days=6)       # domingo

            citas = CitaVenta.objects.filter(Fecha__range=[inicio_semana, fin_semana])
            total_ganancia = citas.aggregate(total=Sum('Total'))['total'] or 0

            return Response({
                "ganancia_total": total_ganancia,
                "fecha_inicio": inicio_semana.strftime("%d/%m/%Y"),
                "fecha_fin": fin_semana.strftime("%d/%m/%Y")
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"error": f"Error al calcular la ganancia semanal: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

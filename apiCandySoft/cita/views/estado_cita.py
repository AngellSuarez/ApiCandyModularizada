from ..models.estado_cita import EstadoCita
from ..serializers.estado_cita import EstadoCitaSerializer
from rest_framework import viewsets

class EstadoCitaViewSet(viewsets.ModelViewSet):
    queryset = EstadoCita.objects.all()
    serializer_class = EstadoCitaSerializer
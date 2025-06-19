from rest_framework import viewsets, status
from rest_framework.response import Response

from ..models.novedades import Novedades
from ..serializers.novedades import NovedadesSerializer

from permisos.custom_permissions import TienePermisoModulo

class NovedadesViewSet(viewsets.ModelViewSet):
    serializer_class = NovedadesSerializer
    queryset = Novedades.objects.all()
    permission_classes = [TienePermisoModulo("Manicurista")];

    def get_queryset(self):
        queryset = Novedades.objects.all()
        manicurista_id = self.request.query_params.get('manicurista_id')

        if manicurista_id:
           queryset = queryset.filter(manicurista_id=manicurista_id)

        return queryset
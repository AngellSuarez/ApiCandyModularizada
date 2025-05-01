from django.db import models

from usuario.models.manicurista import Manicurista
from insumo.models import Insumo

from .abastecimiento import Abastecimiento

class insumoAbastecimiento(models.Model):
    insumo_id = models.ForeignKey(Insumo,on_delete=models.CASCADE)
    abastecimiento_id = models.ForeignKey(Abastecimiento,on_delete=models.CASCADE)
    estado = models.CharField(max_length=30,null=False,default="Uso")
    
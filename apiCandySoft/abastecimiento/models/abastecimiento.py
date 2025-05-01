from django.db import models

from usuario.models.manicurista import Manicurista

class Abastecimiento(models.Model):
    fecha = models.DateField(null=False)
    manicurista_id = models.ForeignKey(Manicurista,on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.fecha} - {self.cantidad} - {self.manicurista_id} - {self.insumo_id}";
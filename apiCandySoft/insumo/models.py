from django.db import models;

class  Marca(models.Model):
    nombre = models.CharField(max_length=40,null=False)
    
    def __str__(self):
        return self.nombre;
    
class Insumo(models.Model):
    ESTADOS_CHOICES = (
        ("activo", "activo"),
        ("inactivo", "inactivo"),
        ("bajo","bajo"),
        ("agotado", "agotado")
    );
    
    nombre = models.CharField(max_length=40,null=False)
    stock = models.IntegerField(null=False,default=0)
    marca_id = models.ForeignKey(Marca,on_delete=models.CASCADE)
    estado = models.CharField(max_length=9,choices=ESTADOS_CHOICES,default="Activo")
    
    def __str__(self):
        return f"{self.nombre} - {self.stock} - {self.marca_id}";
    
    def save(self,*args,**kwargs):
        if self.stock <= 0:
            self.estado = "agotado"
        elif self.stock <= 5:
            self.estado = "bajo"
        else:
            self.estado = "activo"
        super().save(*args,**kwargs)
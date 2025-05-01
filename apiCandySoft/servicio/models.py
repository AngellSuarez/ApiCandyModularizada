from django.db import models

# Create your models here.
class Servicio(models.Model):
    ESTADOS_CHOICES = (
        ("activo", "activo"),
        ("inactivo", "inactivo"),
    );
    
    nombre = models.CharField(max_length=40,null=False)
    descripcion = models.TextField()
    
    precio = models.DecimalField(max_digits=10,decimal_places=2,null=False,default=0.00)
    
    estado = models.CharField(max_length=40,null=False,choices=ESTADOS_CHOICES,default="activo")
    
    url_imagen = models.CharField(max_length=200,null=True,blank=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.precio}";
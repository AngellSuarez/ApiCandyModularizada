from django.db import models
from django.utils import timezone

class Servicio(models.Model):
    ESTADOS_CHOICES = (
        ("Activo", "Activo"),
        ("Inactivo", "Inactivo"),
    )

    TIPO_CHOICES = (
        ("Manicure", "Manicure"),
        ("Pedicure", "Pedicure"),
        ("Uñas acrílicas", "Uñas Acrílicas"),
    )

    nombre = models.CharField(max_length=40, null=False)
    
    descripcion = models.TextField()
    
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, default=0.00)
    
    estado = models.CharField(max_length=40, null=False, choices=ESTADOS_CHOICES, default="Activo")
    
    tipo = models.CharField(max_length=40, null=False, choices=TIPO_CHOICES, default="Manicure")  
    
    url_imagen = models.CharField(max_length=200, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)  

    def __str__(self):
        return f"{self.nombre} - {self.precio} - {self.tipo}"


from django.db import models

# Create your models here.
class Proveedor(models.Model):
    TIPO_PERSONA_CHOICES = (
        ("NATURAL", "NATURAL"),
        ("JURIDICA", "JURIDICA"),
    );
    
    TIPO_DOCUMENTO_CHOICES = (
        ("NIT", "NIT"),
        ("CC", "cedula de ciudadania"),
    );
    
    nombre_empresa = models.CharField(max_length=60,null=True,blank=True)
    
    nombre_representante = models.CharField(max_length=60, null=True, blank=True)
    apellido_representante = models.CharField(max_length=60, null=True,blank=True)
    
    tipo_persona = models.CharField(max_length=8,choices=TIPO_PERSONA_CHOICES,null=False)
    
    tipo_documento = models.CharField(max_length=3,choices=TIPO_DOCUMENTO_CHOICES,null=False)
    
    numero_documento = models.CharField(max_length=15,null=False)
    telefono = models.CharField(max_length=15)
    
    email = models.EmailField(max_length=60)
    
    direccion = models.CharField(max_length=60)
    
    ciudad = models.CharField(max_length=60)
    
    def __str__(self):
        return f"{self.nombre}- {self.representante} - {self.tipo_persona} - {self.tipo_documento} - {self.numero_documento} - {self.telefono} - {self.email} - {self.direccion} - {self.ciudad}";
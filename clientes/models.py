from django.db import models

# Create your models here.

class Cliente (models.Model):
    tipo_documento = models.CharField(max_length = 10)
    numero_documento = models.CharField (max_length=20, unique=True)

    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)

    telefono = models.CharField(max_length=9)
    email = models.EmailField(null=True, unique=True, blank=True)

    direccion = models.TextField()

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombres']
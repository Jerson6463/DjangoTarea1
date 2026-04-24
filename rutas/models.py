from django.db import models

# Create your models here.
class Ruta(models.Model):
    origen = models.CharField(max_length=50)
    destino = models.CharField(max_length=50)

    distancia_km = models.DecimalField(max_digits=8,decimal_places=2)
    tiempo_estimado_horas = models.DecimalField(max_digits=5,decimal_places=2)

    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.origen} → {self.destino}"
    
    class Meta:
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'
        ordering = ['origen']
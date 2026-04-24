from django.contrib import admin
from .models import Ruta

# Register your models here.
@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = (
        'origen',
        'destino',
        'tiempo_estimado_horas'
    )

    list_filter = (
        'activa',
    )

    search_fields = (
        'origen',
        'destino'
    )
    ordering = (
        'origen',
    )

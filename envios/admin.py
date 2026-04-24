from django.contrib import admin
from .models import Encomienda

@admin.register(Encomienda)
class EncomiendaAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'remitente',
        'destinatario',
        'ruta',
        'descripcion',
        'peso_kg',
        'estado',
        'fecha_envio')
    
    list_filter = (
        'estado',
        'ruta',
        'fecha_envio',)
    
    search_fields = (
        'codigo',
        'descripcion',
        'remitente_nombres',
        'destinatario_nombres')
    
    autocomplete_fields = [
        'remitente',
        'destinatario',
        'ruta',
    ]
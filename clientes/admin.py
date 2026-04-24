from django.contrib import admin
from .models import Cliente

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'numero_documento',
        'nombres',
        'apellidos',
        'telefono',
        'email',
        'fecha_registro'
    )

    list_filter = (
        'fecha_registro',
    )

    search_fields = (
        'nombres',
        'apellidos',
        'numero_documento'
    )

    ordering = (
        'nombres',
    )



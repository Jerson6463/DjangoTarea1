# envios/querysets.py
from django.db import models

class EncomiendaQuerySet(models.QuerySet):
    # --- Filtros por estado ---
    def pendientes(self):
        """Filtra encomiendas en estado Pendiente."""
        return self.filter(estado='PE')

    def en_transito(self):
        """Filtra encomiendas en tránsito."""
        return self.filter(estado='TR')

    def entregadas(self):
        """Filtra encomiendas ya entregadas."""
        return self.filter(estado='EN')

    def devueltas(self):
        """Filtra encomiendas devueltas."""
        return self.filter(estado='DV')

    def activas(self):
        """Filtra encomiendas pendientes, en tránsito o en destino."""
        return self.filter(estado__in=['PE', 'TR', 'DE'])

    # --- Filtros compuestos ---
    def por_ruta(self, ruta):
        """Filtra encomiendas por una ruta específica."""
        return self.filter(ruta=ruta)

    def por_remitente(self, cliente):
        """Filtra encomiendas por el cliente remitente."""
        return self.filter(remitente=cliente)

    def por_destinatario(self, cliente):
        """Filtra encomiendas por el cliente destinatario."""
        return self.filter(destinatario=cliente)

    def en_transito_por_ruta(self, ruta):
        """Método encadenado: encomiendas en tránsito en una ruta dada."""
        return self.en_transito().por_ruta(ruta)

    # --- Lógica de negocio específica ---
    def con_retraso(self):
        """Filtra encomiendas activas cuya fecha estimada ya pasó."""
        from django.utils import timezone
        return self.activas().filter(
            fecha_entrega_est__lt=timezone.now().date()
        )

    # --- Optimización de consultas ---
    def con_relaciones(self):
        """Precarga las relaciones más usadas para evitar el problema de consultas N+1."""
        return self.select_related(
            'remitente', 'destinatario', 'ruta', 'empleado_registro'
        )


class ClienteQuerySet(models.QuerySet):
    def activos(self):
        """Filtra clientes con estado Activo (1)."""
        return self.filter(estado=1)

    def de_baja(self):
        """Filtra clientes con estado De baja (9)."""
        return self.filter(estado=9)

    def con_dni(self):
        """Filtra clientes cuyo tipo de documento es DNI."""
        return self.filter(tipo_doc='DNI')

    def buscar(self, termino):
        """Búsqueda por nombre, apellido o número de documento (case-insensitive)."""
        return self.filter(
            models.Q(nombres__icontains=termino) |
            models.Q(apellidos__icontains=termino) |
            models.Q(nro_doc__icontains=termino)
        )


class RutaQuerySet(models.QuerySet):
    def activas(self):
        """Filtra rutas habilitadas (estado 1)."""
        return self.filter(estado=1)

    def por_origen(self, ciudad):
        """Busca rutas que coincidan con la ciudad de origen."""
        return self.filter(origen__icontains=ciudad)

    def por_destino(self, ciudad):
        """Busca rutas que coincidan con la ciudad de destino."""
        return self.filter(destino__icontains=ciudad)
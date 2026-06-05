from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Encomienda
from clientes.models import Cliente
from rutas.models import Ruta
from .serializers import EncomiendaSerializer, EncomiendaDetailSerializer
from .serializers import ClienteSerializer, RutaSerializer
from api.pagination import ClientePagination
from drf_spectacular.utils import extend_schema

@extend_schema(
    summary='Listar clientes activos',
    description='Devuelve todos los clientes con estado Activo, paginados de 20 en 20.',
    tags=['Encomiena'],
)

class EncomiendaListCreateView(generics.ListCreateAPIView):
    queryset = Encomienda.objects.con_relaciones()
    serializer_class = EncomiendaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientePagination

    def perform_create(self, serializer):
        serializer.save(
            empleado_registro=self.request.user.empleado
        )

# ── Encomiendas: detalle + actualizar + eliminar ─────────────────
class EncomiendaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Encomienda.objects.con_relaciones()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Usar serializer diferente según el método"""
        if self.request.method == 'GET':
            return EncomiendaDetailSerializer  # con objetos anidados
        return EncomiendaSerializer  # solo IDs para escritura

# ── Clientes: solo lectura ───────────────────────────────────────
class ClienteListView(generics.ListAPIView):
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ClientePagination

    def get_queryset(self):
        return Cliente.objects.activos()
    
@extend_schema(
    summary = 'Listar rutas activas',
    description = 'Devuelve todas las rutas con estado Activo. Sin paginacion.',
    tags = ['Rutas'],
)

# ── Rutas: solo lectura ──────────────────────────────────────────
class RutaListView(generics.ListAPIView):
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Ruta.objects.activas()
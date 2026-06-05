# envios/viewsets.py - VERSIÓN CORREGIDA Y COMPLETA

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Encomienda, Empleado
from config.choices import EstadoEnvio
from api.filters import EncomiendaFilter
from api.pagination import EncomiendaPagination, HistorialPagination
from api.permissions import EsEmpleadoActivo, EsPropietarioOAdmin
from .serializers import (
    EncomiendaSerializer,
    EncomiendaDetailSerializer,
    HistorialEstadoSerializer,
)

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    OpenApiTypes,
)


@extend_schema_view(
    list=extend_schema(
        summary='Listar encomiendas',
        description='Devuelve la lista paginada de encomiendas. Soporta filtros por estado, busqueda y ordenamiento.',
        tags=['Encomiendas'],
    ),
    create=extend_schema(
        summary='Crear encomienda',
        description='Registra una nueva encomienda en el sistema.',
        tags=['Encomiendas'],
    ),
    retrieve=extend_schema(
        summary='Detalle de encomienda',
        description='Devuelve los datos completos de una encomienda con remitente, destinatario, ruta e historial de estados.',
        tags=['Encomiendas'],
    ),
    update=extend_schema(
        summary='Actualizar encomienda',
        tags=['Encomiendas']
    ),
    partial_update=extend_schema(
        summary='Actualizar parcial',
        tags=['Encomiendas']
    ),
    destroy=extend_schema(
        summary='Eliminar encomienda',
        tags=['Encomiendas']
    ),
)
class EncomiendaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar encomiendas.
    Incluye operaciones CRUD + acciones personalizadas.
    """
    # ========== CONFIGURACIÓN BÁSICA ==========
    # Usar el queryset con relaciones optimizado (de la primera definición)
    queryset = Encomienda.objects.con_relaciones()
    
    # Paginación (de la primera definición)
    pagination_class = EncomiendaPagination
    
    # ========== SERIALIZADORES (fusionado) ==========
    def get_serializer_class(self):
        """Usar serializer diferente según el método"""
        if self.request.method == 'GET' and self.action == 'retrieve':
            return EncomiendaDetailSerializer  # Detalle con objetos anidados
        return EncomiendaSerializer  # Lista y escritura con IDs
    
    # ========== FILTROS Y BÚSQUEDA (de la segunda definición) ==========
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EncomiendaFilter
    search_fields = [
        'codigo',
        'remitente__apellidos',
        'destinatario__apellidos',
        'descripcion',
    ]
    ordering_fields = ['fecha_registro', 'peso_kg', 'costo_envio']
    ordering = ['-fecha_registro']  # orden por defecto
    
    # ========== PERMISOS (de la segunda definición) ==========
    permission_classes = [EsEmpleadoActivo]

    def get_permissions(self):
        """Permisos distintos según la acción"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [EsEmpleadoActivo(), EsPropietarioOAdmin()]
        return [EsEmpleadoActivo()]
    
    # ========== MÉTODOS PERSONALIZADOS (de la primera definición) ==========
    
    def perform_create(self, serializer):
        """Al crear, asignar el empleado que registra"""
        serializer.save(
            empleado_registro=self.request.user.empleado
        )
    
    @extend_schema(
        summary='Cambiar estado de encomienda',
        description='''
            Cambia el estado de una encomienda y registra el cambio
            automaticamente en el historial de estados.
            Estados disponibles:
            - PE: Pendiente
            - TR: En transito
            - DE: En destino
            - EN: Entregado
            - DV: Devuelto
        ''',
        request=OpenApiTypes.OBJECT,
        responses={
            200: EncomiendaSerializer,
            400: OpenApiResponse(description='Estado invalido o ya en ese estado'),
        },
        examples=[
            OpenApiExample(
                'Pasar a En transito',
                value={'estado': 'TR', 'observacion': 'Recogido en agencia Lima'},
                request_only=True,
            ),
            OpenApiExample(
                'Marcar como Entregado',
                value={'estado': 'EN', 'observacion': 'Entregado al destinatario'},
                request_only=True,
            ),
        ],
        tags=['Encomiendas'],
    )
    @action(detail=True, methods=['post'], url_path='cambiar_estado')
    def cambiar_estado(self, request, pk=None):
        enc = self.get_object()
        nuevo_estado = request.data.get('estado')
        observacion = request.data.get('observacion', '')

        if not nuevo_estado:
            return Response({'error': 'El campo estado es requerido.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            empleado = Empleado.objects.get(email=request.user.email)
            enc.cambiar_estado(nuevo_estado, empleado, observacion)
            return Response(EncomiendaSerializer(enc).data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary='Encomiendas con retraso',
        description='Lista todas las encomiendas activas cuya fecha estimada de entrega ya pasó.',
        tags=['Encomiendas'],
    )
    @action(detail=False, methods=['get'], url_path='con_retraso')
    def con_retraso(self, request):
        qs = Encomienda.objects.con_retraso().con_relaciones()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Encomiendas pendientes',
        description='Lista todas las encomiendas en estado Pendiente.',
        tags=['Encomiendas'],
    )
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        qs = Encomienda.objects.pendientes().con_relaciones()
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary='Historial de estados',
        description='Devuelve el historial de cambios de estado de una encomienda, paginado con limit/offset.',
        parameters=[
            OpenApiParameter('limit', type=int, description='Numero de resultados', default=10),
            OpenApiParameter('offset', type=int, description='Posicion de inicio', default=0),
        ],
        tags=['Encomiendas'],
    )
    @action(detail=True, methods=['get'], url_path='historial')
    def historial(self, request, pk=None):
        enc = self.get_object()
        qs = enc.historial.select_related('empleado').order_by('-fecha_cambio')

        paginator = HistorialPagination()
        page = paginator.paginate_queryset(qs, request)

        if page is not None:
            return paginator.get_paginated_response(
                HistorialEstadoSerializer(page, many=True).data
            )
        return Response(HistorialEstadoSerializer(qs, many=True).data)

    @extend_schema(
        summary='Estadísticas globales',
        description='Contadores del sistema: activas, en tránsito, con retraso y entregadas hoy.',
        tags=['Encomiendas'],
    )
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        from django.utils import timezone
        hoy = timezone.now().date()

        return Response({
            'total_activas': Encomienda.objects.activas().count(),
            'en_transito': Encomienda.objects.en_transito().count(),
            'con_retraso': Encomienda.objects.con_retraso().count(),
            'entregadas_hoy': Encomienda.objects.filter(
                estado='EN', fecha_entrega_real=hoy
            ).count(),
        })
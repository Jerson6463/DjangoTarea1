from rest_framework import serializers
from .models import Encomienda, HistorialEstado, Empleado
from clientes.models import Cliente
from rutas.models import Ruta
from django.utils import timezone

class ClienteSerializer(serializers.ModelSerializer):
    # @property del modelo expuesta como campo de solo lectura
    nombre_completo = serializers.ReadOnlyField()
    esta_activo = serializers.ReadOnlyField()

    class Meta:
        model = Cliente
        fields = [
            'id', 'tipo_doc', 'nro_doc',
            'nombres', 'apellidos', 'nombre_completo',
            'telefono', 'email', 'esta_activo',
        ]

class RutaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ruta
        fields = [
            'id', 'codigo', 'origen', 'destino',
            'precio_base', 'dias_entrega', 'estado',
        ]

class HistorialEstadoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.ReadOnlyField(source='empleado.__str__')
    estado_anterior_display = serializers.CharField(
        source='get_estado_anterior_display', read_only=True
    )
    estado_nuevo_display = serializers.CharField(
        source='get_estado_nuevo_display', read_only=True
    )

    class Meta:
        model = HistorialEstado
        fields = [
            'id', 'estado_anterior', 'estado_anterior_display',
            'estado_nuevo', 'estado_nuevo_display',
            'empleado_nombre', 'observacion', 'fecha_cambio',
        ]

class EncomiendaSerializer(serializers.ModelSerializer):
    # Propiedades del modelo como campos de solo lectura
    esta_entregada = serializers.ReadOnlyField()
    tiene_retraso = serializers.ReadOnlyField()
    dias_en_transito = serializers.ReadOnlyField()
    descripcion_corta = serializers.ReadOnlyField()
    # Campo calculado con método
    estado_display = serializers.SerializerMethodField()

    class Meta:
        model = Encomienda
        fields = [
            'id', 'codigo', 'descripcion', 'descripcion_corta',
            'peso_kg', 'volumen_cm3', 'costo_envio',
            'remitente', 'destinatario', 'ruta', 'empleado_registro',
            'estado', 'estado_display',
            'fecha_registro', 'fecha_entrega_est', 'fecha_entrega_real',
            'esta_entregada', 'tiene_retraso', 'dias_en_transito',
            'observaciones',
        ]
    read_only_fields = ['codigo', 'fecha_registro', 'fecha_entrega_real']

    def get_estado_display(self, obj):
        return obj.get_estado_display()
    
    def validate_peso_kg(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'El peso debe ser mayor a 0 kg.'
            )
        if value > 500:
            raise serializers.ValidationError(
                'El peso máximo permitido es 500 kg.'
            )
        return value

    def validate_codigo(self, value):
        if not value.startswith('ENC-'):
            raise serializers.ValidationError(
                'El código debe comenzar con ENC-'
            )
        return value.upper()

    def validate_costo_envio(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'El costo no puede ser negativo.'
            )
        return value

    # ── Validación cruzada: validate() ──────────────────────────
    def validate(self, data):
        errors = {}

        # Regla 1: remitente != destinatario
        if data.get('remitente') == data.get('destinatario'):
            errors['destinatario'] = (
                'El destinatario no puede ser el mismo que el remitente.'
            )

        # Regla 2: fecha estimada no en el pasado
        fecha_est = data.get('fecha_entrega_est')
        if fecha_est and fecha_est < timezone.now().date():
            errors['fecha_entrega_est'] = (
                'La fecha estimada no puede ser en el pasado.'
            )

        # Regla 3: costo mínimo según la ruta
        ruta = data.get('ruta')
        costo = data.get('costo_envio')
        if ruta and costo and costo < float(ruta.precio_base):
            errors['costo_envio'] = (
                f'El costo mínimo para esta ruta es S/ {ruta.precio_base}.'
            )

        if errors:
            raise serializers.ValidationError(errors)

        return data

class EncomiendaDetailSerializer(serializers.ModelSerializer):
    """
    Para GET: devuelve objetos anidados completos
    Para POST/PUT/PATCH: acepta solo IDs (write_only)
    """
    # Campos de solo lectura: objetos anidados completos
    remitente = ClienteSerializer(read_only=True)
    destinatario = ClienteSerializer(read_only=True)
    ruta = RutaSerializer(read_only=True)

    # Campos de solo escritura: aceptar ID para crear/actualizar
    remitente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True, source='remitente'
    )
    destinatario_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.activos(),
        write_only=True, source='destinatario'
    )
    ruta_id = serializers.PrimaryKeyRelatedField(
        queryset=Ruta.objects.activas(),
        write_only=True, source='ruta'
    )

    # Historial: los últimos 5 cambios de estado
    historial = serializers.SerializerMethodField()

    # Propiedades del modelo
    esta_entregada = serializers.ReadOnlyField()
    tiene_retraso = serializers.ReadOnlyField()
    dias_en_transito = serializers.ReadOnlyField()

    class Meta:
        model = Encomienda
        fields = [
            'id', 'codigo', 'descripcion', 'peso_kg',
            'remitente', 'remitente_id',
            'destinatario', 'destinatario_id',
            'ruta', 'ruta_id',
            'estado', 'costo_envio',
            'fecha_registro', 'fecha_entrega_est', 'fecha_entrega_real',
            'esta_entregada', 'tiene_retraso', 'dias_en_transito',
            'historial', 'observaciones',
        ]

    def get_historial(self, obj):
        """Devuelve los últimos 5 cambios de estado"""
        return HistorialEstadoSerializer(
            obj.historial.all()[:5], many=True
        ).data
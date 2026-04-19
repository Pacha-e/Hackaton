"""
REST API serializers for the PQRSD MVP.
Exposes all data needed by the React frontend.
"""
from rest_framework import serializers
from django.contrib.auth.models import User

from apps.pqrsd.models import PQRSD
from apps.conocimiento.models import Dependencia, PrecedenteRespuesta
from apps.clasificacion.models import ClasificacionIA
from apps.sintesis.models import SintesisPQRSD


class DependenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependencia
        fields = ['id', 'nombre', 'sigla', 'descripcion', 'competencias',
                  'email_contacto', 'telefono', 'activa']


class PrecedenteSerializer(serializers.ModelSerializer):
    dependencia_sigla = serializers.CharField(source='dependencia.sigla', read_only=True)

    class Meta:
        model = PrecedenteRespuesta
        fields = ['id', 'dependencia', 'dependencia_sigla', 'tipo_pqrsd',
                  'pregunta_frecuente', 'respuesta_base', 'normativa_aplicable',
                  'usado_veces', 'activo']


class ClasificacionIASerializer(serializers.ModelSerializer):
    validado_por_nombre = serializers.SerializerMethodField()

    def get_validado_por_nombre(self, obj):
        if obj.validado_por:
            return obj.validado_por.get_full_name() or obj.validado_por.username
        return None

    class Meta:
        model = ClasificacionIA
        fields = [
            'id', 'tipo_sugerido', 'prioridad_sugerida', 'razon_clasificacion',
            'confianza', 'modelo_usado', 'fecha_clasificacion',
            'validado_por', 'validado_por_nombre', 'fecha_validacion',
            'aceptada', 'comentario_validacion', 'dependencias_sugeridas',
        ]


class SintesisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SintesisPQRSD
        fields = [
            'id', 'resumen_ejecutivo', 'problema_central', 'accion_requerida',
            'datos_contextuales', 'entidades_mencionadas',
            'normativa_aplicable', 'recomendacion_respuesta', 'fecha_generacion',
            'generado_por_ia',
        ]


class PQRSDListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    dependencia_asignada_nombre = serializers.CharField(
        source='dependencia_asignada.sigla', read_only=True
    )
    dias_restantes = serializers.SerializerMethodField()
    en_alerta = serializers.SerializerMethodField()
    vencida = serializers.SerializerMethodField()
    canal_label = serializers.SerializerMethodField()
    tipo_label = serializers.SerializerMethodField()
    estado_label = serializers.SerializerMethodField()
    prioridad_label = serializers.SerializerMethodField()

    def get_dias_restantes(self, obj):
        return obj.dias_restantes()

    def get_en_alerta(self, obj):
        return obj.en_alerta()

    def get_vencida(self, obj):
        return obj.vencida()

    def get_canal_label(self, obj):
        return obj.get_canal_entrada_display()

    def get_tipo_label(self, obj):
        return obj.get_tipo_display()

    def get_estado_label(self, obj):
        return obj.get_estado_display()

    def get_prioridad_label(self, obj):
        return obj.get_prioridad_display()

    class Meta:
        model = PQRSD
        fields = [
            'id', 'radicado', 'tipo', 'tipo_label', 'estado', 'estado_label',
            'canal_entrada', 'canal_label', 'prioridad', 'prioridad_label',
            'nombre_ciudadano', 'email_ciudadano', 'asunto',
            'dependencia_asignada', 'dependencia_asignada_nombre',
            'clasificacion_validada', 'fecha_radicacion', 'fecha_limite',
            'comuna', 'barrio', 'anonimo',
            'dias_restantes', 'en_alerta', 'vencida',
        ]


class PQRSDDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views, includes nested objects."""
    dependencia_asignada_info = DependenciaSerializer(source='dependencia_asignada', read_only=True)
    dependencia_sugerida_info = DependenciaSerializer(source='dependencia_sugerida', read_only=True)
    clasificacion_ia = ClasificacionIASerializer(read_only=True)
    sintesis = SintesisSerializer(read_only=True)
    dias_restantes = serializers.SerializerMethodField()
    en_alerta = serializers.SerializerMethodField()
    vencida = serializers.SerializerMethodField()
    canal_label = serializers.SerializerMethodField()
    tipo_label = serializers.SerializerMethodField()
    estado_label = serializers.SerializerMethodField()
    prioridad_label = serializers.SerializerMethodField()
    funcionario_nombre = serializers.SerializerMethodField()

    def get_dias_restantes(self, obj):
        return obj.dias_restantes()

    def get_en_alerta(self, obj):
        return obj.en_alerta()

    def get_vencida(self, obj):
        return obj.vencida()

    def get_canal_label(self, obj):
        return obj.get_canal_entrada_display()

    def get_tipo_label(self, obj):
        return obj.get_tipo_display()

    def get_estado_label(self, obj):
        return obj.get_estado_display()

    def get_prioridad_label(self, obj):
        return obj.get_prioridad_display()

    def get_funcionario_nombre(self, obj):
        if obj.funcionario_asignado:
            return obj.funcionario_asignado.get_full_name() or obj.funcionario_asignado.username
        return None

    class Meta:
        model = PQRSD
        fields = [
            'id', 'radicado', 'tipo', 'tipo_label', 'estado', 'estado_label',
            'canal_entrada', 'canal_label', 'prioridad', 'prioridad_label',
            'anonimo', 'nombre_ciudadano', 'email_ciudadano',
            'telefono_ciudadano', 'documento_ciudadano', 'comuna', 'barrio',
            'asunto', 'descripcion', 'archivo_adjunto',
            'dependencia_asignada', 'dependencia_asignada_info',
            'dependencia_sugerida', 'dependencia_sugerida_info',
            'confianza_clasificacion', 'clasificacion_validada',
            'funcionario_asignado', 'funcionario_nombre',
            'fecha_radicacion', 'fecha_limite', 'fecha_respuesta',
            'observaciones_funcionario', 'observaciones_internas', 'omnicanal_meta',
            'clasificacion_ia', 'sintesis',
            'dias_restantes', 'en_alerta', 'vencida',
        ]


class PQRSDCreateSerializer(serializers.ModelSerializer):
    """Serializer for citizen PQRSD submission."""
    class Meta:
        model = PQRSD
        fields = [
            'tipo', 'canal_entrada', 'anonimo',
            'nombre_ciudadano', 'email_ciudadano', 'telefono_ciudadano',
            'documento_ciudadano', 'comuna', 'barrio',
            'asunto', 'descripcion', 'archivo_adjunto',
        ]

    def validate(self, data):
        if not data.get('anonimo') and not data.get('nombre_ciudadano'):
            raise serializers.ValidationError(
                {'nombre_ciudadano': 'Este campo es obligatorio si no es anónimo.'}
            )
        return data

    def create(self, validated_data):
        pqrsd = PQRSD.objects.create(**validated_data)
        return pqrsd


class PQRSDStatusSerializer(serializers.ModelSerializer):
    """Public serializer for citizens checking their PQRSD status."""
    dias_restantes = serializers.SerializerMethodField()
    en_alerta = serializers.SerializerMethodField()
    vencida = serializers.SerializerMethodField()
    estado_label = serializers.SerializerMethodField()
    tipo_label = serializers.SerializerMethodField()
    dependencia_nombre = serializers.CharField(
        source='dependencia_asignada.nombre', read_only=True
    )

    def get_dias_restantes(self, obj):
        return obj.dias_restantes()

    def get_en_alerta(self, obj):
        return obj.en_alerta()

    def get_vencida(self, obj):
        return obj.vencida()

    def get_estado_label(self, obj):
        return obj.get_estado_display()

    def get_tipo_label(self, obj):
        return obj.get_tipo_display()

    class Meta:
        model = PQRSD
        fields = [
            'radicado', 'tipo', 'tipo_label', 'estado', 'estado_label',
            'asunto', 'fecha_radicacion', 'fecha_limite', 'fecha_respuesta',
            'dependencia_nombre', 'clasificacion_validada',
            'dias_restantes', 'en_alerta', 'vencida',
        ]


class StatsSerializer(serializers.Serializer):
    """Dashboard statistics."""
    total = serializers.IntegerField()
    radicadas = serializers.IntegerField()
    en_clasificacion = serializers.IntegerField()
    clasificadas = serializers.IntegerField()
    en_tramite = serializers.IntegerField()
    respondidas = serializers.IntegerField()
    cerradas = serializers.IntegerField()
    sin_clasificar = serializers.IntegerField()
    alertas = serializers.IntegerField()
    vencidas = serializers.IntegerField()
    por_canal = serializers.DictField()
    por_tipo = serializers.DictField()


class InboxMessageSerializer(serializers.Serializer):
    """Multichannel inbox item (wraps a PQRSD with channel-specific display)."""
    id = serializers.IntegerField()
    radicado = serializers.CharField()
    canal = serializers.CharField()
    canal_label = serializers.CharField()
    remitente = serializers.CharField()
    asunto = serializers.CharField()
    preview = serializers.CharField()
    timestamp = serializers.DateTimeField()
    estado = serializers.CharField()
    prioridad = serializers.CharField()
    leido = serializers.BooleanField()
    clasificacion_validada = serializers.BooleanField()
    dias_restantes = serializers.IntegerField(allow_null=True)
    en_alerta = serializers.BooleanField()
    vencida = serializers.BooleanField()

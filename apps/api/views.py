"""
REST API views for the PQRSD MVP React frontend.
All endpoints under /api/v1/
"""
import json
import logging
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.pqrsd.models import PQRSD
from apps.conocimiento.models import Dependencia, PrecedenteRespuesta, SyncLog
from apps.clasificacion.models import ClasificacionIA
from apps.clasificacion.services import clasificar_y_persistir
from apps.sintesis.models import SintesisPQRSD

from .serializers import (
    PQRSDListSerializer, PQRSDDetailSerializer, PQRSDCreateSerializer,
    PQRSDStatusSerializer, DependenciaSerializer, PrecedenteSerializer,
    ClasificacionIASerializer, SintesisSerializer, StatsSerializer,
    InboxMessageSerializer,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# API root (evita 404 en GET /api/v1/)
# ---------------------------------------------------------------------------

@api_view(['GET', 'HEAD'])
@permission_classes([AllowAny])
def api_root(request):
    """Índice mínimo de la API para comprobaciones y desarrollo."""
    rel = request.path
    if not rel.endswith('/'):
        rel = rel + '/'
    routes = {
        'auth_csrf': 'auth/csrf/',
        'auth_login': 'auth/login/',
        'auth_logout': 'auth/logout/',
        'auth_me': 'auth/me/',
        'pqrsd_submit': 'pqrsd/submit/',
        'pqrsd_status': 'pqrsd/status/<radicado>/',
        'dependencias': 'dependencias/',
        'choices': 'choices/',
        'pqrsd_list': 'pqrsd/',
        'pqrsd_detail': 'pqrsd/<id>/',
        'stats': 'stats/',
        'inbox': 'inbox/',
    }
    return Response({
        'service': 'PQRSD Medellín API',
        'version': 1,
        'prefix': rel,
        'routes': routes,
    })


# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf_token(request):
    """Return CSRF token so the React SPA can POST safely."""
    return Response({'csrfToken': get_token(request)})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return Response({
            'id': user.id,
            'username': user.username,
            'fullName': user.get_full_name() or user.username,
            'isStaff': user.is_staff or user.is_superuser,
        })
    return Response({'error': 'Credenciales incorrectas'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def api_logout(request):
    logout(request)
    return Response({'ok': True})


@api_view(['GET'])
@permission_classes([AllowAny])
def me(request):
    if not request.user.is_authenticated:
        return Response({'authenticated': False})
    return Response({
        'authenticated': True,
        'id': request.user.id,
        'username': request.user.username,
        'fullName': request.user.get_full_name() or request.user.username,
        'isStaff': request.user.is_staff or request.user.is_superuser,
    })


# ---------------------------------------------------------------------------
# PUBLIC — CITIZEN
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def pqrsd_create(request):
    """Citizens submit a new PQRSD."""
    serializer = PQRSDCreateSerializer(data=request.data)
    if serializer.is_valid():
        pqrsd = serializer.save()
        return Response({
            'radicado': pqrsd.radicado,
            'id': pqrsd.id,
            'fecha_radicacion': pqrsd.fecha_radicacion,
            'fecha_limite': pqrsd.fecha_limite,
            'estado': pqrsd.estado,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def pqrsd_status(request, radicado):
    """Public status check by radicado number."""
    try:
        pqrsd = PQRSD.objects.select_related('dependencia_asignada').get(radicado=radicado)
    except PQRSD.DoesNotExist:
        return Response({'error': 'Radicado no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = PQRSDStatusSerializer(pqrsd)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def dependencias_list(request):
    """Public list of active departments."""
    deps = Dependencia.objects.filter(activa=True).order_by('nombre')
    serializer = DependenciaSerializer(deps, many=True)
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# STAFF — PQRSD LIST + FILTERS
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pqrsd_list(request):
    """Staff PQRSD list with filters."""
    qs = PQRSD.objects.select_related(
        'dependencia_asignada', 'dependencia_sugerida', 'funcionario_asignado'
    )

    # Filters
    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    canal = request.GET.get('canal', '')
    dep_id = request.GET.get('dependencia', '')
    prioridad = request.GET.get('prioridad', '')
    solo_alertas = request.GET.get('alertas') == '1'
    q = request.GET.get('q', '')
    sin_clasificar = request.GET.get('sin_clasificar') == '1'

    if estado:
        qs = qs.filter(estado=estado)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if canal:
        qs = qs.filter(canal_entrada=canal)
    if dep_id:
        qs = qs.filter(dependencia_asignada_id=dep_id)
    if prioridad:
        qs = qs.filter(prioridad=prioridad)
    if q:
        qs = qs.filter(
            Q(radicado__icontains=q) |
            Q(asunto__icontains=q) |
            Q(nombre_ciudadano__icontains=q) |
            Q(descripcion__icontains=q)
        )
    if sin_clasificar:
        qs = qs.filter(clasificacion_validada=False, estado__in=['radicada', 'en_clasificacion'])

    hoy = date.today()
    if solo_alertas:
        alerta_fecha = hoy + timedelta(days=3)
        qs = qs.filter(
            Q(fecha_limite__lte=alerta_fecha, fecha_limite__gte=hoy) |
            Q(fecha_limite__lt=hoy),
            estado__in=['radicada', 'en_clasificacion', 'clasificada', 'en_tramite']
        )

    serializer = PQRSDListSerializer(qs, many=True)
    return Response({
        'count': qs.count(),
        'results': serializer.data,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pqrsd_detail(request, pk):
    """Full PQRSD detail for staff."""
    try:
        pqrsd = PQRSD.objects.select_related(
            'dependencia_asignada', 'dependencia_sugerida',
            'funcionario_asignado', 'validado_por'
        ).prefetch_related(
            'clasificacion_ia', 'sintesis'
        ).get(pk=pk)
    except PQRSD.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = PQRSDDetailSerializer(pqrsd)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def pqrsd_update_estado(request, pk):
    """Staff changes PQRSD state."""
    try:
        pqrsd = PQRSD.objects.get(pk=pk)
    except PQRSD.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    nuevo_estado = request.data.get('estado')
    estados_validos = [e[0] for e in PQRSD.ESTADO_CHOICES]
    if nuevo_estado not in estados_validos:
        return Response({'error': 'Estado no válido'}, status=status.HTTP_400_BAD_REQUEST)

    if nuevo_estado == 'respondida':
        pqrsd.fecha_respuesta = timezone.now()

    pqrsd.estado = nuevo_estado
    obs = request.data.get('observaciones', '')
    if obs:
        pqrsd.observaciones_funcionario = obs

    dep_id = request.data.get('dependencia_asignada')
    if dep_id:
        try:
            pqrsd.dependencia_asignada_id = int(dep_id)
        except (ValueError, TypeError):
            pass

    pqrsd.save()
    return Response({'ok': True, 'estado': pqrsd.estado, 'estado_label': pqrsd.get_estado_display()})


# ---------------------------------------------------------------------------
# STAFF — CLASSIFICATION
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pqrsd_classify(request, pk):
    """Trigger AI classification for a PQRSD."""
    try:
        pqrsd = PQRSD.objects.get(pk=pk)
    except PQRSD.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    try:
        c = pqrsd.clasificacion_ia
        if c.aceptada is not None:
            serializer = ClasificacionIASerializer(c)
            return Response({'already_classified': True, 'clasificacion': serializer.data})
    except ClasificacionIA.DoesNotExist:
        pass

    try:
        clasificacion, resultado, dep = clasificar_y_persistir(pqrsd)
        serializer = ClasificacionIASerializer(clasificacion)
        dep_data = DependenciaSerializer(dep).data if dep else None
        return Response({
            'clasificacion': serializer.data,
            'dependencia_sugerida': dep_data,
        })
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pqrsd_validate_classification(request, pk):
    """Staff validates AI classification."""
    try:
        pqrsd = PQRSD.objects.get(pk=pk)
        clasificacion = pqrsd.clasificacion_ia
    except (PQRSD.DoesNotExist, ClasificacionIA.DoesNotExist):
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    aceptada = request.data.get('aceptada', True)
    comentario = request.data.get('comentario', '')
    dep_id = request.data.get('dependencia_id')

    clasificacion.aceptada = aceptada
    clasificacion.comentario_validacion = comentario
    clasificacion.validado_por = request.user
    clasificacion.fecha_validacion = timezone.now()
    clasificacion.save()

    if dep_id:
        try:
            dep = Dependencia.objects.get(pk=dep_id)
            pqrsd.dependencia_asignada = dep
        except Dependencia.DoesNotExist:
            pass
    elif aceptada and pqrsd.dependencia_sugerida:
        pqrsd.dependencia_asignada = pqrsd.dependencia_sugerida

    pqrsd.clasificacion_validada = True
    pqrsd.validado_por = request.user
    pqrsd.estado = 'clasificada'
    pqrsd.save()

    return Response({'ok': True, 'estado': pqrsd.estado})


# ---------------------------------------------------------------------------
# STAFF — SYNTHESIS
# ---------------------------------------------------------------------------

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def pqrsd_synthesis(request, pk):
    """Get or generate synthesis for a PQRSD."""
    try:
        pqrsd = PQRSD.objects.select_related('dependencia_asignada').get(pk=pk)
    except PQRSD.DoesNotExist:
        return Response({'error': 'No encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        try:
            sintesis = pqrsd.sintesis
            return Response(SintesisSerializer(sintesis).data)
        except SintesisPQRSD.DoesNotExist:
            return Response({'exists': False})

    # POST — generate
    try:
        from apps.sintesis.gemini_sintesis import generar_sintesis
        from apps.conocimiento.models import PrecedenteRespuesta
        resultado = generar_sintesis(pqrsd)
        sintesis, _ = SintesisPQRSD.objects.get_or_create(pqrsd=pqrsd)
        for k, v in resultado.items():
            setattr(sintesis, k, v)
        sintesis.save()
        if pqrsd.dependencia_asignada:
            precedentes = PrecedenteRespuesta.objects.filter(
                dependencia=pqrsd.dependencia_asignada,
                tipo_pqrsd=pqrsd.tipo,
                activo=True
            )[:3]
            sintesis.precedentes_similares.set(precedentes)
        return Response(SintesisSerializer(sintesis).data)
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------------------
# STAFF — DASHBOARD STATS
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stats(request):
    """Aggregated statistics for the dashboard."""
    hoy = date.today()
    alerta_fecha = hoy + timedelta(days=3)

    total_qs = PQRSD.objects.all()

    # State counts
    state_counts = {
        s[0]: total_qs.filter(estado=s[0]).count()
        for s in PQRSD.ESTADO_CHOICES
    }

    # Channel counts
    canal_counts = {}
    for row in total_qs.values('canal_entrada').annotate(n=Count('id')):
        canal_counts[row['canal_entrada']] = row['n']

    # Type counts
    tipo_counts = {}
    for row in total_qs.values('tipo').annotate(n=Count('id')):
        tipo_counts[row['tipo']] = row['n']

    alertas = total_qs.filter(
        fecha_limite__lte=alerta_fecha,
        fecha_limite__gte=hoy,
        estado__in=['radicada', 'en_clasificacion', 'clasificada', 'en_tramite']
    ).count()

    vencidas = total_qs.filter(
        fecha_limite__lt=hoy,
        estado__in=['radicada', 'en_clasificacion', 'clasificada', 'en_tramite']
    ).count()

    sin_clasificar = total_qs.filter(
        clasificacion_validada=False,
        estado__in=['radicada', 'en_clasificacion']
    ).count()

    data = {
        'total': total_qs.count(),
        'radicadas': state_counts.get('radicada', 0),
        'en_clasificacion': state_counts.get('en_clasificacion', 0),
        'clasificadas': state_counts.get('clasificada', 0),
        'en_tramite': state_counts.get('en_tramite', 0),
        'respondidas': state_counts.get('respondida', 0),
        'cerradas': state_counts.get('cerrada', 0),
        'sin_clasificar': sin_clasificar,
        'alertas': alertas,
        'vencidas': vencidas,
        'por_canal': canal_counts,
        'por_tipo': tipo_counts,
    }

    serializer = StatsSerializer(data)
    return Response(serializer.data)


# ---------------------------------------------------------------------------
# STAFF — INBOX (multichannel view)
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inbox(request):
    """
    Unified multichannel inbox.
    Returns PQRSD list formatted as inbox messages grouped by channel.
    """
    qs = PQRSD.objects.select_related('dependencia_asignada').order_by('-fecha_radicacion')

    canal = request.GET.get('canal', '')
    if canal:
        qs = qs.filter(canal_entrada=canal)

    # Unread = radicada or en_clasificacion
    solo_no_leidos = request.GET.get('no_leidos') == '1'
    if solo_no_leidos:
        qs = qs.filter(estado__in=['radicada', 'en_clasificacion'])

    limit = int(request.GET.get('limit', 50))
    qs = qs[:limit]

    canal_labels = dict(PQRSD.CANAL_CHOICES)

    messages_data = []
    for p in qs:
        leido = p.estado not in ('radicada', 'en_clasificacion')
        remitente = p.nombre_ciudadano if p.nombre_ciudadano else 'Ciudadano Anónimo'
        if p.canal_entrada == 'whatsapp' and p.telefono_ciudadano:
            remitente = f"{remitente} ({p.telefono_ciudadano})"
        elif p.canal_entrada == 'email' and p.email_ciudadano:
            remitente = f"{remitente} <{p.email_ciudadano}>"
        elif p.canal_entrada == 'instagram':
            remitente = f"@{p.nombre_ciudadano.lower().replace(' ', '_')}" if p.nombre_ciudadano else '@usuario'

        messages_data.append({
            'id': p.id,
            'radicado': p.radicado,
            'canal': p.canal_entrada,
            'canal_label': canal_labels.get(p.canal_entrada, p.canal_entrada),
            'remitente': remitente,
            'asunto': p.asunto,
            'preview': p.descripcion[:120] + ('...' if len(p.descripcion) > 120 else ''),
            'timestamp': p.fecha_radicacion,
            'estado': p.estado,
            'prioridad': p.prioridad,
            'leido': leido,
            'clasificacion_validada': p.clasificacion_validada,
            'dias_restantes': p.dias_restantes(),
            'en_alerta': p.en_alerta(),
            'vencida': p.vencida(),
        })

    return Response({
        'count': len(messages_data),
        'results': messages_data,
    })


# ---------------------------------------------------------------------------
# DEMO — multichannel simulation
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def demo_inject(request):
    """
    Demo/simulation endpoint.
    Injects a realistic fake PQRSD from a specific channel.
    Used to demonstrate multichannel intake during the pitch.
    """
    canal = request.data.get('canal', 'whatsapp')
    scenario = request.data.get('scenario', 'default')

    scenarios = {
        'whatsapp': {
            'tipo': 'queja',
            'canal_entrada': 'whatsapp',
            'nombre_ciudadano': 'Carlos Andrés Mejía',
            'telefono_ciudadano': '+57 300 123 4567',
            'email_ciudadano': 'carlos.mejia@gmail.com',
            'comuna': 'Laureles - Estadio',
            'barrio': 'Laureles',
            'asunto': 'Huecos en la vía principal del barrio Laureles',
            'descripcion': (
                'Hola, quiero reportar que hay varios huecos muy peligrosos en la '
                'Carrera 76 con Calle 33 en el barrio Laureles. Uno de estos huecos '
                'dañó la llanta de mi moto ayer en la noche. Hay carros que pasan '
                'casi volcándose. Ya van más de 3 meses con ese problema y nadie hace nada. '
                'Por favor ayúdenme con eso. Gracias.'
            ),
            'prioridad': 'alta',
            'anonimo': False,
        },
        'email': {
            'tipo': 'peticion',
            'canal_entrada': 'email',
            'nombre_ciudadano': 'María Fernanda López Restrepo',
            'email_ciudadano': 'mflopez@empresa.com.co',
            'telefono_ciudadano': '+57 604 555 0123',
            'comuna': 'El Poblado',
            'barrio': 'Manila',
            'asunto': 'Solicitud información proceso licitación pública obra vial',
            'descripcion': (
                'Estimados señores de la Alcaldía de Medellín,\n\n'
                'Por medio de la presente me permito solicitar información detallada '
                'sobre el proceso licitatorio número LIC-2026-004 para la construcción '
                'de la ciclovía en el sector de El Poblado. Específicamente requiero:\n'
                '1. Pliego de condiciones completo\n'
                '2. Cronograma del proceso\n'
                '3. Requisitos técnicos y financieros\n\n'
                'Quedo atenta a su respuesta.\n\n'
                'Cordialmente,\nMaría Fernanda López'
            ),
            'prioridad': 'media',
            'anonimo': False,
        },
        'instagram': {
            'tipo': 'queja',
            'canal_entrada': 'instagram',
            'nombre_ciudadano': 'Juan David Ospina',
            'email_ciudadano': '',
            'telefono_ciudadano': '',
            'comuna': 'Aranjuez',
            'barrio': 'San Isidro',
            'asunto': 'Queja por falta de alumbrado público en Aranjuez',
            'descripcion': (
                '@AlcaldíaMedellín hace 2 semanas que se dañó el alumbrado en toda '
                'la Cra 45 entre calles 78 y 82 en Aranjuez. Es muy peligroso en las '
                'noches, ya hubo un robo esta semana. Los vecinos estamos muy preocupados '
                '#Medellín #Aranjuez #Seguridad porfavor atiendan esto 🙏'
            ),
            'prioridad': 'alta',
            'anonimo': False,
        },
        'presencial': {
            'tipo': 'reclamo',
            'canal_entrada': 'presencial',
            'nombre_ciudadano': 'Rosa Elena Cardona Ríos',
            'documento_ciudadano': '43.567.890',
            'email_ciudadano': '',
            'telefono_ciudadano': '+57 301 987 6543',
            'comuna': 'Robledo',
            'barrio': 'Robledo',
            'asunto': 'Reclamo por cobro indebido en servicio de acueducto',
            'descripcion': (
                'La ciudadana Rosa Elena Cardona Ríos se presentó en persona a las '
                'instalaciones de la Alcaldía de Medellín. Manifiesta que EPM le cobró '
                'en la factura de octubre 2025 un valor de $450.000 pesos por consumo '
                'de agua que ella considera excesivo e injustificado, ya que vive sola '
                'y sus consumos históricos son de $85.000 mensuales. Solicita revisión '
                'del medidor y ajuste de la factura. Adjunta facturas de los últimos '
                '6 meses como soporte.'
            ),
            'prioridad': 'media',
            'anonimo': False,
        },
        'default': {
            'tipo': 'sugerencia',
            'canal_entrada': canal,
            'nombre_ciudadano': 'Ciudadano Demo',
            'email_ciudadano': 'demo@ciudadano.com',
            'comuna': 'Centro',
            'barrio': 'La Candelaria',
            'asunto': 'Sugerencia de prueba desde canal ' + canal,
            'descripcion': 'Esta es una sugerencia de prueba inyectada para demostrar el sistema multicanal.',
            'prioridad': 'baja',
            'anonimo': False,
        }
    }

    data = scenarios.get(scenario, scenarios.get(canal, scenarios['default']))
    data['canal_entrada'] = canal

    serializer = PQRSDCreateSerializer(data=data)
    if serializer.is_valid():
        pqrsd = serializer.save()
        return Response({
            'ok': True,
            'radicado': pqrsd.radicado,
            'id': pqrsd.id,
            'canal': canal,
            'message': f'PQRSD simulada desde {canal} creada exitosamente.',
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# CHOICES (for frontend dropdowns)
# ---------------------------------------------------------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def choices(request):
    """Return all choice lists for dropdowns."""
    return Response({
        'tipo': [{'value': k, 'label': v} for k, v in PQRSD.TIPO_CHOICES],
        'estado': [{'value': k, 'label': v} for k, v in PQRSD.ESTADO_CHOICES],
        'canal': [{'value': k, 'label': v} for k, v in PQRSD.CANAL_CHOICES],
        'prioridad': [{'value': k, 'label': v} for k, v in PQRSD.PRIORIDAD_CHOICES],
    })


# ---------------------------------------------------------------------------
# AGENTES IA — Pipeline completo
# ---------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pqrsd_run_pipeline(request, pk):
    """
    Ejecuta el pipeline completo de agentes IA sobre una PQRSD existente.
    Staff-only. Responde con el PipelineContext final.
    """
    try:
        pqrsd = PQRSD.objects.get(pk=pk)
    except PQRSD.DoesNotExist:
        return Response({'error': 'PQRSD no encontrada'}, status=status.HTTP_404_NOT_FOUND)

    if not getattr(settings, 'ANTHROPIC_API_KEY', ''):
        return Response(
            {'error': 'ANTHROPIC_API_KEY no configurada. Pipeline IA no disponible.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        from apps.agentes.orchestrator import procesar_pqrsd
        from dataclasses import asdict

        ctx = procesar_pqrsd(
            canal=pqrsd.canal_entrada,
            descripcion=pqrsd.descripcion,
            pqrsd_id=pqrsd.pk,
            radicado=pqrsd.radicado,
            nombre=pqrsd.nombre_ciudadano,
            email=pqrsd.email_ciudadano,
            telefono=pqrsd.telefono_ciudadano,
            documento=pqrsd.documento_ciudadano,
            anonimo=pqrsd.anonimo,
            barrio=pqrsd.barrio or '',
            comuna=pqrsd.comuna or '',
        )

        return Response({
            'ok': True,
            'radicado': ctx.radicado,
            'admisible': ctx.admisible,
            'motivo_rechazo': ctx.motivo_rechazo,
            'secretaria_asignada': ctx.secretaria_asignada,
            'confianza': ctx.confianza_clasificacion,
            'requiere_revision_humana': ctx.requiere_revision_humana,
            'dividida': ctx.dividida,
            'sub_pqrsds': ctx.sub_pqrsds,
            'respuesta_generada': ctx.respuesta_generada,
            'respuesta_texto': ctx.respuesta_texto,
            'entregada': ctx.entregada,
            'canal_exitoso': ctx.canal_exitoso,
            'fecha_limite': ctx.fecha_limite,
            'dias_restantes': ctx.dias_restantes,
            'estado_sla': ctx.estado_sla,
            'pii_detectada': ctx.pii_detectada,
            'agentes_ejecutados': ctx.agentes_ejecutados,
            'errores': ctx.errores,
        })
    except Exception as e:
        logger.exception(f'[pqrsd_run_pipeline] Error procesando PQRSD {pk}')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def pqrsd_submit_pipeline(request):
    """
    Crea y procesa una PQRSD en un solo paso (pipeline completo).
    Canal ciudadano — no requiere autenticación.
    """
    if not getattr(settings, 'ANTHROPIC_API_KEY', ''):
        # Fallback al submit estándar sin IA
        return pqrsd_create(request)

    required = ['descripcion_raw', 'canal']
    for f in required:
        if not request.data.get(f):
            return Response({'error': f'Campo requerido: {f}'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        from apps.agentes.orchestrator import procesar_pqrsd

        ctx = procesar_pqrsd(
            canal=request.data.get('canal', 'web'),
            descripcion=request.data.get('descripcion_raw', ''),
            nombre=request.data.get('nombre', ''),
            email=request.data.get('email', ''),
            telefono=request.data.get('telefono', ''),
            documento=request.data.get('documento', ''),
            anonimo=request.data.get('anonimo', False),
            barrio=request.data.get('barrio', ''),
            comuna=request.data.get('comuna', ''),
        )

        if not ctx.admisible:
            return Response({
                'admisible': False,
                'motivo': ctx.motivo_rechazo,
                'mensaje': ctx.notificacion_ciudadano,
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response({
            'ok': True,
            'radicado': ctx.radicado,
            'admisible': True,
            'secretaria_asignada': ctx.secretaria_asignada,
            'fecha_limite': ctx.fecha_limite,
            'respuesta': ctx.respuesta_texto,
            'dividida': ctx.dividida,
            'sub_radicados': [s['radicado'] for s in ctx.sub_pqrsds],
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.exception('[pqrsd_submit_pipeline] Error')
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------------------
# STAFF — SYNC MEDATA
# ---------------------------------------------------------------------------

@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def sync_medata(request):
    """
    Triggers sync_medata management command inline (no Celery needed).
    GET → returns last sync log entry.
    POST → runs sync and returns result.
    """
    if not request.user.is_staff:
        return Response({'error': 'Solo staff puede ejecutar sincronizaciones.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        last = SyncLog.objects.filter(fuente='medata').first()
        if not last:
            return Response({'last_sync': None})
        return Response({
            'last_sync': {
                'ejecutado_en': last.ejecutado_en,
                'registros_importados': last.registros_importados,
                'exitoso': last.exitoso,
                'error_msg': last.error_msg,
            }
        })

    limit = int(request.data.get('limit', 500))
    from django.core.management import call_command
    import io as _io
    out = _io.StringIO()
    err = _io.StringIO()
    try:
        call_command('sync_medata', limit=limit, stdout=out, stderr=err)
        log = SyncLog.objects.filter(fuente='medata').first()
        return Response({
            'ok': True,
            'registros_importados': log.registros_importados if log else 0,
            'output': out.getvalue(),
        })
    except Exception as exc:
        return Response({'ok': False, 'error': str(exc), 'output': out.getvalue()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



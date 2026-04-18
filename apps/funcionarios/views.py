from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from apps.pqrsd.models import PQRSD
from apps.conocimiento.models import Dependencia


@login_required
def dashboard(request):
    pqrsds = PQRSD.objects.select_related('dependencia_asignada', 'funcionario_asignado')

    # Filtros
    estado = request.GET.get('estado', '')
    tipo = request.GET.get('tipo', '')
    dep_id = request.GET.get('dependencia', '')
    solo_alertas = request.GET.get('alertas', '') == '1'
    q = request.GET.get('q', '')

    if estado:
        pqrsds = pqrsds.filter(estado=estado)
    if tipo:
        pqrsds = pqrsds.filter(tipo=tipo)
    if dep_id:
        pqrsds = pqrsds.filter(dependencia_asignada_id=dep_id)
    if q:
        pqrsds = pqrsds.filter(Q(radicado__icontains=q) | Q(asunto__icontains=q) | Q(nombre_ciudadano__icontains=q))

    # Estadísticas
    stats = {
        'total': PQRSD.objects.count(),
        'radicadas': PQRSD.objects.filter(estado='radicada').count(),
        'en_tramite': PQRSD.objects.filter(estado='en_tramite').count(),
        'respondidas': PQRSD.objects.filter(estado='respondida').count(),
        'sin_clasificar': PQRSD.objects.filter(clasificacion_validada=False, estado__in=['radicada', 'en_clasificacion']).count(),
    }

    from datetime import date, timedelta
    hoy = date.today()
    alerta_fecha = hoy + timedelta(days=3)
    alertas = PQRSD.objects.filter(
        fecha_limite__lte=alerta_fecha,
        fecha_limite__gte=hoy,
        estado__in=['radicada', 'en_clasificacion', 'clasificada', 'en_tramite']
    )
    vencidas = PQRSD.objects.filter(fecha_limite__lt=hoy, estado__in=['radicada', 'en_clasificacion', 'clasificada', 'en_tramite'])
    stats['alertas'] = alertas.count()
    stats['vencidas'] = vencidas.count()

    if solo_alertas:
        pqrsds = alertas | vencidas

    dependencias = Dependencia.objects.filter(activa=True)
    return render(request, 'funcionarios/dashboard.html', {
        'pqrsds': pqrsds,
        'stats': stats,
        'dependencias': dependencias,
        'filtros': {'estado': estado, 'tipo': tipo, 'dep_id': dep_id, 'q': q, 'alertas': solo_alertas},
        'estado_choices': PQRSD.ESTADO_CHOICES,
        'tipo_choices': PQRSD.TIPO_CHOICES,
    })


@login_required
def detalle_pqrsd(request, pk):
    pqrsd = get_object_or_404(
        PQRSD.objects.select_related('dependencia_asignada', 'dependencia_sugerida', 'funcionario_asignado', 'validado_por'),
        pk=pk
    )
    return render(request, 'funcionarios/detalle_pqrsd.html', {'pqrsd': pqrsd})


@login_required
def cambiar_estado(request, pk):
    if request.method != 'POST':
        return redirect('funcionarios:detalle_pqrsd', pk=pk)

    pqrsd = get_object_or_404(PQRSD, pk=pk)
    nuevo_estado = request.POST.get('estado')
    estados_validos = [e[0] for e in PQRSD.ESTADO_CHOICES]

    if nuevo_estado not in estados_validos:
        messages.error(request, 'Estado no válido.')
        return redirect('funcionarios:detalle_pqrsd', pk=pk)

    if nuevo_estado == 'respondida':
        pqrsd.fecha_respuesta = timezone.now()

    pqrsd.estado = nuevo_estado
    obs = request.POST.get('observaciones', '')
    if obs:
        pqrsd.observaciones_funcionario = obs
    pqrsd.save()
    messages.success(request, f'Estado actualizado a: {pqrsd.get_estado_display()}')
    return redirect('funcionarios:detalle_pqrsd', pk=pk)

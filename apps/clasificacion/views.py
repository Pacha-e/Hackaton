from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from apps.pqrsd.models import PQRSD
from apps.conocimiento.models import Dependencia
from .models import ClasificacionIA
from .gemini_service import clasificar_pqrsd


@login_required
def clasificar(request, pqrsd_id):
    pqrsd = get_object_or_404(PQRSD, pk=pqrsd_id)

    if hasattr(pqrsd, 'clasificacion_ia'):
        clasificacion = pqrsd.clasificacion_ia
    else:
        resultado = clasificar_pqrsd(pqrsd)
        dep_sugerida = None
        if resultado and resultado.get('dependencia_id'):
            try:
                dep_sugerida = Dependencia.objects.get(pk=resultado['dependencia_id'])
            except Dependencia.DoesNotExist:
                pass

        clasificacion = ClasificacionIA.objects.create(
            pqrsd=pqrsd,
            prompt_enviado=resultado.get('prompt', ''),
            respuesta_cruda=resultado.get('respuesta_cruda', ''),
            tipo_sugerido=resultado.get('tipo_sugerido', ''),
            prioridad_sugerida=resultado.get('prioridad_sugerida', 'media'),
            razon_clasificacion=resultado.get('razon', ''),
            confianza=resultado.get('confianza'),
            modelo_usado=resultado.get('modelo', 'gemini-1.5-flash'),
            dependencias_sugeridas=[{
                'id': resultado.get('dependencia_id'),
                'nombre': resultado.get('dependencia_nombre'),
                'confianza': resultado.get('confianza'),
                'razon': resultado.get('razon'),
            }],
        )
        pqrsd.dependencia_sugerida = dep_sugerida
        pqrsd.confianza_clasificacion = resultado.get('confianza')
        pqrsd.estado = 'en_clasificacion'
        pqrsd.save()

    dependencias = Dependencia.objects.filter(activa=True)
    return render(request, 'clasificacion/revisar.html', {
        'pqrsd': pqrsd,
        'clasificacion': clasificacion,
        'dependencias': dependencias,
    })


@login_required
def validar_clasificacion(request, pqrsd_id):
    if request.method != 'POST':
        return redirect('clasificacion:clasificar', pqrsd_id=pqrsd_id)

    pqrsd = get_object_or_404(PQRSD, pk=pqrsd_id)
    clasificacion = get_object_or_404(ClasificacionIA, pqrsd=pqrsd)

    dep_id = request.POST.get('dependencia_id')
    aceptada = request.POST.get('aceptada') == 'si'
    comentario = request.POST.get('comentario', '')

    try:
        dep = Dependencia.objects.get(pk=dep_id)
    except Dependencia.DoesNotExist:
        messages.error(request, 'Dependencia no válida.')
        return redirect('clasificacion:clasificar', pqrsd_id=pqrsd_id)

    clasificacion.validado_por = request.user
    clasificacion.fecha_validacion = timezone.now()
    clasificacion.aceptada = aceptada
    clasificacion.comentario_validacion = comentario
    clasificacion.save()

    pqrsd.dependencia_asignada = dep
    pqrsd.clasificacion_validada = True
    pqrsd.validado_por = request.user
    pqrsd.estado = 'clasificada'
    pqrsd.save()

    messages.success(request, f'Clasificación validada. Asignada a: {dep.nombre}')
    return redirect('funcionarios:detalle_pqrsd', pk=pqrsd_id)

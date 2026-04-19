from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from apps.pqrsd.models import PQRSD
from apps.conocimiento.models import Dependencia
from .models import ClasificacionIA
from apps.sintesis.models import SintesisPQRSD
from .langgraph_agent import procesar_pqrsd_con_agente


@login_required
def clasificar(request, pqrsd_id):
    pqrsd = get_object_or_404(PQRSD, pk=pqrsd_id)

    if hasattr(pqrsd, 'clasificacion_ia'):
        clasificacion = pqrsd.clasificacion_ia
    else:
        # 1. Ejecutamos nuestra red de LangGraph Agent
        estado_final = procesar_pqrsd_con_agente(pqrsd)
        
        # 2. Extraemos el bloque de la clasificación
        clasif_data = estado_final.get('clasificacion', {})
        dep_sugerida = None
        if clasif_data and clasif_data.get('dependencia_id'):
            try:
                dep_sugerida = Dependencia.objects.get(pk=clasif_data['dependencia_id'])
            except Dependencia.DoesNotExist:
                pass

        # 3. Guardamos la Clasificación
        clasificacion = ClasificacionIA.objects.create(
            pqrsd=pqrsd,
            prompt_enviado="Orquestado via LangGraph (ver LangSmith para detalles)",
            respuesta_cruda="JSON estructurado",
            tipo_sugerido=clasif_data.get('tipo_sugerido', ''),
            prioridad_sugerida=clasif_data.get('prioridad_sugerida', 'media'),
            razon_clasificacion=clasif_data.get('razon', ''),
            confianza=clasif_data.get('confianza', 0),
            modelo_usado='langgraph-gemini-agent-flash',
            dependencias_sugeridas=[clasif_data] if clasif_data else [],
        )
        
        pqrsd.dependencia_sugerida = dep_sugerida
        pqrsd.confianza_clasificacion = clasif_data.get('confianza', 0)
        pqrsd.estado = 'en_clasificacion'
        pqrsd.save()
        
        # 4. Guardamos también la Síntesis de paso (porque el agente ya la hizo gratis en el segundo nodo)
        sintesis_data = estado_final.get('sintesis', {})
        if sintesis_data and not hasattr(pqrsd, 'sintesis'):
            SintesisPQRSD.objects.create(
                pqrsd=pqrsd,
                resumen_ejecutivo=sintesis_data.get('resumen_ejecutivo', ''),
                problema_central=sintesis_data.get('problema_central', ''),
                accion_requerida=sintesis_data.get('accion_requerida', ''),
                datos_contextuales=sintesis_data.get('datos_contextuales', {}),
                entidades_mencionadas=sintesis_data.get('entidades_mencionadas', []),
                normativa_aplicable=sintesis_data.get('normativa_aplicable', ''),
            )

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

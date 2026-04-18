from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.pqrsd.models import PQRSD
from apps.conocimiento.models import PrecedenteRespuesta
from .models import SintesisPQRSD
from .gemini_sintesis import generar_sintesis


@login_required
def ver_sintesis(request, pqrsd_id):
    pqrsd = get_object_or_404(PQRSD, pk=pqrsd_id)

    if not hasattr(pqrsd, 'sintesis'):
        resultado = generar_sintesis(pqrsd)
        sintesis = SintesisPQRSD.objects.create(
            pqrsd=pqrsd,
            resumen_ejecutivo=resultado.get('resumen_ejecutivo', ''),
            problema_central=resultado.get('problema_central', ''),
            accion_requerida=resultado.get('accion_requerida', ''),
            datos_contextuales=resultado.get('datos_contextuales', {}),
            entidades_mencionadas=resultado.get('entidades_mencionadas', []),
            normativa_aplicable=resultado.get('normativa_aplicable', ''),
            recomendacion_respuesta=resultado.get('recomendacion_respuesta', ''),
        )
        # Vincular precedentes si la dependencia asignada tiene alguno
        if pqrsd.dependencia_asignada:
            precedentes = PrecedenteRespuesta.objects.filter(
                dependencia=pqrsd.dependencia_asignada,
                tipo_pqrsd=pqrsd.tipo,
                activo=True
            )[:3]
            sintesis.precedentes_similares.set(precedentes)
        messages.info(request, 'Síntesis generada automáticamente por IA. Revise antes de usar.')
    else:
        sintesis = pqrsd.sintesis

    return render(request, 'funcionarios/sintesis.html', {'pqrsd': pqrsd, 'sintesis': sintesis})

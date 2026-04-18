from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PQRSD
from .forms import PQRSDCiudadanoForm


def home(request):
    tipos = [
        ('peticion', 'Petición', 'Para solicitar información, copias o actuaciones a la Alcaldía.', 'envelope-open'),
        ('queja', 'Queja', 'Cuando un servidor público ha incurrido en acción u omisión.', 'emoji-frown'),
        ('reclamo', 'Reclamo', 'Para exigir el reconocimiento de un derecho desconocido.', 'exclamation-triangle'),
        ('sugerencia', 'Sugerencia', 'Para proponer mejoras en los servicios o procedimientos.', 'lightbulb'),
        ('denuncia', 'Denuncia', 'Para poner en conocimiento actos irregulares o ilegales.', 'flag'),
        ('correspondencia', 'Correspondencia', 'Para comunicaciones generales no clasificadas anteriormente.', 'envelope'),
    ]
    return render(request, 'pqrsd/home.html', {'tipos': tipos})


def radicar_pqrsd(request):
    if request.method == 'POST':
        form = PQRSDCiudadanoForm(request.POST, request.FILES)
        if form.is_valid():
            pqrsd = form.save(commit=False)
            pqrsd.estado = 'radicada'
            pqrsd.save()
            messages.success(request, f'Su solicitud fue radicada exitosamente con el número: {pqrsd.radicado}')
            return redirect('confirmacion_radicado', radicado=pqrsd.radicado)
    else:
        tipo_inicial = request.GET.get('tipo', '')
        form = PQRSDCiudadanoForm(initial={'tipo': tipo_inicial} if tipo_inicial else None)
    return render(request, 'pqrsd/radicar.html', {'form': form})


def confirmacion_radicado(request, radicado):
    pqrsd = get_object_or_404(PQRSD, radicado=radicado)
    return render(request, 'pqrsd/confirmacion.html', {'pqrsd': pqrsd})


def consultar_estado(request):
    pqrsd = None
    radicado = request.GET.get('radicado', '').strip()
    if radicado:
        try:
            pqrsd = PQRSD.objects.get(radicado=radicado)
        except PQRSD.DoesNotExist:
            messages.error(request, f'No se encontró ninguna solicitud con el radicado "{radicado}".')
    return render(request, 'pqrsd/consultar.html', {'pqrsd': pqrsd, 'radicado': radicado})

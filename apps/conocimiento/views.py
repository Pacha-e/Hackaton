from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Dependencia, PrecedenteRespuesta


@login_required
def lista_dependencias(request):
    dependencias = Dependencia.objects.filter(activa=True)
    q = request.GET.get('q', '')
    if q:
        dependencias = dependencias.filter(nombre__icontains=q) | dependencias.filter(sigla__icontains=q) | dependencias.filter(keywords__icontains=q)
    return render(request, 'conocimiento/lista_dependencias.html', {'dependencias': dependencias, 'q': q})


@login_required
def detalle_dependencia(request, pk):
    dep = get_object_or_404(Dependencia, pk=pk)
    precedentes = dep.precedentes.filter(activo=True)
    return render(request, 'conocimiento/detalle_dependencia.html', {'dep': dep, 'precedentes': precedentes})

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('radicar/', views.radicar_pqrsd, name='radicar_pqrsd'),
    path('confirmacion/<str:radicado>/', views.confirmacion_radicado, name='confirmacion_radicado'),
    path('consultar/', views.consultar_estado, name='consultar_estado'),
]

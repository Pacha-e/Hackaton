from django.urls import path
from . import views

app_name = 'clasificacion'

urlpatterns = [
    path('<int:pqrsd_id>/clasificar/', views.clasificar, name='clasificar'),
    path('<int:pqrsd_id>/validar/', views.validar_clasificacion, name='validar'),
]

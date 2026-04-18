from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_dependencias, name='lista_dependencias'),
    path('<int:pk>/', views.detalle_dependencia, name='detalle_dependencia'),
]

from django.urls import path
from . import views
from apps.sintesis.views import ver_sintesis

app_name = 'funcionarios'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pqrsd/<int:pk>/', views.detalle_pqrsd, name='detalle_pqrsd'),
    path('pqrsd/<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
    path('pqrsd/<int:pqrsd_id>/sintesis/', ver_sintesis, name='ver_sintesis'),
    path('sync-medata/', views.sync_medata_view, name='sync_medata'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/csrf/', views.csrf_token),
    path('auth/login/', views.api_login),
    path('auth/logout/', views.api_logout),
    path('auth/me/', views.me),

    # Public / citizen
    path('pqrsd/submit/', views.pqrsd_create),
    path('pqrsd/status/<str:radicado>/', views.pqrsd_status),
    path('dependencias/', views.dependencias_list),
    path('choices/', views.choices),

    # Staff — PQRSD management
    path('pqrsd/', views.pqrsd_list),
    path('pqrsd/<int:pk>/', views.pqrsd_detail),
    path('pqrsd/<int:pk>/estado/', views.pqrsd_update_estado),

    # Staff — Classification
    path('pqrsd/<int:pk>/classify/', views.pqrsd_classify),
    path('pqrsd/<int:pk>/validate/', views.pqrsd_validate_classification),

    # Staff — Synthesis
    path('pqrsd/<int:pk>/synthesis/', views.pqrsd_synthesis),

    # Dashboard
    path('stats/', views.stats),

    # Inbox
    path('inbox/', views.inbox),

    # Demo simulation
    path('demo/inject/', views.demo_inject),

    # Chatwoot → PQRSD (webhook)
    path('integrations/chatwoot/', views.chatwoot_webhook),
]

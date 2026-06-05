# envios/urls.py
from django.urls import path
from . import views, views_cbv
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Encomiendas - CRUD
    path('encomiendas/', views_cbv.EncomiendaListView.as_view(), name='encomienda_lista'),
    path('encomiendas/nueva/', views_cbv.EncomiendaCreateView.as_view(), name='encomienda_crear'),
    path('encomiendas/<int:pk>/', views_cbv.EncomiendaDetailView.as_view(), name='encomienda_detalle'),
    path('encomiendas/<int:pk>/editar/', views_cbv.EncomiendaUpdateView.as_view(), name='encomienda_editar'),
    path('encomiendas/<int:pk>/estado/', views.encomienda_cambiar_estado, name='encomienda_cambiar_estado'),
    
    # Búsqueda
    path('encomiendas/buscar/<str:codigo>/', views.buscar_por_codigo, name='buscar_por_codigo'),

    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # API
    # path('api/encomiendas/<uuid:uuid>/', views.encomienda_api, name='encomienda_api'),
]
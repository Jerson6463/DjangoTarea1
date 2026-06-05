"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from envios import views_auth
from api.views import EncomiendaTokenView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from drf_spectacular.views import (
    SpectacularAPIView, # endpoint que sirve el schema YAML/JSON
    SpectacularSwaggerView, # interfaz Swagger UI (interactiva)
    SpectacularRedocView, # interfaz ReDoc (solo lectura, más limpia)
)

admin.site.site_header = 'Sistema de Gestion De Encomiendas'
admin.site.site_title = 'Encomiendas Admin'
admin.site.index_title = 'Panel de Administracion'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('envios.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('login/', views_auth.login_view, name='login'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('perfil/', views_auth.perfil_view, name='perfil'),
    path('api/v1/auth/token/', EncomiendaTokenView.as_view()),
]

urlpatterns += [
    # Schema en formato OpenAPI 3.0 (YAML o JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI: interfaz interactiva para probar la API
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger'),
    # ReDoc: documentación de solo lectura más limpia
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += [
    path('api/v1/auth/token/',
         TokenObtainPairView.as_view(), name='token_obtain'),
    path('api/v1/auth/token/refresh/',
         TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/blacklist/',
         TokenBlacklistView.as_view(), name='token_blacklist'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

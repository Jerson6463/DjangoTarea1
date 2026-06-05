from django.urls import path, include
from . import api_views
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from envios.api_views import (
    EncomiendaListCreateView,
    EncomiendaDetailView,
    ClienteListView,
    RutaListView,
)

from envios.viewsets import EncomiendaViewSet

router = DefaultRouter()
router.register('encomiendas', EncomiendaViewSet, basename='encomienda')

urlpatterns = [
    # URLs del router (ViewSets)
    path('', include(router.urls)),
    
    # Endpoints de autenticación JWT
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Documentación interactiva
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(), name='swagger'),
    
]
from django.shortcuts import render

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EncomiendaTokenSerializer

class EncomiendaTokenView(TokenObtainPairView):
    serializer_class = EncomiendaTokenSerializer

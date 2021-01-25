from manager.settings import AUTH_USER_MODEL
from rest_framework import viewsets, permissions
from carbina.models import Client
from .serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated]
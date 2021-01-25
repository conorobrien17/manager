from rest_framework.response import Response
from rest_framework import viewsets, generics
from carbina.models import Client
from .serializers import ClientSerializer
from .paginators import StandardPaginator


class ClientList(viewsets.ViewSet, generics.ListAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    pagination_class = StandardPaginator

    def get(self, request, format=None, **kwargs):
        clients = Client.objects.all()
        return Response(clients)


class ClientDetail(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get(self, request, *args, **kwargs):
        client = Client.objects.get(pk=kwargs.get('pk'))
        serialized_client = self.serializer_class(data=client)
        if serialized_client.is_valid():
            return Response(serialized_client.data)
        return Response(serialized_client.errors)
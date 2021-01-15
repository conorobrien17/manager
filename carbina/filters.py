from .models import Client, Address
import django_filters


class AddressFilter(django_filters.FilterSet):
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'zip_code']


class ClientFilter(django_filters.FilterSet):
    class Meta:
        model = Client
        fields = ['first_name', 'last_name', 'home_phone', 'cell_phone', 'email_address']
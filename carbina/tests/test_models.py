from django.test import TestCase
from carbina.models import Client, Address
from carbina.async_tasks import forward_geocode_call
from carbina.utils import are_nav_values_loaded
from carbina.apps import FALSE_FLAG, TRUE_FLAG, ERROR_FLAG, OK_FLAG

_fn = 'Conor'
_ln = 'Tester'
_em = 'chobrien@loyola.edu'
_hp = '+16106629464'


class ClientTest(TestCase):
    def setUp(self):
        Client.objects.create(first_name=_fn, last_name=_ln, email_address=_em)

    def test_home_phone(self):
        client = Client.objects.get(pk=1)
        client.home_phone = _hp
        client.save()
        self.assertEqual(client.home_phone, _hp)

    def test_home_phone_no_intl(self):
        client = Client.objects.get(pk=1)
        client.home_phone = '6106629464'
        client.save()
        self.assertNotEqual(client.home_phone, _hp)


class AddressTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Client.objects.create(first_name=_fn, last_name=_ln, email_address=_em)

    def setUp(self):
        _street = '820 Rhinehart Ln'
        _city = 'Phoenixville'
        _state = 'PA'
        _zip_code = 19460
        client = Client.objects.get(pk=1)
        Address.objects.create(street=_street, city=_city, state=_state, zip_code=_zip_code, owner=client)

    def test_valid_object(self):
        address = Address.objects.get(pk=1)
        self.assertEqual(address.__str__(), '820 Rhinehart Ln, Phoenixville PA')

    def test_detail_url(self):
        address = Address.objects.get(pk=1)
        self.assertEqual(address.get_absolute_url(), '/carbina/addresses/1/detail')

    def test_are_nav_values_loaded(self):
        address = Address.objects.get(pk=1)
        tmp = are_nav_values_loaded(address)

        # Test empty condition
        self.assertEqual(tmp, FALSE_FLAG)

        # Load dummy data into the object and check again
        address.driving_summary = "PA RT 23"
        address.duration_shop = 15.6104341
        address.distance_shop = 8.1234521
        address.save()
        tmp = are_nav_values_loaded(address)
        self.assertEqual(tmp, TRUE_FLAG)

        # Test for empty address
        tmp = are_nav_values_loaded(None)
        self.assertEqual(tmp, ERROR_FLAG)

    def test_geocode_latitude(self):
        address = Address.objects.get(pk=1)
        address = forward_geocode_call(address)
        address.save()
        self.assertEqual(address.latitude, -75.497311)

    def test_geocode_longitude(self):
        address = Address.objects.get(pk=1)
        address = forward_geocode_call(address)
        address.save()
        self.assertEqual(address.longitude, 40.122863)

    def test_geocode_together(self):
        address = Address.objects.get(pk=1)
        address = forward_geocode_call(address)
        address.save()
        self.assertEqual(address.latitude, -75.497311)
        self.assertEqual(address.longitude, 40.122863)
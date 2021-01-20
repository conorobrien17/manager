from django.test import TestCase
from django.test import Client as TestClient
from employee_auth.models import User
from carbina.models import Client, Address
import carbina.async_tasks as tasks
from carbina.apps import ERROR_FLAG

_fn = 'Conor'
_ln = 'Tester'
_em = 'chobrien@loyola.edu'
_hp = '+16106629464'

_street = '820 Rhinehart Ln'
_city = 'Phoenixville'
_state = 'PA'
_zip_code = 19460
_lat = -75.497311
_long = 40.122863

# **NOTE**
# These expected values rely on MapBox's API call and are subject to change,
# if these are coming back false, try the API call to get the values for the
# address and update the expected values. Otherwise you messed up somewhere :)
_EXPECTED_DURATION = 15.735033333333332
_EXPECTED_DISTANCE = 8.328991191441979
_EXPECTED_SUMMARY = 'North Park Avenue, Valley Forge Road'


class AsyncCalls(TestCase):
    t_client: TestClient
    client: Client
    address: Address
    user: User

    @classmethod
    def setUpTestData(cls):
        Client.objects.create(first_name=_fn, last_name=_ln, email_address=_em).save()

    def setUp(self):
        self.client = Client.objects.get(pk=1)
        Address.objects.create(street=_street, city=_city, state=_state, zip_code=_zip_code, owner=self.client,
                               owner_id=self.client.pk)
        self.address = Address.objects.get(pk=1)
        self.address.latitude = _lat
        self.address.longitude = _long
        self.address.save()

    def test_latitude(self):
        address = tasks.forward_geocode_call(self.address)
        address.save()
        self.assertEqual(address.latitude, _lat)

    def test_longitude(self):
        address = tasks.forward_geocode_call(self.address)
        address.save()
        self.assertEqual(address.longitude, _long)

    def test_static_map(self):
        address = tasks.get_static_map_image(self.address)
        self.assertIsNotNone(address.static_map)

    def test_static_map_null_coord(self):
        temp_address = self.address
        temp_address.latitude = None
        temp_address.static_map = None
        address = tasks.get_static_map_image(temp_address)
        self.assertEqual(address, ERROR_FLAG)

    def test_nagivation_info(self):
        tmp = tasks.get_navigation_info(None)
        self.assertEqual(tmp, ERROR_FLAG)
        address = tasks.get_navigation_info(self.address)
        self.assertEqual(address.duration_shop, 15.158566666666667)
        self.assertEqual(address.distance_shop, 8.32899181281317)
        self.assertEqual(address.driving_summary, 'North Park Avenue, Valley Forge Road')

from django.test import TestCase
from carbina.models import Address, Client
from employee_auth.models import User
from django.urls import reverse
from django.test import Client as TestClient


clients = [
    {'first': 'Conor', 'last': 'OBrien', 'email': 'chobrien@loyola.edu'},
    {'first': 'Kate', 'last': 'Smith', 'email': 'kate00@gmail.gmail'},
    {'first': 'Francis', 'last': 'Ocean', 'email': 'frank@ocean.com'},
    {'first': 'Charles', 'last': 'LeClerc', 'email': 'charles@monaco.mc'},
    {'first': 'Lando', 'last': 'Norris', 'email': 'lando_norris@superlongjusttoseemclaren.com'},
    {'first': 'George', 'last': 'Russell', 'email': 'george@icloud.com'},
    {'first': 'Lewis', 'last': 'Hamilton', 'email': 'lhamilton@gmail.com'},
    {'first': 'Alexandra', 'last': 'Parker', 'email': 'alexa.parker@yahaoo.com'},
    {'first': 'Jillian', 'last': 'Thompson', 'email': 'jillyt@pentagon.gov'},
    {'first': 'Sean', 'last': 'Spicer', 'email': 'chobrien@whitehouse.gov'},
    {'first': 'Enzo', 'last': 'Ferrari', 'email': 'enzo@ferrari.it'},
    {'first': 'Mia', 'last': 'Lake', 'email': 'mialake31234dq@gcc.edu'},
    {'first': 'Christian', 'last': 'Pope', 'email': 'cthepope123@gmail.com'},
    {'first': 'Conor', 'last': 'Hamilton', 'email': 'chobrien@cs.loyola.edu'},
    {'first': 'Quinn', 'last': 'OBrien', 'email': 'quinno44@gmail.com'},
]

_first_names = []
_last_names = []
_emails = []


class ClientListView(TestCase):
    t_client: TestClient
    user: User

    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_clients = 15
        cls.t_client = TestClient()
        cls.user = User.objects.create(username="tester", first_name="Test", last_name="Tester", phone="+16106629565", company_email="test@arenatreespecialists.com", personal_email="tester123@gmail.com")
        cls.user.set_password("Test4321$$$")
        cls.user.save()

        for client_data in clients:
            Client.objects.create(
                first_name=client_data.get('first'),
                last_name=client_data.get('last'),
                email_address=client_data.get('email')
            ).save()

            _first_names.append(client_data.get('first'))
            _last_names.append(client_data.get('last'))
            _emails.append(client_data.get('email'))

    def setUp(self):
        user = self.t_client.login(username='tester', password='Test4321$$$')

    def test_view_url_exists_at_desired_location(self):
        response = self.t_client.get('/carbina/clients/list', follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.t_client.get(reverse('client-list'), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.t_client.get(reverse('client-list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'carbina/client/list.html')

    def test_context_values(self):
        response = self.t_client.get(reverse('client-list'), follow=True)
        self.assertEqual(response.status_code, 200)

        first_names = []
        last_names = []
        emails = []

        for client in response.context['clients']:
            first_names.append(client.first_name)
            last_names.append(client.last_name)
            emails.append(client.email_address)

        # Sort all of the lists to ensure the data is the same, test the ordering elsewhere
        first_names.sort()
        _first_names.sort()
        last_names.sort()
        _last_names.sort()
        emails.sort()
        _emails.sort()
        self.assertListEqual(first_names, _first_names)
        self.assertListEqual(last_names, _last_names)
        self.assertListEqual(emails, _emails)


class ClientDetailView(TestCase):
    t_client: TestClient
    user: User

    def setUp(self):
        self.t_client = TestClient()
        user = User.objects.create(username="tester", first_name="Test", last_name="Tester", phone="+16106629565", company_email="test@arenatreespecialists.com", personal_email="tester123@gmail.com")
        user.set_password("Test4321$$$")
        user.save()
        self.user = user

        Client.objects.create(
            first_name=clients[0].get('first'),
            last_name=clients[0].get('last'),
            email_address=clients[0].get('email')
        ).save()

        dummy_client = Client.objects.get(pk=1)
        user = User.objects.get(pk=1)

        Address.objects.create(
            street="816 Rhinehart Ln",
            city="Phoenixville",
            state="PA",
            zip_code=19460,
            owner_id=dummy_client.pk,
            owner=dummy_client,
            created_by_id=user.pk,
            created_by=user,
        ).save()

        auth_user = self.t_client.login(username='tester', password='Test4321$$$')

    def test_view_url_exists_at_desired_location(self):
        response = self.t_client.get('/carbina/clients/1/detail', follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.t_client.get(reverse('client-detail', args=['1']), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        client = Client.objects.get(pk=1)
        response = self.t_client.get(reverse('client-detail', args=[1]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'carbina/client/detail.html')
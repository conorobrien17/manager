from django.test import TestCase
from carbina.models import Address, Client
from employee_auth.models import User
from django.urls import reverse
from django.test import Client as TestClient


clients = [
    {'first': 'Conor', 'last': 'OBrien', 'email': 'chobrien@loyola.edu', 'home_phone': '6106629464', 'cell_phone': '2415429984'},
    {'first': 'Kate', 'last': 'Smith', 'email': 'kate00@gmail.gmail', 'home_phone': '6109332722', 'cell_phone': '2672156109'},
    {'first': 'Francis', 'last': 'Ocean', 'email': 'frank@ocean.com', 'home_phone': '4102652465', 'cell_phone': '9183331234'},
    {'first': 'Charles', 'last': 'LeClerc', 'email': 'charles@monaco.mc', 'home_phone': '9990001234', 'cell_phone': '0018345681'},
    {'first': 'Lando', 'last': 'Norris', 'email': 'lando_norris@superlongjusttoseemclaren.com', 'home_phone': '4513980132', 'cell_phone': '9105694435'},
    {'first': 'George', 'last': 'Russell', 'email': 'george@icloud.com', 'home_phone': '8135698345', 'cell_phone': '9234459840'},
    {'first': 'Lewis', 'last': 'Hamilton', 'email': 'lhamilton@gmail.com', 'home_phone': '5088432584', 'cell_phone': '2678089432'},
    {'first': 'Alexandra', 'last': 'Parker', 'email': 'alexa.parker@yahaoo.com', 'home_phone': '4846236134', 'cell_phone': '4125493051'},
    {'first': 'Jillian', 'last': 'Thompson', 'email': 'jillyt@pentagon.gov', 'home_phone': '3052038812', 'cell_phone': '6129582430'},
    {'first': 'Sean', 'last': 'Spicer', 'email': 'chobrien@whitehouse.gov', 'home_phone': '4193129265', 'cell_phone': '2012135755'},
    {'first': 'Enzo', 'last': 'Ferrari', 'email': 'enzo@ferrari.it', 'home_phone': '2283559759', 'cell_phone': '3259655627'},
    {'first': 'Mia', 'last': 'Lake', 'email': 'mialake31234dq@gcc.edu', 'home_phone': '2059839527', 'cell_phone': '3144621847'},
    {'first': 'Christian', 'last': 'Pope', 'email': 'cthepope123@gmail.com', 'home_phone': '2164101618', 'cell_phone': '3098307182'},
    {'first': 'Conor', 'last': 'Hamilton', 'email': 'chobrien@cs.loyola.edu', 'home_phone': '2349811998', 'cell_phone': '5206339923'},
    {'first': 'Quinn', 'last': 'OBrien', 'email': 'quinno44@gmail.com', 'home_phone': '6054903809', 'cell_phone': '3269687270'},
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


class ClientCreateView(TestCase):
    t_client: TestClient
    user: User
    auth_user = None

    def setUp(self):
        self.t_client = TestClient()
        user = User.objects.create(username="tester", first_name="Test", last_name="Tester", phone="+16106629565", company_email="test@arenatreespecialists.com", personal_email="tester123@gmail.com")
        user.set_password("Test4321$$$")
        user.save()
        self.user = user

        self.auth_user = self.t_client.login(username='tester', password='Test4321$$$')

    def test_get_view_url_exists_at_desired_location(self):
        response = self.t_client.get('/carbina/clients/create', follow=False)
        self.assertEqual(response.status_code, 200)

    def test_get_view_url_accessible_by_name(self):
        response = self.t_client.get(reverse('client-create'), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_get_view_uses_correct_template(self):
        response = self.t_client.get(reverse('client-create'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'carbina/client/create.html')

    def test_post_view_url_exists_at_desired_location(self):
        response = self.t_client.post('/carbina/clients/create', follow=False)
        self.assertEqual(response.status_code, 200)

    def test_post_view_url_accessible_by_name(self):
        response = self.t_client.post(reverse('client-create'), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_post_view_uses_correct_template(self):
        response = self.t_client.post(reverse('client-create'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'carbina/client/create.html')

    def test_post_create_client_data(self):
        data = clients[0]
        args = {
            'form-INITIAL_FORMS': '1',
            'form-TOTAL_FORMS': '2',
            'form-first_name': data.get('first'),
            'form-last_name': data.get('last'),
            'form-home_phone': data.get('home_phone'),
            'form-cell_phone': data.get('cell_phone'),
            'form-email_address': data.get('email'),
            'form-0-street': '816 Rhinehart Lane',
            'form-0-city': 'Phoenixville',
            'form-0-state': 'PA',
            'form-0-zip_code': 19460
        }
        for item in args:
            print(args.get(item))
        response = self.t_client.post(reverse('client-create'), data=args)
        self.assertTemplateUsed(response, 'carbina/client/detail.html')
        self.assertEqual(response.status_code, 200)
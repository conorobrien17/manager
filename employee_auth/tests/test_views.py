from django.test import TestCase
from carbina.models import Address, Client
from employee_auth.models import User
from django.urls import reverse
from django.test import Client as TestClient

_users = [
    {'username': 'tester', 'first_name': 'Test', 'last_name': 'Tester', 'phone': '6106629565', 'company_email': 'test@arenatreespecialists.com', 'personal_email': 'tester123@gmail.com'},
    {'username': 'adam', 'first_name': 'Adam', 'last_name': 'Arena', 'phone': '4848687084', 'company_email': 'adam@arenatreespecialists.com', 'personal_email': 'adamgolf@gmail.com'},
    {'username': 'conor', 'first_name': 'Conor', 'last_name': 'O\'Brien', 'phone': '6106629464', 'company_email': 'conor@arenatreespecialists.com', 'personal_email': 'cobrien@gmail.com'},
    {'username': 'mike', 'first_name': 'Mike', 'last_name': 'Shreiner', 'phone': '1250923453', 'company_email': 'mike@arenatreespecialists.com', 'personal_email': 'mshrine98@gmail.com'},
    {'username': 'rocco', 'first_name': 'Rocco', 'last_name': 'Convict', 'phone': '5124324454', 'company_email': 'rocco@arenatreespecialists.com', 'personal_email': 'roccosomething@yahoo.com'},
    {'username': 'kate', 'first_name': 'Kate', 'last_name': 'Smith', 'phone': '6105743619', 'company_email': 'kate@arenatreespecialists.com', 'personal_email': 'katieo4444@gmail.com'},
    {'username': 'chris', 'first_name': 'Chris', 'last_name': 'OBrien', 'phone': '6105743620', 'company_email': 'christopher@arenatreespecialists.com', 'personal_email': 'christopherforeman@gmail.com'},
    {'username': 'mark', 'first_name': 'Mark', 'last_name': 'Giovinazzio', 'phone': '4847731993', 'company_email': 'mark@arenatreespecialists.com', 'personal_email': 'markg41@icloud.com'},
    {'username': 'herve', 'first_name': 'Herve', 'last_name': 'Franceschi', 'phone': '4932669152', 'company_email': 'herve@arenatreespecialists.com', 'personal_email': 'hfranceschi@loyola.edu'},
    {'username': 'sibren', 'first_name': 'Sibren', 'last_name': 'Isaacman', 'phone': '7172319423', 'company_email': 'sibren@arenatreespecialists.com', 'personal_email': 'sibrenisaacs@ymail.com'},
]


class UserListView(TestCase):
    t_client: TestClient
    user: User
    _usernames = []
    _first_names = []
    _last_names = []
    _phones = []
    _company_emails = []
    _personal_emails = []

    @classmethod
    def setUpTestData(cls):
        # Create 13 authors for pagination tests
        number_clients = 15
        cls.t_client = TestClient()
        cls.user = User.objects.create(username="tester", first_name="Test", last_name="Tester", phone="6106629565", company_email="test@arenatreespecialists.com", personal_email="tester123@gmail.com")
        cls.user.set_password("Test4321$$$")
        cls.user.save()

        cls._usernames.append(_users[0].get('username'))
        cls._first_names.append(_users[0].get('first_name'))
        cls._last_names.append(_users[0].get('last_name'))
        cls._phones.append(_users[0].get('phone'))
        cls._company_emails.append(_users[0].get('company_email'))
        cls._personal_emails.append(_users[0].get('personal_email'))

        for _user in _users[1:]:
            User.objects.create(
                username=_user.get('username'),
                first_name=_user.get('first_name'),
                last_name=_user.get('last_name'),
                company_email=_user.get('company_email'),
                phone=_user.get('phone'),
                personal_email=_user.get('personal_email')
            ).save()

            cls._usernames.append(_user.get('username'))
            cls._first_names.append(_user.get('first_name'))
            cls._last_names.append(_user.get('last_name'))
            cls._phones.append(_user.get('phone'))
            cls._company_emails.append(_user.get('company_email'))
            cls._personal_emails.append(_user.get('personal_email'))

    def setUp(self):
        user = self.t_client.login(username='tester', password='Test4321$$$')

    def test_view_url_exists_at_desired_location(self):
        response = self.t_client.get('/accounts/employees/list', follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.t_client.get(reverse('user-list'), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.t_client.get(reverse('user-list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/employees/list.html')

    def test_context_values(self):
        response = self.t_client.get(reverse('user-list'), follow=True)
        self.assertEqual(response.status_code, 200)

        usernames = []
        first_names = []
        last_names = []
        phones = []
        company_emails = []
        personal_emails = []

        for user in response.context['users']:
            usernames.append(user.username)
            first_names.append(user.first_name)
            last_names.append(user.last_name)
            company_emails.append(user.company_email)
            phones.append(user.phone)
            personal_emails.append(user.personal_email)

        # Sort all of the lists to ensure the data is the same, test the ordering elsewhere
        usernames.sort()
        self._usernames.sort()
        first_names.sort()
        self._first_names.sort()
        last_names.sort()
        self._last_names.sort()
        company_emails.sort()
        self._company_emails.sort()
        personal_emails.sort()
        self._personal_emails.sort()

        self.assertListEqual(usernames, self._usernames)
        self.assertListEqual(first_names, self._first_names)
        self.assertListEqual(last_names, self._last_names)
        self.assertListEqual(company_emails, self._company_emails)
        self.assertListEqual(personal_emails, self._personal_emails)
        # self.assertListEqual(phones, self._phones)


class UserDetailView(TestCase):
    t_client: TestClient
    user: User

    def setUp(self):
        self.t_client = TestClient()
        user = User.objects.create(username="tester", first_name="Test", last_name="Tester", phone="+16106629565", company_email="test@arenatreespecialists.com", personal_email="tester123@gmail.com")
        user.set_password("Test4321$$$")
        user.save()
        self.user = User.objects.get(pk=1)
        auth_user = self.t_client.login(username='tester', password='Test4321$$$')

    def test_view_url_exists_at_desired_location(self):
        response = self.t_client.get('/accounts/employees/1/profile', follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.t_client.get(reverse('user-detail', args=['1']), follow=False)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        client = User.objects.get(pk=1)
        response = self.t_client.get(reverse('user-detail', args=[1]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/employees/detail.html')

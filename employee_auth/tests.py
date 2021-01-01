from django.test import TestCase
from .models import Department
from .models import User

dummy_users = ({"username": "conor", "first_name": "Conor", "last_name": "OBrien", "personal_email": "chobrien@loyola.edu", "company_email": "conor@test.com", "job_title": "Developer", "phone": "+16106629464"},)


class UserModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        temp = dummy_users[0]
        User.objects.create(
            username=temp.get("username"),
            first_name=temp.get("first_name"),
            last_name=temp.get("last_name"),
            personal_email=temp.get("personal_email"),
            company_email=temp.get("company_email"),
            phone=temp.get("phone"),
            job_title=temp.get("job_title")
        )
        pass

    def test_username(self):
        test_user = User.objects.get(pk=1)
        actual_username = test_user.username
        self.assertEquals(actual_username, dummy_users[0].get("username"))

    def test_first_name(self):
        test_user = User.objects.get(pk=1)
        actual_first_name = test_user.first_name
        self.assertEquals(actual_first_name, dummy_users[0].get("first_name"))

    def test_last_name(self):
        test_user = User.objects.get(pk=1)
        actual_last_name = test_user.last_name
        self.assertEquals(actual_last_name, dummy_users[0].get("last_name"))

    def test_personal_email(self):
        test_user = User.objects.get(pk=1)
        actual_personal_email = test_user.personal_email
        self.assertEquals(actual_personal_email, dummy_users[0].get("personal_email"))

    def test_company_email(self):
        test_user = User.objects.get(pk=1)
        actual_company_email = test_user.company_email
        self.assertEquals(actual_company_email, dummy_users[0].get("company_email"))

    def test_phone(self):
        test_user = User.objects.get(pk=1)
        actual_phone = test_user.phone.raw_phone
        self.assertEquals(actual_phone, dummy_users[0].get("phone"))
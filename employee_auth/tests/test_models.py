from django.test import TestCase
from employee_auth.models import Department, User, UserManager
from django.utils import timezone

dummy_users = ({"username": "conor", "first_name": "Conor", "last_name": "OBrien", "personal_email": "chobrien@loyola.edu", "company_email": "conor@test.com", "phone": "+16106629464", "job_title": "Developer", "department": None, "is_active": True, "last_login": None},)
dummy_depts = ({'name': 'Sales', 'manager': None, 'manager_id': 0, 'description': 'Sales staff that go out on quotes'},)


class UserModelTests(TestCase):
    user: User

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        temp = dummy_users[0]
        User.objects.create(
            username=temp.get("username"),
            first_name=temp.get("first_name"),
            last_name=temp.get("last_name"),
            password='LavaLakeLarry123$',
            personal_email=temp.get("personal_email"),
            company_email=temp.get("company_email"),
            phone=temp.get("phone"),
            job_title=temp.get("job_title")
        )
        self.user = User.objects.get(pk=1)

    def test_username(self):
        actual_username = self.user.username
        self.assertEquals(actual_username, dummy_users[0].get("username"))

    def test_first_name(self):
        actual_first_name = self.user.first_name
        self.assertEquals(actual_first_name, dummy_users[0].get("first_name"))

    def test_last_name(self):
        actual_last_name = self.user.last_name
        self.assertEquals(actual_last_name, dummy_users[0].get("last_name"))

    def test_full_name(self):
        expected_full_name = dummy_users[0].get("first_name").title() + " " + dummy_users[0].get("last_name").title()
        self.assertEqual(self.user.full_name, expected_full_name)

    def test_personal_email(self):
        actual_personal_email = self.user.personal_email
        self.assertEquals(actual_personal_email, dummy_users[0].get("personal_email"))

    def test_company_email(self):
        actual_company_email = self.user.company_email
        self.assertEquals(actual_company_email, dummy_users[0].get("company_email"))

    def test_phone(self):
        actual_phone = str(self.user.phone.raw_phone)
        self.assertEquals(actual_phone, str(dummy_users[0].get("phone")))

    def test_user_str(self):
        self.assertEqual(self.user.__str__(), str(dummy_users[0].get("username")))

    def test_ping_login(self):
        login_time = timezone.now()
        dummy_users[0].__setitem__("last_login", login_time)
        self.user.ping_login(login_time)
        self.assertEqual(self.user.last_login, login_time)

    def test_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), '/accounts/employees/1/profile')

    def test_user_repr(self):
        # Ping the login first
        self.user.ping_login(dummy_users[0].get("last_login"))
        self.assertDictEqual(self.user.__repr__(), dummy_users[0])

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), dummy_users[0].get('first_name').title())


class DepartmentModelTests(TestCase):
    dept: Department
    manager_user: User

    @classmethod
    def setUpTestData(cls):
        temp = dummy_users[0]
        User.objects.create(
            username=temp.get('username'),
            first_name=temp.get('first_name'),
            last_name=temp.get('last_name'),
            password='LavaLakeLarry123$',
            personal_email=temp.get('personal_email'),
            company_email=temp.get('company_email'),
            phone=temp.get('phone'),
            job_title=temp.get('job_title')
        ).save()
        cls.manager_user = User.objects.get(username=temp.get('username'))

    def setUp(self):
        dept_data = dummy_depts[0]
        Department.objects.create(
            name=dept_data.get('name'),
            description=dept_data.get('description'),
        ).save()
        self.dept = Department.objects.get(name=dept_data.get('name'))
        self.dept.manager = self.manager_user
        self.dept.manager_id = self.manager_user.id
        self.dept.save()

    def test_name(self):
        self.assertEquals(self.dept.name, dummy_depts[0].get('name'))

    def test_manager(self):
        self.assertEquals(self.dept.manager, self.manager_user)

    def test_description(self):
        self.assertEquals(self.dept.description, dummy_depts[0].get('description'))

    def test_department_str(self):
        self.assertEqual(self.dept.__str__(), dummy_depts[0].get('name').title())

    def test_absolute_url(self):
        self.assertEqual(self.dept.get_absolute_url(), '/accounts/departments/1/detail')

    def test_department_repr(self):
        dummy_depts[0].__setitem__('manager', 'conor')
        dummy_depts[0].__setitem__('manager_id', '1')
        self.assertEqual(self.dept.__repr__(), dummy_depts[0])


class UserManagerTests(TestCase):
    user_manager: UserManager
    _username = dummy_users[0].get("username")
    _personal_email = dummy_users[0].get("personal_email")
    _company_email = dummy_users[0].get("company_email")
    _phone = dummy_users[0].get("phone")
    _job_title = dummy_users[0].get("job_title")
    _first_name = dummy_users[0].get("first_name")
    _last_name = dummy_users[0].get("last_name")

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.user_manager = UserManager()

    def test_create_user(self):
        user_manager = UserManager()
        created_user = user_manager.create_user(
            username=self._username,
            personal_email=self._personal_email,
            company_email=self._company_email,
            phone=self._phone,
            job_title=self._job_title,
            first_name=self._first_name,
            last_name=self._last_name,
            password='LavaLakeLarry123$',
        )
        self.assertEqual(created_user.__str__(), self._username)

    def test_create_user_username_none(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=None,
                personal_email=self._personal_email,
                company_email=self._company_email,
                phone=self._phone,
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'Username is required')

    def test_create_user_username_empty(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=' ',
                personal_email=self._personal_email,
                company_email=self._company_email,
                phone=self._phone,
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'Username is required')

    def test_create_user_personal_email_none(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=None,
                company_email=self._company_email,
                phone=self._phone,
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'Personal email address is required')

    def test_create_user_personal_email_empty(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=' ',
                company_email=self._company_email,
                phone=self._phone,
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'Personal email address is required')

    def test_create_user_work_email_none(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=self._personal_email,
                company_email=None,
                phone=self._phone,
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'Company email address is required')

    def test_create_user_work_email_empty(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=self._personal_email,
                company_email=' ',
                phone=self._phone,
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'Company email address is required')

    def test_create_user_first_name_none(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=self._personal_email,
                company_email=self._company_email,
                phone=self._phone,
                job_title=self._job_title,
                first_name=None,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'The user\'s full name (first and last) is required')

    def test_create_user_first_name_empty(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=self._personal_email,
                company_email=self._company_email,
                phone=self._phone,
                job_title=self._job_title,
                first_name=' ',
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'The user\'s full name (first and last) is required')

    def test_create_user_phone_none(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=self._personal_email,
                company_email=self._company_email,
                phone=None,
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'User\'s phone number must be entered')

    def test_create_user_phone_empty(self):
        user_manager = UserManager()
        with self.assertRaises(ValueError) as cm:
            user_manager.create_user(
                username=self._username,
                personal_email=self._personal_email,
                company_email=self._company_email,
                phone=' ',
                job_title=self._job_title,
                first_name=self._first_name,
                last_name=self._last_name,
                password='LavaLakeLarry123$',
            )

        the_exception = cm.exception
        self.assertEqual(the_exception.__class__, ValueError)
        self.assertEqual(str(the_exception), 'User\'s phone number must be entered')

    def test_create_super_user(self):
        user_manager = UserManager()
        created_user = user_manager.create_superuser(
            username=self._username,
            personal_email=self._personal_email,
            company_email=self._company_email,
            phone=self._phone,
            job_title=self._job_title,
            first_name=self._first_name,
            last_name=self._last_name,
            password='TqwEWFldk1431$'
        )
        self.assertEqual(created_user.__str__(), self._username)
        self.assertIsNotNone(created_user.password)

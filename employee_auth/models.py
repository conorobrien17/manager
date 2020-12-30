from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, PermissionManager
from django.conf import settings
from django.contrib.auth.hashers import is_password_usable, make_password, check_password
from django.urls import reverse
from phone_field import PhoneField
import logging
from .apps import EmployeeAuthConfig as AppSettings
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ValidationError
from django.utils import timezone


class UserManager(BaseUserManager, PermissionManager):
    """ Create a new user account """

    def create_user(self, username, personal_email, company_email, phone, job_title, first_name, last_name, password=None, commit=True):
        if not username:
            raise ValueError('Username is required')
        if not personal_email:
            raise ValueError('Personal email address is required')
        if not company_email:
            raise ValueError('Company email address is required')
        if not first_name or not last_name:
            raise ValueError('The user\'s full name (first and last) is required')
        if not phone:
            raise ValueError('User\'s phone number must be entered')

        user = self.model(
            username=username,
            personal_email=self.normalize_email(personal_email),
            company_email=self.normalize_email(company_email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            account_creation_dt=timezone.now(),
            job_title=job_title,
        )

        user.set_password(password)
        if commit:
            user.save(using=self._db)

        return user

    def create_superuser(self, username, personal_email, company_email, phone, job_title, first_name,
                         last_name, password):
        user = self.create_user(username, personal_email, company_email, phone, job_title, first_name,
                                last_name, password, commit=False)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    personal_email = models.EmailField(max_length=128, unique=True)
    company_email = models.EmailField(max_length=128, unique=True)
    company_email_password = models.CharField(max_length=512, blank=True)
    department = models.ForeignKey("Department", on_delete=models.SET_NULL, related_name="users", blank=True, null=True)
    job_title = models.CharField(max_length=64)
    phone = PhoneField(blank=False, help_text="Best phone number to contact")
    is_active = models.BooleanField(default=True, help_text="Designates whether this user should be treated as "
                                                            "active. Unselect this instead of deleting accounts.")
    is_staff = models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.")
    account_creation_dt = models.DateTimeField(auto_now_add=True, help_text="The date and time the account was created.")
    last_login = models.DateTimeField(blank=True, null=True)
    profile_picture = models.ImageField(blank=True, null=True, help_text="The employee's profile picture")
    objects = UserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'personal_email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'personal_email', 'company_email', 'job_title', 'phone']

    class Meta:
        indexes = [
            models.Index(fields=['username', ]),
            models.Index(fields=['first_name', ]),
            models.Index(fields=['last_name', ]),
            models.Index(fields=['personal_email', ]),
            models.Index(fields=['company_email', ]),
            models.Index(fields=['department', ]),
        ]
        permissions = [
            ("edit_all_users", "Can edit any user"),
            ("edit_username", "Can edit a user\'s username"),
            ("edit_department", "Can assign a user to a department"),
            ("edit_staff_status", "Can edit a user\'s staff status"),
            ("view_phone_number", "Can view a user\'s phone number"),
        ]
        ordering = ['username']

    def __repr__(self):
        return {'username': self.username, 'first_name': self.first_name, 'last_name': self.last_name,
                'personal_email': self.personal_email, 'company_email': self.company_email, "phone": self.phone, "job_title": self.job_title, "department": self.department, "is_active": self.is_active, "last_login": self.last_login}

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', args=[str(self.pk)])

    def ping_login(self, login_time=datetime.utcnow()):
        logging.info("[LOGIN] " + self.full_name + " logged in successfully")
        self.last_login = login_time

    @permission_required('employee_auth.modify_comp_email_password')
    def set_company_email_password(self, password_str):
        if not is_password_usable(password_str):
            raise ValidationError("Password is unusable")
        company_email_password = make_password(password_str)
        logging.info("[COMP. EMAIL PASS. SET] " + self.full_name + " company email password was set")
        self.company_email_password = company_email_password
        self.save()

    def check_company_email_password(self, password_str):
        if not is_password_usable(password_str):
            raise ValidationError("Password entered to check is unusable")
        return check_password(password_str, self.company_email_password)

    @property
    def full_name(self):
        return self.first_name.title() + " " + self.last_name.title()

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.first_name.title()


class Department(models.Model):
    name = models.CharField(max_length=128, unique=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="departments", on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(help_text="A description of the department and what it\'s employees do.", blank=True)

    def get_absolute_url(self):
        return reverse("department-detail", args=[str(self.pk)])

    def __str__(self):
        return str(self.name).title()
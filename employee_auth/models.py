from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, PermissionManager
from django.conf import settings
from django.contrib.auth.hashers import is_password_usable, make_password, check_password
from django.urls import reverse
from django.utils.text import slugify
from phone_field import PhoneField
import logging
from django.utils import timezone


class UserManager(BaseUserManager, PermissionManager):
    """ Create a new user account """

    def create_user(self, username, personal_email, company_email, phone, job_title, first_name, last_name, password, commit=True):
        if not username or len(username.strip()) < 1:
            raise ValueError('Username is required')
        if not personal_email or len(personal_email.strip()) < 1:
            raise ValueError('Personal email address is required')
        if not company_email or len(company_email.strip()) < 1:
            raise ValueError('Company email address is required')
        if not first_name or not last_name or len(first_name.strip()) < 1 or len(last_name.strip()) < 1:
            raise ValueError('The user\'s full name (first and last) is required')
        if not phone or len(str(phone).strip()) < 1:
            raise ValueError('User\'s phone number must be entered')

        # Create the user object without the password field
        user = User.objects.create(
            username=username,
            personal_email=self.normalize_email(personal_email),
            company_email=self.normalize_email(company_email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            account_creation_dt=timezone.now(),
            job_title=job_title,
        )

        # Use django's set_password method to set the user account's pass
        user.set_password(password)

        if commit:
            user.save(using=self._db)

        return user

    # Allows for superusers to be created with the same
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
    slug = models.SlugField(unique=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    personal_email = models.EmailField(max_length=128, unique=True)
    company_email = models.EmailField(max_length=128, unique=True)
    department = models.ForeignKey("Department", on_delete=models.SET_NULL, related_name="users", blank=True, null=True)
    job_title = models.CharField(max_length=64)
    phone = PhoneField(blank=False, help_text="Best phone number to contact")
    is_active = models.BooleanField(default=True, help_text="Designates whether this user should be treated as "
                                                            "active. Unselect this instead of deleting accounts.")
    is_staff = models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.")
    account_creation_dt = models.DateTimeField(auto_now_add=True, help_text="The date and time the account was created.")
    last_login = models.DateTimeField(blank=True, null=True)
    profile_picture = models.ImageField(blank=True, upload_to="profile_pics", null=True, help_text="The employee's profile picture")
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
            ("view_advanced_acc_info", "Can view more administrative information about an account"),
        ]
        ordering = ['username']

    def __repr__(self):
        return {
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'personal_email': self.personal_email,
            'company_email': self.company_email,
            'phone': self.phone.raw_phone,
            'job_title': self.job_title,
            'department': self.department,
            'is_active': self.is_active,
            'last_login': self.last_login}

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('user-detail', args=[self.slug])

    def ping_login(self, login_time=timezone.now()):
        logging.info("[LOGIN] " + self.full_name + " logged in successfully")
        self.last_login = login_time
        self.save()

    @property
    def full_name(self):
        return self.first_name.title() + " " + self.last_name.title()

    def get_short_name(self):
        return self.first_name.title()

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.username)
        super().save(*args, **kwargs)


class Department(models.Model):
    name = models.CharField(max_length=128, unique=True, help_text='The name of the department')
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="departments", on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(help_text="A description of the department and what it\'s employees do.", blank=True)

    def get_absolute_url(self):
        return reverse("department-detail", args=[str(self.pk)])

    def __repr__(self):
        return {
            'name': self.name,
            'manager': self.manager,
            'manager_id': self.manager_id,
            'description': self.description
        }

    def __str__(self):
        return str(self.name).title()
from django.db import models
from phone_field import PhoneField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Service(models.Model):
    title = models.CharField(blank=False, max_length=128, help_text="The name of the service")
    description = models.TextField(blank=False, help_text="A description of this service and what is typically done.")
    quantity = models.PositiveIntegerField(null=True, default=1, help_text="The quantity of this service item")
    price = models.FloatField(null=True, validators=[MinValueValidator(0)], help_text="The quoted price of the service")

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title


class HistoryLogUpdate(models.Model):
    title = models.CharField(blank=False, max_length=64, help_text="The primary text of the update")
    theme = models.CharField(blank=False, max_length=32, default="default", help_text="The theme to be used if any on the update")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "HistoryLogUpdates"

    def __str__(self):
        return self.title


class JobPicture(models.Model):
    filename = models.CharField(blank=False, unique=True, max_length=128, help_text="The unique file name for the "
                                                                                    "image.")
    image = models.ImageField(blank=False, help_text="The image for a job or quote", upload_to="job_pictures/")
    caption = models.TextField(blank=True, help_text="A caption to accompany the image")
    upload_timestamp = models.DateTimeField(auto_now_add=True, help_text="Timestamp for when the image was uploaded")
    uploaded_by = models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name="job_pictures", on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-upload_timestamp"]


class Address(models.Model):
    street = models.CharField(blank=False, max_length=256, help_text="The property\'s street address")
    city = models.CharField(blank=False, max_length=128, help_text="The town or city where the property is located")
    state = models.CharField(blank=False, max_length=64, help_text="The state where the property is located")
    zip_code = models.PositiveIntegerField(null=False, validators=[MaxValueValidator(99999)])
    created_by = models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name="created_addresses", on_delete=models.SET_NULL)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return self.street + ", " + self.city + " " + self.state


class Status(models.Model):
    title = models.CharField(blank=False, max_length=32, help_text="The title of a job/quote status")
    theme = models.CharField(blank=False, max_length=32, help_text="The color theme for this status")
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Client(models.Model):
    first_name = models.CharField(blank=False, max_length=64, help_text="The client\'s first name")
    last_name = models.CharField(blank=False, max_length=64, help_text="The client\'s last name")
    home_phone = PhoneField(blank=True)
    cell_phone = PhoneField(blank=True)
    email_address = models.EmailField(blank=True, null=False, max_length=256, help_text="The client's email address")
    properties = models.ForeignKey(null=True, to="Address", related_name="addresses", on_delete=models.SET_NULL)
    job_list = models.ForeignKey(null=True, to="Job", related_name="jobs", on_delete=models.SET_NULL)
    quote_list = models.ForeignKey(null=True, to="Quote", related_name="quotes", on_delete=models.SET_NULL)

    class Meta:
        ordering = ["last_name", "first_name"]
        permissions = [
            ("can_view_contact_info", "Can view client\'s contact information"),
        ]
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + self.properties.city + ")"


class Quote(models.Model):
    title = models.CharField(blank=False, max_length=64, help_text="A brief descriptive title of the job")
    salesman = models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)
    scheduled_time = models.DateTimeField(auto_now=False, help_text="The time and date scheduled for the quote")
    service_items = models.ForeignKey(null=True, to="Service", related_name="services_requested", on_delete=models.SET_NULL)
    status_history = models.ForeignKey(blank=True, null=True, to="Status", related_name="status_history",
                                       on_delete=models.SET_NULL)
    office_notes = models.TextField(help_text="Office and administrative notes about the quote")
    quote_notes = models.TextField(help_text="Notes for the quote and potential job itself")

    class Meta:
        ordering = ["-scheduled_time", "title"]
        permissions = [
            ("can_view_price", "Can view each item\'s estimated price"),
            ("can_edit_price", "Can edit each item\'s estimated price"),
        ]

    def __str__(self):
        return self.title


class Job(models.Model):
    title = models.CharField(blank=False, max_length=64, help_text="A brief descriptive title of the job")
    quote = models.OneToOneField(null=True, to="Quote", related_name="quote", on_delete=models.SET_NULL)
    foreman = models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)
    scheduled_time = models.DateTimeField(auto_now=False, help_text="The scheduled start time of the job")
    service_items = models.ForeignKey(null=True, to="Service", related_name="services", on_delete=models.SET_NULL)
    status_history = models.ForeignKey(null=True, to="Status", related_name="job_status_history", on_delete=models.SET_NULL)
    history_log = models.ForeignKey(null=True, to="HistoryLogUpdate", related_name="history_log", on_delete=models.SET_NULL)
    images = models.ForeignKey(null=True, to="JobPicture", related_name="images", on_delete=models.SET_NULL)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    storm_job = models.BooleanField(default=False, help_text="Is this a storm damage job?")

    class Meta:
        ordering = ["-scheduled_time"]

    def __str__(self):
        return self.title

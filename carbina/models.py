from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Service(models.Model):
    title = models.CharField(blank=False, max_length=128, help_text="The name of the service")
    description = models.TextField(blank=True, help_text="A description of this service and what is typically done.")
    quantity = models.PositiveIntegerField(null=True, default=1, help_text="The quantity of this service item")

    class Meta:
        abstract = True
        ordering = ["title"]
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title


class QuoteItem(Service):
    price = models.FloatField(null=True, validators=[MinValueValidator(0)], help_text="The quoted price of the service")
    author = models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name="quoted_services",
                               on_delete=models.SET_NULL)
    quote = models.ForeignKey(null=False, to="Quote", related_name="quote_items", on_delete=models.CASCADE)

    class Meta:
        abstract = False
        verbose_name_plural = "QuoteItems"

    @property
    def total_cost(self):
        return "${:,.2f}".format(self.price * self.quantity)


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
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)
    static_map = models.ImageField(upload_to='images', null=True, blank=True)
    distance_shop = models.FloatField(null=True)
    duration_shop = models.FloatField(null=True)
    driving_summary = models.CharField(blank=True, max_length=256, help_text='Brief summary of the recommended route to the address from the shop')
    owner = models.ForeignKey(null=False, to="Client", related_name="addresses", on_delete=models.CASCADE)
    created_by = models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name="created_addresses", on_delete=models.CASCADE)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Addresses'
        ordering = ['city']
        unique_together = ['street', 'city', 'state', 'zip_code']

    def __str__(self):
        return self.street + ", " + self.city + " " + self.state

    def get_absolute_url(self):
        return reverse("address-detail", args=[str(self.pk)])


class Status(models.Model):
    title = models.CharField(blank=False, max_length=32, help_text="The title of a job/quote status")
    theme = models.CharField(blank=False, max_length=32, help_text="The color theme for this status")
    modified = models.DateTimeField(auto_now_add=True)
    job = models.ForeignKey(null=False, to='Job', related_name='statuses', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Client(models.Model):
    first_name = models.CharField(blank=False, max_length=64, help_text="The client\'s first name")
    last_name = models.CharField(blank=False, max_length=64, help_text="The client\'s last name")
    home_phone = PhoneNumberField(blank=True)
    cell_phone = PhoneNumberField(blank=True)
    email_address = models.EmailField(blank=True, null=False, max_length=256, help_text="The client's email address")

    class Meta:
        ordering = ["last_name", "first_name"]
        permissions = [
            ("can_view_contact_info", "Can view client\'s contact information"),
        ]
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_absolute_url(self):
        return reverse("client-detail", args=[str(self.pk)])


class Quote(models.Model):
    title = models.CharField(blank=False, max_length=64, help_text="A brief descriptive title of the job")
    salesman = models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, related_name='sales_quotes', on_delete=models.SET_NULL)
    scheduled_time = models.DateTimeField(auto_now=False, help_text="The time and date scheduled for the quote")
    office_notes = models.TextField(help_text="Office and administrative notes about the quote")
    quote_notes = models.TextField(help_text="Notes for the quote and potential job itself")
    client = models.ForeignKey(null=True, to="Client", related_name="quotes", on_delete=models.SET_NULL)
    address = models.ForeignKey(null=True, to='Address', related_name='quotes', on_delete=models.SET_NULL)
    created_by = models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='created_quotes', on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-scheduled_time", "title"]
        permissions = [
            ("can_view_price", "Can view each item\'s estimated price"),
            ("can_edit_price", "Can edit each item\'s estimated price"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("quote-detail", args=[str(self.pk)])


class Job(models.Model):
    title = models.CharField(blank=False, max_length=64, help_text="A brief descriptive title of the job")
    quote = models.OneToOneField(null=True, to="Quote", related_name="quote", on_delete=models.SET_NULL)
    foreman = models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, on_delete=models.SET_NULL)
    scheduled_time = models.DateTimeField(auto_now=False, help_text="The scheduled start time of the job")
    images = models.ForeignKey(null=True, to="JobPicture", related_name="images", on_delete=models.SET_NULL)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    storm_job = models.BooleanField(default=False, help_text="Is this a storm damage job?")
    client = models.ForeignKey(null=True, to="Client", related_name="jobs", on_delete=models.SET_NULL)

    class Meta:
        ordering = ["-scheduled_time"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("job-detail", args=[str(self.pk)])

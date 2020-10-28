from django import forms
from django.core.validators import validate_email
from django.forms.formsets import BaseFormSet
from .models import *
import re as regex

PHONE_VALIDATION_REGEX = "^[+]*[(]{0,1}[0-9]{1,4}[)]{0,1}[-\s\.\/0-9]*$"
EMAIL_VALIDATION_REGEX = "[^@]+@[^@]+\.[^@]+"


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('title', 'description', 'quantity', 'price')

    def __init__(self, *args, **kwargs):
        super(ServiceForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(ServiceForm, self).clean()
        title = self.cleaned_data.get('title')
        price = self.cleaned_data.get('price')

        if len(title) < 4:
            self._errors['title'] = self.error_class(['Please enter a more descriptive title'])
        if not price:
            self._errors['price'] = self.error_class(['Please enter the cost of the service'])

        return self.cleaned_data


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('street', 'city', 'state', 'zip_code')

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)

    def clean(self):

        # data from the form is fetched using super function
        super(AddressForm, self).clean()

        # extract the username and text field from the data
        street = self.cleaned_data.get('street')
        city = self.cleaned_data.get('city')
        state = self.cleaned_data.get('state')
        zip_code = self.cleaned_data.get('zip_code')

        # conditions to be met for the username length
        if len(street) < 1:
            self._errors['street'] = self.error_class([
                'Please enter a street address'])
        if len(city) < 1:
            self._errors['city'] = self.error_class([
                'Please enter a valid city'])
        if len(state) < 2:
            self._errors['state'] = self.error_class([
                'Please enter a valid state'])
        if len(str(zip_code)) != 5:
            self._errors['zip_code'] = self.error_class([
                'Please enter a valid zip_code'])

            # return any errors if found
        return self.cleaned_data


class AddressFormSet(BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        streets = []
        cities = []
        states = []
        zip_codes = []
        duplicates = False

        for form in self.forms:
            if form.cleaned_data:
                street = form.cleaned_data['street']
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                zip_code = form.cleaned_data['zip_code']

                if street and street in streets:
                    raise forms.ValidationError(
                        'Addresses must have unique street addresses.',
                        code='duplicate_addresses'
                    )

                if streets and cities and not zip_codes:
                    raise forms.ValidationError(
                        'All addresses require a zip code',
                        code='missing_zip_code'
                    )
                elif zip_codes and streets and not cities:
                    raise forms.ValidationError(
                        'All addresses require a city',
                        code='missing_city'
                    )
                elif zip_codes and cities and not streets:
                    raise forms.ValidationError(
                        'All addresses require a street address',
                        code='missing_street'
                    )


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ('first_name', 'last_name', 'home_phone', 'cell_phone', 'email_address', 'properties')

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(ClientForm, self).clean()
        first_name = self.cleaned_data.get('first_name')
        last_name = self.cleaned_data.get('last_name')
        home_phone = self.cleaned_data.get('home_phone')
        cell_phone = self.cleaned_data.get('cell_phone')
        email_address = self.cleaned_data.get('email_address')

        phone_pattern = regex.compile(PHONE_VALIDATION_REGEX)
        email_pattern = regex.compile(EMAIL_VALIDATION_REGEX)

        if len(first_name) < 1:
            self._errors['first_name'] = self.error_class(['Please enter the client\'s first name'])
        if len(last_name) < 1:
            self._errors['last_name'] = self.error_class(['Please enter the client\'s last name'])
        if home_phone and not phone_pattern.match(home_phone):
            self._errors['home_phone'] = self.error_class(['Please enter a valid home phone'])
        if cell_phone and not phone_pattern.match(cell_phone):
            self._errors['cell_phone'] = self.error_class(['Please enter a valid cell phone'])
        if email_address and not email_pattern.match(email_address):
            self._errors['email_address'] = self.error_class(['Please enter a valid email address'])

        return self.cleaned_data


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ('title', 'salesman', 'scheduled_time', 'service_items', 'office_notes', 'quote_notes')

    def __init__(self, *args, **kwargs):
        super(QuoteForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(QuoteForm, self).clean()
        title = self.cleaned_data.get('title')
        scheduled_time = self.cleaned_data.get('scheduled_time')

        if len(title) < 1:
            self._errors['title'] = self.error_class(['Please enter a title'])
        if not scheduled_time:
            self._errors['scheduled_time'] = self.error_class(['Please enter a meeting time for the quote'])

        return self.cleaned_data


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('title', 'quote', 'foreman', 'scheduled_time', 'service_items', 'images', 'storm_job')

    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(JobForm, self).clean()
        title = self.cleaned_data.get('title')

        if len(title) < 1:
            self._errors['title'] = self.error_class(['Please enter a title'])

        return self.cleaned_data

from django import forms
from django.core.validators import validate_email
from .models import Address


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
        if len(zip_code) != 5:
            self._errors['zip_code'] = self.error_class([
                'Please enter a valid zip_code'])

            # return any errors if found
        return self.cleaned_data

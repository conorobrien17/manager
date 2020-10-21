from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Department
from phone_field import phone_number

_base_fields = ("first_name", "last_name", "personal_email", "company_email", "phone")


class BaseUserEditForm(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    personal_email = forms.EmailField()
    company_email = forms.EmailField()

    class Meta:
        model = User
        fields = _base_fields

    def __init__(self, *args, **kwargs):
        super(BaseUserEditForm, self).__init__(*args, **kwargs)


class AdminUserEditFormMixin(forms.ModelForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    personal_email = forms.EmailField()
    company_email = forms.EmailField()

    class Meta:
        model = User
        fields = _base_fields + ("department", "job_title", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        super(AdminUserEditFormMixin, self).__init__(*args, **kwargs)


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name", "manager", "description")

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
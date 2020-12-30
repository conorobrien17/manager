from django.contrib import admin
from django import forms
import phone_field
import phonenumber_field
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserCreationForm
from .models import User, Department


class AddUserForm(UserCreationForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "personal_email", "company_email", "phone", "job_title",
            "department", "password1", "password2", "groups", "user_permissions")

    def check_passwords_match(self):
        if not self.password1 or not self.password2:
            raise forms.ValidationError("Password fields cannot be empty")
        cleaned_password1 = self.cleaned_data.get("password1")
        cleaned_password2 = self.cleaned_data.get("password2")
        if cleaned_password1 != cleaned_password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_password1

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.check_passwords_match())
        if commit:
            user.save()
        return user


class EditUserForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "personal_email", "company_email", "phone", "job_title",
            "department", "is_active", "is_staff", "last_login",
        )

    # enforce it doesn't get changed, make a separate form for admin use only
    def clean_password(self):
        return self.initial["password"]


class UserAdmin(BaseUserAdmin):
    form = EditUserForm
    add_form = AddUserForm

    list_display = ("username", "first_name", "last_name", "department", "job_title")
    list_filter = ("is_staff",)
    readonly_fields = ["account_creation_dt"]
    fieldsets = (
        ("Account", {"fields": ("username", "password")}),
        ("Personal", {"fields": ("first_name", "last_name", "personal_email", "phone")}),
        ("Employee Information", {"fields": ("company_email", "job_title", "department")}),
        ("Permissions", {"fields": ("groups", "user_permissions", "is_active", "is_staff")}),
        ("Administration", {"fields": ("last_login", "account_creation_dt")})
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username", "first_name", "last_name", "personal_email", "phone", "company_email", "job_title",
                    "department", "is_active", "account_creation_dt", "password1", "password2"
                )
            }
        ),
    )
    search_fields = ("username", "first_name", "last_name", "personal_email")
    ordering = ("username",)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Department)
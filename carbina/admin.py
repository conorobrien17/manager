from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserCreationForm
from .models import Address, Client


class AddressAdmin(admin.ModelAdmin):
    list_display = ("street", "city", "state", "zip_code")
    fieldsets = (
        ("Address", {"fields": ("street", "city", "state", "zip_code")}),
        ("Client", {"fields": ("owner",)}),
        ("GeoLocation", {"fields": ("latitude", "longitude")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "street", "city", "state", "zip_code"
                )
            }
        ),
    )
    search_fields = ("street", "city", "state", "zip_code")
    ordering = ("city",)
    filter_horizontal = ()


admin.site.register(Address, AddressAdmin)
admin.site.register(Client)

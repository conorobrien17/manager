from rest_framework import serializers
from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ("username", "personal_email", "company_email", "phone", "job_title", "first_name", "last_name",
                  "is_staff")

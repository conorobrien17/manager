# Generated by Django 3.1.4 on 2021-01-03 03:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employee_auth', '0003_auto_20210102_2348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='company_email_password',
        ),
    ]
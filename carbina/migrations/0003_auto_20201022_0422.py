# Generated by Django 3.1 on 2020-10-22 04:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carbina', '0002_auto_20201020_2316'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='description',
            field=models.TextField(blank=True, help_text='A description of this service and what is typically done.'),
        ),
    ]

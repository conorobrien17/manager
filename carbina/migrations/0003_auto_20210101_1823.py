# Generated by Django 3.1.4 on 2021-01-01 18:23

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('carbina', '0002_auto_20201231_1902'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='The name of the service', max_length=128)),
                ('description', models.TextField(blank=True, help_text='A description of this service and what is typically done.')),
                ('quantity', models.PositiveIntegerField(default=1, help_text='The quantity of this service item', null=True)),
                ('price', models.FloatField(help_text='The quoted price of the service', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quoted_services', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'QuoteItems',
                'abstract': False,
            },
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.AlterModelOptions(
            name='address',
            options={'ordering': ['city'], 'verbose_name_plural': 'Addresses'},
        ),
        migrations.AddField(
            model_name='quote',
            name='address',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quotes', to='carbina.address'),
        ),
        migrations.AlterUniqueTogether(
            name='address',
            unique_together={('street', 'city', 'state', 'zip_code')},
        ),
    ]

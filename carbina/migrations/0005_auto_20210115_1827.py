# Generated by Django 3.1.4 on 2021-01-15 18:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('carbina', '0004_auto_20210115_1725'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'HistoryLogs',
            },
        ),
        migrations.AddField(
            model_name='historylogupdate',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_history_logs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historylogupdate',
            name='history_log',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='history_log_updates', to='carbina.historylog'),
        ),
        migrations.CreateModel(
            name='QuoteHistoryLog',
            fields=[
                ('historylog_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='carbina.historylog')),
                ('quote', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='history_log', to='carbina.quote')),
            ],
            bases=('carbina.historylog',),
        ),
    ]

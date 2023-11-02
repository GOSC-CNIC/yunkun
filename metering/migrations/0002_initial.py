# Generated by Django 4.2.4 on 2023-08-29 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('metering', '0001_initial'),
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meteringserver',
            name='service',
            field=models.ForeignKey(db_index=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.serviceconfig', verbose_name='服务'),
        ),
    ]
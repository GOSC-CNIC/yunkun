# Generated by Django 4.2.9 on 2024-01-08 06:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0009_orgdatacenter_log_monitor_url_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='datacenter',
            name='endpoint_compute',
        ),
        migrations.RemoveField(
            model_name='datacenter',
            name='endpoint_monitor',
        ),
        migrations.RemoveField(
            model_name='datacenter',
            name='endpoint_object',
        ),
        migrations.RemoveField(
            model_name='datacenter',
            name='endpoint_vms',
        ),
    ]

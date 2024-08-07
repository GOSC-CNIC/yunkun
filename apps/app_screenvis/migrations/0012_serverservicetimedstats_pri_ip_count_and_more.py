# Generated by Django 4.2.9 on 2024-07-10 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_screenvis', '0011_delete_datacenter_delete_hostcpuusage'),
    ]

    operations = [
        migrations.AddField(
            model_name='serverservicetimedstats',
            name='pri_ip_count',
            field=models.IntegerField(blank=True, default=0, verbose_name='私IP总数'),
        ),
        migrations.AddField(
            model_name='serverservicetimedstats',
            name='pri_ip_used_count',
            field=models.IntegerField(blank=True, default=0, verbose_name='已用私网IP数'),
        ),
        migrations.AddField(
            model_name='serverservicetimedstats',
            name='pub_ip_count',
            field=models.IntegerField(blank=True, default=0, verbose_name='公网IP总数'),
        ),
        migrations.AddField(
            model_name='serverservicetimedstats',
            name='pub_ip_used_count',
            field=models.IntegerField(blank=True, default=0, verbose_name='已用公网IP数'),
        ),
    ]

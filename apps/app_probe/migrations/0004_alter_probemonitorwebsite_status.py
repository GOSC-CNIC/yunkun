# Generated by Django 4.2.9 on 2024-04-17 02:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_probe', '0003_probemonitorwebsite_connect_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='probemonitorwebsite',
            name='status',
            field=models.CharField(blank=True, default='', max_length=3, null=True, verbose_name='状态'),
        ),
    ]

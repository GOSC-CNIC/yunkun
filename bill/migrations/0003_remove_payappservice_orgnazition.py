# Generated by Django 4.2.5 on 2023-10-20 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bill', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payappservice',
            name='orgnazition',
        ),
    ]

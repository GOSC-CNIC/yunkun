# Generated by Django 4.2.9 on 2024-04-25 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0008_price_scan_host_price_scan_web'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='period_unit',
            field=models.CharField(choices=[('day', '天'), ('month', '月')], default='month', max_length=8, verbose_name='订购时长单位'),
        ),
    ]

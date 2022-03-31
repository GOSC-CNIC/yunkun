# Generated by Django 3.2.5 on 2022-03-25 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='end_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='终止时间'),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('unknown', '未知'), ('balance', '余额')], default='unknown', max_length=16, verbose_name='付款方式'),
        ),
        migrations.AddField(
            model_name='order',
            name='start_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='起用时间'),
        ),
    ]

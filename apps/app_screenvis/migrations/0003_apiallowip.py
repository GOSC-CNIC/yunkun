# Generated by Django 4.2.9 on 2024-04-15 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_screenvis', '0002_hostcpuusage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiAllowIP',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ip_value', models.CharField(help_text='192.168.1.1、 192.168.1.1/24、192.168.1.66 - 192.168.1.100', max_length=100, verbose_name='IP')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': 'API允许访问的IP',
                'verbose_name_plural': 'API允许访问的IP',
                'db_table': 'screenvis_apiallowip',
                'ordering': ['-creation_time'],
            },
        ),
    ]

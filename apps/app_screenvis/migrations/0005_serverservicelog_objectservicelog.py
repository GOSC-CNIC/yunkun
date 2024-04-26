# Generated by Django 4.2.9 on 2024-04-19 06:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_screenvis', '0004_objectservice_serverservice_vpntimedstats_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerServiceLog',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=255, verbose_name='用户')),
                ('content', models.TextField(max_length=255, verbose_name='操作内容')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('service_cell', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_screenvis.serverservice', verbose_name='云主机服务单元')),
            ],
            options={
                'verbose_name': '云主机服务单元用户操作日志',
                'verbose_name_plural': '云主机服务单元用户操作日志',
                'db_table': 'screenvis_serverservice_log',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ObjectServiceLog',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=255, verbose_name='用户')),
                ('content', models.TextField(max_length=255, verbose_name='操作内容')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('service_cell', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app_screenvis.objectservice', verbose_name='对象存储服务单元')),
            ],
            options={
                'verbose_name': '对象存储服务单元用户操作日志',
                'verbose_name_plural': '对象存储服务单元用户操作日志',
                'db_table': 'screenvis_objectservice_log',
                'ordering': ['-id'],
            },
        ),
    ]
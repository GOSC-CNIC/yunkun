# Generated by Django 3.2.4 on 2021-06-09 08:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # replaces = [('servers', '0001_squashed_0007_serverarchive_user_quota_tag'), ('servers', '0002_auto_20210128_0133'), ('servers', '0003_auto_20210204_0724'), ('servers', '0004_remove_serverarchive_user_quota_tag'), ('servers', '0005_auto_20210407_0307'), ('servers', '0006_auto_20210407_0553')]

    dependencies = [
        ('service', '0001_squashed_0006_userquota_deleted_squashed_0009_rename_data_center_applyvmservice_organization'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Flavor',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('vcpus', models.IntegerField(default=0, verbose_name='虚拟CPU数')),
                ('ram', models.IntegerField(default=0, verbose_name='内存MB')),
                ('enable', models.BooleanField(default=True, verbose_name='可用状态')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '配置样式',
                'verbose_name_plural': '配置样式',
                'db_table': 'flavor',
                'ordering': ['vcpus'],
            },
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='服务器实例名称')),
                ('instance_id', models.CharField(help_text='各接入服务中云主机的ID', max_length=128, verbose_name='云主机实例ID')),
                ('vcpus', models.IntegerField(default=0, verbose_name='虚拟CPU数')),
                ('ram', models.IntegerField(default=0, verbose_name='内存MB')),
                ('ipv4', models.CharField(default='', max_length=128, verbose_name='IPV4')),
                ('image', models.CharField(default='', max_length=255, verbose_name='镜像系统名称')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='server_set', to='service.serviceconfig', verbose_name='接入的服务配置')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_servers', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('public_ip', models.BooleanField(default=True, verbose_name='公/私网')),
                ('task_status', models.SmallIntegerField(choices=[(1, '创建成功'), (2, '正在创建中'), (3, '创建失败')], default=1, verbose_name='创建状态')),
                ('center_quota', models.SmallIntegerField(choices=[(1, '私有资源配额'), (2, '共享资源配额')], default=1, verbose_name='服务配额')),
                ('user_quota', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quota_servers', to='service.userquota', verbose_name='所属用户配额')),
                ('expiration_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='过期时间')),
            ],
            options={
                'verbose_name': '虚拟服务器',
                'verbose_name_plural': '虚拟服务器',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.CreateModel(
            name='ServerArchive',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='服务器实例名称')),
                ('instance_id', models.CharField(help_text='各接入服务中云主机的ID', max_length=128, verbose_name='云主机实例ID')),
                ('vcpus', models.IntegerField(default=0, verbose_name='虚拟CPU数')),
                ('ram', models.IntegerField(default=0, verbose_name='内存MB')),
                ('ipv4', models.CharField(default='', max_length=128, verbose_name='IPV4')),
                ('public_ip', models.BooleanField(default=True, verbose_name='公/私网')),
                ('image', models.CharField(default='', max_length=255, verbose_name='镜像系统名称')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('deleted_time', models.DateTimeField(auto_now_add=True, verbose_name='删除归档时间')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='server_archive_set', to='service.serviceconfig', verbose_name='接入的服务配置')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_server_archives', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('task_status', models.SmallIntegerField(choices=[(1, '创建成功'), (2, '正在创建中'), (3, '创建失败')], default=1, verbose_name='创建状态')),
                ('center_quota', models.SmallIntegerField(choices=[(1, '私有资源配额'), (2, '共享资源配额')], default=1, verbose_name='服务配额')),
                ('user_quota', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='server_archive_set', to='service.userquota', verbose_name='所属用户配额')),
                ('expiration_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='过期时间')),
            ],
            options={
                'verbose_name': '服务器归档记录',
                'verbose_name_plural': '服务器归档记录',
                'ordering': ['-deleted_time'],
            },
        ),
    ]

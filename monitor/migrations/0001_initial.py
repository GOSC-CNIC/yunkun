# Generated by Django 3.2.5 on 2022-05-11 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorJobCeph',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='监控的CEPH集群名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='监控的CEPH集群英文名称')),
                ('job_tag', models.CharField(default='', max_length=255, verbose_name='CEPH集群标签名称')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '监控任务Ceph节点',
                'verbose_name_plural': '监控任务Ceph节点',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='MonitorProvider',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='监控服务名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='监控服务名称')),
                ('endpoint_url', models.CharField(default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='查询接口')),
                ('username', models.CharField(blank=True, default='', help_text='用于此服务认证的用户名', max_length=128, verbose_name='认证用户名')),
                ('password', models.CharField(blank=True, default='', max_length=255, verbose_name='认证密码')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '监控服务配置信息',
                'verbose_name_plural': '监控服务配置信息',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='MonitorJobVideoMeeting',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='科技云会服务节点院所名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='科技云会服务节点院所英文名称')),
                ('job_tag', models.CharField(default='', max_length=255, verbose_name='标签名称')),
                ('ips', models.CharField(default='', help_text='多个ip用“;”分割', max_length=255, verbose_name='ipv4地址')),
                ('longitude', models.FloatField(blank=True, default=0, verbose_name='经度')),
                ('latitude', models.FloatField(blank=True, default=0, verbose_name='纬度')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置')),
            ],
            options={
                'verbose_name': '科技云会视频会议监控工作节点',
                'verbose_name_plural': '科技云会视频会议监控工作节点',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='MonitorJobServer',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='监控的主机集群名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='监控的主机集群英文名称')),
                ('job_tag', models.CharField(default='', max_length=255, verbose_name='主机集群标签名称')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置')),
            ],
            options={
                'verbose_name': '监控服务器节点',
                'verbose_name_plural': '监控服务器节点',
                'ordering': ['-creation'],
            },
        ),
    ]

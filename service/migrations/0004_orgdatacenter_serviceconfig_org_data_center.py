# Generated by Django 4.2.5 on 2023-11-01 06:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0003_contacts_datacenter_province_datacenter_contacts'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrgDataCenter',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='英文名称')),
                ('longitude', models.FloatField(blank=True, default=0, verbose_name='经度')),
                ('latitude', models.FloatField(blank=True, default=0, verbose_name='纬度')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('sort_weight', models.IntegerField(default=0, help_text='值越小排序越靠前', verbose_name='排序值')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='Loki服务备注')),
                ('thanos_endpoint_url', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Thanos服务查询接口')),
                ('thanos_username', models.CharField(blank=True, default='', help_text='用于此服务认证的用户名', max_length=128, verbose_name='Thanos服务认证用户名')),
                ('thanos_password', models.CharField(blank=True, default='', max_length=255, verbose_name='Thanos服务认证密码')),
                ('thanos_receive_url', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Thanos服务接收接口')),
                ('thanos_remark', models.CharField(blank=True, default='', max_length=255, verbose_name='Thanos服务备注')),
                ('loki_endpoint_url', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Loki服务查询接口')),
                ('loki_username', models.CharField(blank=True, default='', help_text='用于此服务认证的用户名', max_length=128, verbose_name='Loki服务认证用户名')),
                ('loki_password', models.CharField(blank=True, default='', max_length=255, verbose_name='Loki服务认证密码')),
                ('loki_receive_url', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Loki服务接收接口')),
                ('loki_remark', models.CharField(blank=True, default='', max_length=255, verbose_name='Loki服务备注')),
                ('organization', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='service.datacenter', verbose_name='机构')),
                ('users', models.ManyToManyField(blank=True, db_table='org_data_center_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理员')),
            ],
            options={
                'verbose_name': '机构数据中心',
                'verbose_name_plural': '机构数据中心',
                'db_table': 'org_data_center',
                'ordering': ['sort_weight'],
            },
        ),
        migrations.AddField(
            model_name='serviceconfig',
            name='org_data_center',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.orgdatacenter', verbose_name='数据中心'),
        ),
    ]

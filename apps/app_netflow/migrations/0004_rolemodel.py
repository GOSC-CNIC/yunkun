# Generated by Django 4.2.9 on 2024-04-06 12:55

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_netflow', '0003_menumodel_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoleModel',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='名称')),
                ('sort_weight', models.IntegerField(help_text='值越小排序越靠前', verbose_name='排序值')),
                ('remark', models.TextField(blank=True, default='', null=True, verbose_name='备注')),
                ('charts', models.ManyToManyField(blank=True, related_name='role_set', related_query_name='role', to='app_netflow.chartmodel', verbose_name='图表权限')),
                ('menus', models.ManyToManyField(blank=True, related_name='role_set', related_query_name='role', to='app_netflow.menumodel', verbose_name='菜单权限')),
                ('users', models.ManyToManyField(blank=True, related_name='netflow_role_set', related_query_name='netflow_role', to=settings.AUTH_USER_MODEL, verbose_name='组员')),
            ],
            options={
                'verbose_name': '权限管理',
                'verbose_name_plural': '权限管理',
                'db_table': 'netflow_role',
                'ordering': ['sort_weight'],
            },
        ),
    ]
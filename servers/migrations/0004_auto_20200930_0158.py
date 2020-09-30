# Generated by Django 2.2.16 on 2020-09-30 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('servers', '0003_remove_server_flavor_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='image_id',
        ),
        migrations.RemoveField(
            model_name='serverarchive',
            name='image_id',
        ),
        migrations.AddField(
            model_name='server',
            name='task_status',
            field=models.SmallIntegerField(choices=[(1, '创建成功'), (2, '正在创建中'), (3, '创建失败')], default=1, verbose_name='创建状态'),
        ),
        migrations.AddField(
            model_name='serverarchive',
            name='task_status',
            field=models.SmallIntegerField(choices=[(1, '创建成功'), (2, '正在创建中'), (3, '创建失败')], default=1, verbose_name='创建状态'),
        ),
    ]

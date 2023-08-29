# Generated by Django 3.2.13 on 2023-08-25 03:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0008_serviceconfig_disk_available'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('vo', '0001_initial'),
        ('servers', '0010_resourceactionlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiskChangeLog',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='云硬盘名称')),
                ('instance_id', models.CharField(help_text='各接入服务单元中云硬盘的ID', max_length=128, verbose_name='云硬盘实例ID')),
                ('instance_name', models.CharField(blank=True, default='', help_text='各接入服务单元中云硬盘的名称', max_length=255, verbose_name='云硬盘实例名称')),
                ('size', models.IntegerField(default=0, verbose_name='容量大小GiB')),
                ('azone_id', models.CharField(blank=True, default='', max_length=36, verbose_name='可用区Id')),
                ('azone_name', models.CharField(blank=True, default='', max_length=36, verbose_name='可用区名称')),
                ('quota_type', models.CharField(choices=[('private', '私有资源配额'), ('shared', '共享资源配额')], default='private', max_length=16, verbose_name='服务单元配额')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('task_status', models.CharField(choices=[('ok', '创建成功'), ('creating', '正在创建中'), ('failed', '创建失败')], default='ok', max_length=16, verbose_name='创建状态')),
                ('expiration_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='过期时间')),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, help_text='云硬盘资源使用量计量开始时间', verbose_name='计量开始时间')),
                ('pay_type', models.CharField(choices=[('prepaid', '包年包月'), ('postpaid', '按量计费'), ('quota', '资源配额券')], default='postpaid', max_length=16, verbose_name='计费方式')),
                ('classification', models.CharField(choices=[('personal', '个人的'), ('vo', 'VO组的')], default='personal', help_text='标识云硬盘属于申请者个人的，还是vo组的', max_length=16, verbose_name='云硬盘归属类型')),
                ('disk_id', models.CharField(editable=False, max_length=36, verbose_name='云硬盘ID')),
                ('log_type', models.CharField(choices=[('expansion', '扩容'), ('post2pre', '按量转包年包月')], max_length=16, verbose_name='变更类型')),
                ('change_time', models.DateTimeField(verbose_name='变更时间')),
                ('change_user', models.CharField(default='', max_length=128, verbose_name='变更人')),
                ('service', models.ForeignKey(db_constraint=False, db_index=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.serviceconfig', verbose_name='服务单元')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
                ('vo', models.ForeignKey(blank=True, db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='vo.virtualorganization', verbose_name='项目组')),
            ],
            options={
                'verbose_name': '云硬盘变更日志',
                'verbose_name_plural': '云硬盘变更日志',
                'db_table': 'disk_change_log',
                'ordering': ['-change_time'],
            },
        ),
        migrations.AddIndex(
            model_name='diskchangelog',
            index=models.Index(fields=['disk_id'], name='idx_disk_id'),
        ),
    ]
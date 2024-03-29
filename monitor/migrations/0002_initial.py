# Generated by Django 4.2.4 on 2023-08-29 08:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('monitor', '0001_initial'),
        ('service', '0001_initial'),
        ('servers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitorwebsite',
            name='user',
            field=models.ForeignKey(blank=True, db_constraint=False, help_text='关联用户有权限管理监控任务和查询监控数据；用户与数据中心原则上只能关联其一', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='monitorjobvideomeeting',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置'),
        ),
        migrations.AddField(
            model_name='monitorjobtidb',
            name='organization',
            field=models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.datacenter', verbose_name='监控机构'),
        ),
        migrations.AddField(
            model_name='monitorjobtidb',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置'),
        ),
        migrations.AddField(
            model_name='monitorjobtidb',
            name='service',
            field=models.ForeignKey(blank=True, db_constraint=False, db_index=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='servers.serviceconfig', verbose_name='云主机服务单元'),
        ),
        migrations.AddField(
            model_name='monitorjobtidb',
            name='users',
            field=models.ManyToManyField(blank=True, db_constraint=False, db_table='monitor_tidb_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户'),
        ),
        migrations.AddField(
            model_name='monitorjobserver',
            name='organization',
            field=models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.datacenter', verbose_name='监控机构'),
        ),
        migrations.AddField(
            model_name='monitorjobserver',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置'),
        ),
        migrations.AddField(
            model_name='monitorjobserver',
            name='service',
            field=models.ForeignKey(blank=True, db_constraint=False, db_index=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='servers.serviceconfig', verbose_name='云主机服务单元'),
        ),
        migrations.AddField(
            model_name='monitorjobserver',
            name='users',
            field=models.ManyToManyField(blank=True, db_constraint=False, db_table='monitor_server_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户'),
        ),
        migrations.AddField(
            model_name='monitorjobceph',
            name='organization',
            field=models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.datacenter', verbose_name='监控机构'),
        ),
        migrations.AddField(
            model_name='monitorjobceph',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置'),
        ),
        migrations.AddField(
            model_name='monitorjobceph',
            name='service',
            field=models.ForeignKey(blank=True, db_constraint=False, db_index=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='servers.serviceconfig', verbose_name='云主机服务单元'),
        ),
        migrations.AddField(
            model_name='monitorjobceph',
            name='users',
            field=models.ManyToManyField(blank=True, db_constraint=False, db_table='monitor_ceph_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户'),
        ),
        migrations.AddField(
            model_name='logsitetimereqnum',
            name='site',
            field=models.ForeignKey(db_constraint=False, db_index=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='monitor.logsite', verbose_name='日志站点'),
        ),
        migrations.AddField(
            model_name='logsite',
            name='organization',
            field=models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.datacenter', verbose_name='机构'),
        ),
        migrations.AddField(
            model_name='logsite',
            name='provider',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='日志数据查询服务提供者'),
        ),
        migrations.AddField(
            model_name='logsite',
            name='site_type',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='monitor.logsitetype', verbose_name='站点类别'),
        ),
        migrations.AddField(
            model_name='logsite',
            name='users',
            field=models.ManyToManyField(blank=True, db_constraint=False, db_table='log_site_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户'),
        ),
        migrations.AddIndex(
            model_name='logsitetimereqnum',
            index=models.Index(fields=['timestamp'], name='idx_timestamp'),
        ),
    ]

# Generated by Django 3.2.5 on 2022-05-11 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('service', '0001_initial'),
        ('monitor', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monitorjobserver',
            name='service',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='monitor_job_server_set', to='service.serviceconfig', verbose_name='所属的服务'),
        ),
        migrations.AddField(
            model_name='monitorjobceph',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置'),
        ),
        migrations.AddField(
            model_name='monitorjobceph',
            name='service',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='monitor_job_ceph_set', to='service.serviceconfig', verbose_name='所属的服务'),
        ),
    ]

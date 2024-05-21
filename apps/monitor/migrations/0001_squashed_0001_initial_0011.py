# Generated by Django 4.2.9 on 2024-05-14 06:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    # replaces = [('monitor', '0001_initial'), ('monitor', '0002_initial'),
    #             ('monitor', '0003_monitorwebsiterecord_and_more'), ('monitor', '0004_alter_monitorwebsite_url'),
    #             ('monitor', '0005_logsite_org_data_center_and_more'), ('monitor', '0006_auto_20231103_0215'),
    #             ('monitor', '0007_remove_logsite_organization_remove_logsite_provider_and_more'),
    #             ('monitor', '0008_alter_logsitetimereqnum_count'),
    #             ('monitor', '0009_remove_monitorwebsite_url_monitorwebsite_odc'), ('monitor', '0010_errorlog'),
    #             ('monitor', '0011_websitedetectionpoint_sort_weight')]

    initial = True

    dependencies = [
        ('service', '0001_squashed_0010_remove_datacenter_endpoint_compute_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_code', models.IntegerField(blank=True, default=0, verbose_name='状态码')),
                ('method', models.CharField(blank=True, default='', max_length=32, verbose_name='请求方法')),
                ('full_path', models.CharField(blank=True, default='', max_length=1024, verbose_name='URI')),
                ('message', models.TextField(blank=True, default='', verbose_name='日志信息')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('username', models.CharField(blank=True, default='', max_length=128, verbose_name='请求用户')),
            ],
            options={
                'verbose_name': '错误日志',
                'verbose_name_plural': '错误日志',
                'db_table': 'error_log',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='LogSiteType',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='对象存储、一体云', max_length=64, unique=True, verbose_name='日志网站类别名称')),
                ('name_en', models.CharField(default='', max_length=128, verbose_name='英文名称')),
                ('sort_weight', models.IntegerField(help_text='值越小排序越靠前', verbose_name='排序值')),
                ('desc', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('modification', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
            ],
            options={
                'verbose_name': '日志单元类别',
                'verbose_name_plural': '日志单元类别',
                'db_table': 'log_site_type',
                'ordering': ['sort_weight'],
            },
        ),
        migrations.CreateModel(
            name='MonitorProvider',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='监控服务名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='监控服务英文名称')),
                ('endpoint_url', models.CharField(default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='查询接口')),
                ('username', models.CharField(blank=True, default='', help_text='用于此服务认证的用户名', max_length=128, verbose_name='认证用户名')),
                ('password', models.CharField(blank=True, default='', max_length=255, verbose_name='认证密码')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('receive_url', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='接收接口')),
                ('bucket_service_name', models.CharField(blank=True, default='', max_length=128, verbose_name='存储桶所在对象存储服务名称')),
                ('bucket_service_url', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='存储桶所在对象存储服务地址')),
                ('bucket_name', models.CharField(blank=True, default='', max_length=128, verbose_name='存储桶名称')),
                ('remark', models.TextField(blank=True, default='', verbose_name='备注')),
            ],
            options={
                'verbose_name': '监控数据查询提供者服务',
                'verbose_name_plural': '监控数据查询提供者服务',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='MonitorWebsiteRecord',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='网站名称')),
                ('url_hash', models.CharField(default='', max_length=64, verbose_name='网址hash值')),
                ('creation', models.DateTimeField(verbose_name='创建时间')),
                ('modification', models.DateTimeField(verbose_name='修改时间')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('is_tamper_resistant', models.BooleanField(default=False, verbose_name='防篡改')),
                ('scheme', models.CharField(default='', help_text='https|tcp://', max_length=32, verbose_name='协议')),
                ('hostname', models.CharField(default='', help_text='hostname:8000', max_length=255, verbose_name='域名[:端口]')),
                ('uri', models.CharField(default='', help_text='/a/b?query=123#test', max_length=1024, verbose_name='URI')),
                ('user_id', models.CharField(blank=True, default='', max_length=36, verbose_name='用户ID')),
                ('username', models.CharField(blank=True, default='', max_length=128, verbose_name='用户名')),
                ('record_time', models.DateTimeField(verbose_name='记录时间')),
                ('type', models.CharField(choices=[('deleted', '删除')], max_length=16, verbose_name='记录类型')),
            ],
            options={
                'verbose_name': '网站监控任务记录',
                'verbose_name_plural': '网站监控任务记录',
                'db_table': 'monitor_website_record',
                'ordering': ['-record_time'],
            },
        ),
        migrations.CreateModel(
            name='MonitorWebsiteTask',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(default='', max_length=2048, verbose_name='要监控的网址')),
                ('url_hash', models.CharField(default='', max_length=64, unique=True, verbose_name='网址hash值')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('is_tamper_resistant', models.BooleanField(default=False, verbose_name='防篡改')),
            ],
            options={
                'verbose_name': '网站监控任务',
                'verbose_name_plural': '网站监控任务',
                'db_table': 'monitor_website_task',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='MonitorWebsiteVersion',
            fields=[
                ('id', models.IntegerField(default=1, primary_key=True, serialize=False)),
                ('version', models.BigIntegerField(default=1, help_text='用于区分网站监控任务表是否有变化', verbose_name='监控任务版本号')),
                ('creation', models.DateTimeField(verbose_name='创建时间')),
                ('modification', models.DateTimeField(verbose_name='修改时间')),
                ('pay_app_service_id', models.CharField(default='', help_text='此服务对应的APP服务（注册在余额结算中的APP服务）id，扣费时需要此id，用于指定哪个服务发生的扣费', max_length=36, verbose_name='余额结算APP子服务ID')),
            ],
            options={
                'verbose_name': '网站监控任务版本',
                'verbose_name_plural': '网站监控任务版本',
                'db_table': 'monitor_website_version_provider',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='TotalReqNum',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('req_num', models.IntegerField(default=0, verbose_name='服务总请求数')),
                ('until_time', models.DateTimeField(verbose_name='截止到时间')),
                ('creation', models.DateTimeField(verbose_name='创建时间')),
                ('modification', models.DateTimeField(verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '本服务和对象存储总请求数',
                'verbose_name_plural': '本服务和对象存储总请求数',
                'db_table': 'total_req_num',
                'ordering': ['creation'],
            },
        ),
        migrations.CreateModel(
            name='WebsiteDetectionPoint',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=128, verbose_name='监控探测点名称')),
                ('name_en', models.CharField(default='', max_length=128, verbose_name='监控探测点英文名称')),
                ('creation', models.DateTimeField(verbose_name='创建时间')),
                ('modification', models.DateTimeField(verbose_name='修改时间')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('enable', models.BooleanField(default=True, verbose_name='是否启用')),
                ('sort_weight', models.IntegerField(default=0, help_text='值越小排序越靠前', verbose_name='排序值')),
                ('provider', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='monitor.monitorprovider', verbose_name='监控查询服务配置信息')),
            ],
            options={
                'verbose_name': '网站监控探测点',
                'verbose_name_plural': '网站监控探测点',
                'db_table': 'website_detection_point',
                'ordering': ['sort_weight'],
            },
        ),
        migrations.CreateModel(
            name='MonitorWebsite',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='网站名称')),
                ('url_hash', models.CharField(default='', max_length=64, verbose_name='网址hash值')),
                ('creation', models.DateTimeField(verbose_name='创建时间')),
                ('modification', models.DateTimeField(verbose_name='修改时间')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('is_tamper_resistant', models.BooleanField(default=False, verbose_name='防篡改')),
                ('scheme', models.CharField(default='', help_text='https|tcp://', max_length=32, verbose_name='协议')),
                ('hostname', models.CharField(default='', help_text='hostname:8000', max_length=255, verbose_name='域名[:端口]')),
                ('uri', models.CharField(default='', help_text='/a/b?query=123#test', max_length=1024, verbose_name='URI')),
                ('is_attention', models.BooleanField(default=False, verbose_name='特别关注')),
                ('odc', models.ForeignKey(blank=True, db_constraint=False, default=None, help_text='关联数据中心后，数据中心管理员有权限访问此监控任务的数据，无监控任务的管理权限；数据中心与用户原则上只能关联其一', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.orgdatacenter', verbose_name='数据中心')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, help_text='关联用户有权限管理监控任务和查询监控数据；用户与数据中心原则上只能关联其一', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '网站监控',
                'verbose_name_plural': '网站监控',
                'db_table': 'monitor_website',
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
                ('prometheus', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Prometheus接口')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('remark', models.CharField(blank=True, default='', max_length=1024, verbose_name='备注')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='monitor.monitorprovider', verbose_name='监控服务配置')),
            ],
            options={
                'verbose_name': '科技云会视频会议监控工作节点',
                'verbose_name_plural': '科技云会视频会议监控工作节点',
                'db_table': 'monitor_monitorjobvideomeeting',
                'ordering': ['-creation'],
            },
        ),
        migrations.CreateModel(
            name='MonitorJobTiDB',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='监控的TiDB集群名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='监控的TiDB集群英文名称')),
                ('job_tag', models.CharField(default='', help_text='模板：xxx_tidb_metric', max_length=255, verbose_name='TiDB集群标签名称')),
                ('prometheus', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Prometheus接口')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('remark', models.TextField(blank=True, default='', verbose_name='备注')),
                ('sort_weight', models.IntegerField(default=0, help_text='值越小排序越靠前', verbose_name='排序值')),
                ('grafana_url', models.CharField(blank=True, default='', max_length=255, verbose_name='Grafana连接')),
                ('dashboard_url', models.CharField(blank=True, default='', max_length=255, verbose_name='Dashboard连接')),
                ('version', models.CharField(blank=True, default='', help_text='xx.xx.xx', max_length=32, verbose_name='TiDB版本')),
                ('org_data_center', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.orgdatacenter', verbose_name='数据中心')),
                ('users', models.ManyToManyField(blank=True, db_constraint=False, db_table='monitor_tidb_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户')),
            ],
            options={
                'verbose_name': 'TiDB监控单元',
                'verbose_name_plural': 'TiDB监控单元',
                'db_table': 'monitor_unit_tidb',
                'ordering': ['sort_weight'],
            },
        ),
        migrations.CreateModel(
            name='MonitorJobServer',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='监控的主机集群名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='监控的主机集群英文名称')),
                ('job_tag', models.CharField(default='', help_text='模板：xxx_node_metric', max_length=255, verbose_name='主机集群标签名称')),
                ('prometheus', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Prometheus接口')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('remark', models.TextField(blank=True, default='', verbose_name='备注')),
                ('sort_weight', models.IntegerField(default=0, help_text='值越小排序越靠前', verbose_name='排序值')),
                ('grafana_url', models.CharField(blank=True, default='', max_length=255, verbose_name='Grafana连接')),
                ('dashboard_url', models.CharField(blank=True, default='', max_length=255, verbose_name='Dashboard连接')),
                ('org_data_center', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.orgdatacenter', verbose_name='数据中心')),
                ('users', models.ManyToManyField(blank=True, db_constraint=False, db_table='monitor_server_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户')),
            ],
            options={
                'verbose_name': '服务器监控单元',
                'verbose_name_plural': '服务器监控单元',
                'db_table': 'monitor_monitorjobserver',
                'ordering': ['sort_weight'],
            },
        ),
        migrations.CreateModel(
            name='MonitorJobCeph',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=255, verbose_name='监控的CEPH集群名称')),
                ('name_en', models.CharField(default='', max_length=255, verbose_name='监控的CEPH集群英文名称')),
                ('job_tag', models.CharField(default='', help_text='模板：xxx_ceph_metric', max_length=255, verbose_name='CEPH集群标签名称')),
                ('prometheus', models.CharField(blank=True, default='', help_text='http(s)://example.cn/', max_length=255, verbose_name='Prometheus接口')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('remark', models.TextField(blank=True, default='', verbose_name='备注')),
                ('sort_weight', models.IntegerField(default=0, help_text='值越小排序越靠前', verbose_name='排序值')),
                ('grafana_url', models.CharField(blank=True, default='', max_length=255, verbose_name='Grafana连接')),
                ('dashboard_url', models.CharField(blank=True, default='', max_length=255, verbose_name='Dashboard连接')),
                ('org_data_center', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.orgdatacenter', verbose_name='数据中心')),
                ('users', models.ManyToManyField(blank=True, db_constraint=False, db_table='monitor_ceph_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户')),
            ],
            options={
                'verbose_name': 'Ceph监控单元',
                'verbose_name_plural': 'Ceph监控单元',
                'db_table': 'monitor_monitorjobceph',
                'ordering': ['sort_weight'],
            },
        ),
        migrations.CreateModel(
            name='LogSite',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='日志单元站点名称')),
                ('name_en', models.CharField(default='', max_length=128, verbose_name='日志单元英文名称')),
                ('log_type', models.CharField(choices=[('http', 'HTTP'), ('nat', 'NAT')], default='http', max_length=16, verbose_name='日志类型')),
                ('job_tag', models.CharField(default='', help_text='Loki日志中对应的job标识，模板xxx_log', max_length=64, verbose_name='网站日志单元标识')),
                ('sort_weight', models.IntegerField(help_text='值越小排序越靠前', verbose_name='排序值')),
                ('desc', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('creation', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('modification', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
                ('org_data_center', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.orgdatacenter', verbose_name='数据中心')),
                ('site_type', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='monitor.logsitetype', verbose_name='站点类别')),
                ('users', models.ManyToManyField(blank=True, db_constraint=False, db_table='log_site_users', related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='管理用户')),
            ],
            options={
                'verbose_name': '日志单元',
                'verbose_name_plural': '日志单元',
                'db_table': 'log_site',
                'ordering': ['sort_weight'],
            },
        ),
        migrations.CreateModel(
            name='LogSiteTimeReqNum',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.PositiveBigIntegerField(verbose_name='统计时间')),
                ('count', models.IntegerField(help_text='负数标识数据无效（查询失败的占位记录，便于后补）', verbose_name='请求量')),
                ('site', models.ForeignKey(db_constraint=False, db_index=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='monitor.logsite', verbose_name='日志站点')),
            ],
            options={
                'verbose_name': '日志单元时序请求量',
                'verbose_name_plural': '日志单元时序请求量',
                'db_table': 'log_site_time_req_num',
                'ordering': ['-timestamp'],
                'indexes': [models.Index(fields=['timestamp'], name='idx_timestamp')],
            },
        ),
    ]

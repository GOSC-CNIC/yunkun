# Generated by Django 4.2.7 on 2023-11-22 07:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # replaces = [('link', '0001_initial'), ('link', '0002_distriframeport_element_delete_port_and_more'),
    #             ('link', '0003_link_alter_distriframeport_options_and_more')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0003_contacts_datacenter_province_datacenter_contacts'),
    ]

    operations = [
        migrations.CreateModel(
            name='DistributionFrame',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default='', max_length=64, verbose_name='设备号')),
                ('model_type', models.CharField(blank=True, default='', max_length=36, verbose_name='设备型号')),
                ('row_count', models.IntegerField(default=None, verbose_name='行数')),
                ('col_count', models.IntegerField(default=None, verbose_name='列数')),
                ('place', models.CharField(blank=True, default='', max_length=128, verbose_name='位置')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '配线架',
                'verbose_name_plural': '配线架',
                'db_table': 'link_distribution_frame',
                'ordering': ('-update_time',),
            },
        ),
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_type', models.CharField(choices=[('fiber', '光纤'), ('lease', '租用线路'), ('port', '配线架端口'), ('box', '光缆接头盒')], max_length=32, verbose_name='网元对象类型')),
                ('object_id', models.CharField(db_index=True, max_length=36, verbose_name='网元对象id')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '网元汇总表',
                'verbose_name_plural': '网元汇总表',
                'db_table': 'link_element',
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='ElementLink',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(verbose_name='链路位置')),
                ('sub_index', models.IntegerField(default=1, verbose_name='同位编号')),
                ('element', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='element_link', to='link.element', verbose_name='网元')),
            ],
            options={
                'verbose_name': '链路网元对应表',
                'verbose_name_plural': '链路网元对应表',
                'db_table': 'link_elementlink',
                'ordering': ('link_id', 'index', 'sub_index'),
            },
        ),
        migrations.CreateModel(
            name='FiberCable',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default='', max_length=64, verbose_name='光缆编号')),
                ('fiber_count', models.IntegerField(verbose_name='总纤芯数量')),
                ('length', models.DecimalField(blank=True, decimal_places=2, default=None, help_text='km', max_digits=10, null=True, verbose_name='长度')),
                ('endpoint_1', models.CharField(blank=True, default='', max_length=255, verbose_name='端点1')),
                ('endpoint_2', models.CharField(blank=True, default='', max_length=255, verbose_name='端点2')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '光缆',
                'verbose_name_plural': '光缆',
                'db_table': 'link_fiber_cable',
                'ordering': ('-update_time',),
            },
        ),
        migrations.CreateModel(
            name='OpticalFiber',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(verbose_name='纤序')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('element', models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='link.element', verbose_name='网元记录')),
                ('fiber_cable', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fibercable_opticalfiber', to='link.fibercable', verbose_name='光缆')),
            ],
            options={
                'verbose_name': '光纤',
                'verbose_name_plural': '光纤',
                'db_table': 'link_optical_fiber',
                'ordering': ('fiber_cable_id', 'sequence'),
            },
        ),
        migrations.CreateModel(
            name='LinkUserRole',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_admin', models.BooleanField(default=False, help_text='用户拥有科技网链路管理功能的管理员权限', verbose_name='链路管理员权限')),
                ('is_readonly', models.BooleanField(default=False, help_text='用户拥有科技网链路管理功能的全局只读权限', verbose_name='链路只读权限')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='userprofile_linkuserrole', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '链路管理用户角色和权限',
                'verbose_name_plural': '链路管理用户角色和权限',
                'db_table': 'link_user_role',
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='LinkOrg',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=64, verbose_name='二级机构名')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('location', models.CharField(blank=True, default='', max_length=64, verbose_name='经纬度')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('data_center', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='datacenter_linkorg', to='service.datacenter', verbose_name='主机构')),
            ],
            options={
                'verbose_name': '机构二级',
                'verbose_name_plural': '机构二级',
                'db_table': 'link_org',
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default='', max_length=64, verbose_name='编号')),
                ('user', models.CharField(blank=True, default='', max_length=128, verbose_name='用户（单位）')),
                ('endpoint_a', models.CharField(blank=True, default='', max_length=255, verbose_name='A端')),
                ('endpoint_z', models.CharField(blank=True, default='', max_length=255, verbose_name='Z端')),
                ('bandwidth', models.IntegerField(blank=True, default=None, help_text='Mbps', null=True, verbose_name='带宽')),
                ('description', models.CharField(blank=True, default='', max_length=255, verbose_name='用途描述')),
                ('line_type', models.CharField(blank=True, default='', max_length=36, verbose_name='线路类型')),
                ('business_person', models.CharField(blank=True, default='', max_length=36, verbose_name='商务对接')),
                ('build_person', models.CharField(blank=True, default='', max_length=36, verbose_name='线路搭建')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('link_status', models.CharField(choices=[('using', '使用'), ('backup', '备用'), ('idle', '闲置')], default='idle', max_length=16, verbose_name='链路状态')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('enable_date', models.DateField(blank=True, default=None, null=True, verbose_name='开通日期')),
                ('elements', models.ManyToManyField(related_name='links', through='link.ElementLink', to='link.element', verbose_name='网元')),
            ],
            options={
                'verbose_name': '链路',
                'verbose_name_plural': '链路',
                'db_table': 'link_link',
                'ordering': ('-update_time',),
            },
        ),
        migrations.CreateModel(
            name='LeaseLine',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_line_number', models.CharField(blank=True, default='', max_length=64, verbose_name='专线号')),
                ('lease_line_code', models.CharField(blank=True, default='', max_length=64, verbose_name='电路代号')),
                ('line_username', models.CharField(blank=True, default='', max_length=36, verbose_name='专线用户')),
                ('endpoint_a', models.CharField(blank=True, default='', max_length=255, verbose_name='A端')),
                ('endpoint_z', models.CharField(blank=True, default='', max_length=255, verbose_name='Z端')),
                ('line_type', models.CharField(blank=True, default='', max_length=36, verbose_name='线路类型')),
                ('cable_type', models.CharField(blank=True, default='', max_length=36, verbose_name='电路类型')),
                ('bandwidth', models.IntegerField(blank=True, default=None, help_text='Mbps', null=True, verbose_name='带宽')),
                ('length', models.DecimalField(blank=True, decimal_places=2, default=None, help_text='km', max_digits=10, null=True, verbose_name='长度')),
                ('provider', models.CharField(blank=True, default='', max_length=36, verbose_name='运营商')),
                ('enable_date', models.DateField(blank=True, default=None, null=True, verbose_name='开通日期')),
                ('is_whithdrawal', models.BooleanField(default=False, help_text='0:在网 1:撤线', verbose_name='是否撤线')),
                ('money', models.DecimalField(blank=True, decimal_places=2, default=None, help_text='元', max_digits=10, null=True, verbose_name='月租费')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('element', models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='link.element', verbose_name='网元记录')),
            ],
            options={
                'verbose_name': '租用线路',
                'verbose_name_plural': '租用线路',
                'db_table': 'link_lease_line',
                'ordering': ('-update_time',),
            },
        ),
        migrations.AddField(
            model_name='elementlink',
            name='link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='element_link', to='link.link', verbose_name='业务链路'),
        ),
        migrations.CreateModel(
            name='DistriFramePort',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default='', help_text='自定义编号', max_length=64, verbose_name='端口编号')),
                ('row', models.IntegerField(default=None, verbose_name='行号')),
                ('col', models.IntegerField(default=None, verbose_name='列号')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('distribution_frame', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distriframe_distriframeport', to='link.distributionframe', verbose_name='配线架')),
                ('element', models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='link.element', verbose_name='网元记录')),
            ],
            options={
                'verbose_name': '配线架端口',
                'verbose_name_plural': '配线架端口',
                'db_table': 'link_distriframe_port',
                'ordering': ('distribution_frame_id', 'row', 'col'),
            },
        ),
        migrations.AddField(
            model_name='distributionframe',
            name='link_org',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='linkorg_distriframe', to='link.linkorg', verbose_name='机构'),
        ),
        migrations.CreateModel(
            name='ConnectorBox',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default='', help_text='自定义编号', max_length=64, verbose_name='接头盒编号')),
                ('place', models.CharField(blank=True, default='', max_length=128, verbose_name='位置')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('location', models.CharField(blank=True, default='', max_length=64, verbose_name='经纬度')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('element', models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='link.element', verbose_name='网元记录')),
            ],
            options={
                'verbose_name': '光缆接头盒',
                'verbose_name_plural': '光缆接头盒',
                'db_table': 'link_connector_box',
                'ordering': ('-update_time',),
            },
        ),
    ]

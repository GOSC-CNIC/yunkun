# Generated by Django 4.2.9 on 2024-01-17 03:03

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import netbox.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service', '0010_remove_datacenter_endpoint_compute_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ASN',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveIntegerField(verbose_name='AS编码')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='名称')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
            ],
            options={
                'verbose_name': 'AS编号',
                'verbose_name_plural': 'AS编号',
                'db_table': 'netbox_asn',
                'ordering': ('number',),
            },
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
            ],
            options={
                'verbose_name': '光缆接头盒',
                'verbose_name_plural': '光缆接头盒',
                'db_table': 'netbox_connector_box',
                'ordering': ('-update_time',),
            },
        ),
        migrations.CreateModel(
            name='ContactPerson',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='姓名')),
                ('telephone', models.CharField(default='', max_length=16, verbose_name='电话')),
                ('email', models.EmailField(blank=True, default='', max_length=254, verbose_name='邮箱地址')),
                ('address', models.CharField(blank=True, default='', help_text='详细的联系地址', max_length=255, verbose_name='联系地址')),
                ('creation_time', models.DateTimeField(blank=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(blank=True, verbose_name='更新时间')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
            ],
            options={
                'verbose_name': '03_机构二级对象联系人',
                'verbose_name_plural': '03_机构二级对象联系人',
                'db_table': 'netbox_contact_person',
                'ordering': ('-creation_time',),
            },
        ),
        migrations.CreateModel(
            name='DistributionFrame',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(default='', max_length=64, verbose_name='设备号')),
                ('model_type', models.CharField(blank=True, default='', max_length=36, verbose_name='设备型号')),
                ('row_count', models.IntegerField(default=0, verbose_name='行数')),
                ('col_count', models.IntegerField(default=0, verbose_name='列数')),
                ('place', models.CharField(blank=True, default='', max_length=128, verbose_name='位置')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '配线架',
                'verbose_name_plural': '配线架',
                'db_table': 'netbox_distribution_frame',
                'ordering': ('-update_time',),
            },
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
            ],
            options={
                'verbose_name': '配线架端口',
                'verbose_name_plural': '配线架端口',
                'db_table': 'netbox_distriframe_port',
                'ordering': ('distribution_frame_id', 'row', 'col'),
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
                'db_table': 'netbox_element',
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='ElementLink',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField(verbose_name='链路位置')),
                ('sub_index', models.IntegerField(default=1, verbose_name='同位编号')),
            ],
            options={
                'verbose_name': '链路网元对应表',
                'verbose_name_plural': '链路网元对应表',
                'db_table': 'netbox_elementlink',
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
                'db_table': 'netbox_fiber_cable',
                'ordering': ('-update_time',),
            },
        ),
        migrations.CreateModel(
            name='IPv4Address',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='更新时间')),
                ('admin_remark', models.CharField(blank=True, default='', max_length=255, verbose_name='网络管理员备注信息')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='机构管理员备注信息')),
                ('ip_address', models.PositiveIntegerField(verbose_name='IP地址')),
            ],
            options={
                'verbose_name': 'IPv4地址',
                'verbose_name_plural': 'IPv4地址',
                'db_table': 'netbox_ipv4_addr',
                'ordering': ('ip_address',),
            },
        ),
        migrations.CreateModel(
            name='IPv4Range',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='名称')),
                ('status', models.CharField(choices=[('assigned', '已分配'), ('reserved', '预留'), ('wait', '未分配')], default='wait', max_length=16, verbose_name='状态')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='更新时间')),
                ('assigned_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='分配时间')),
                ('admin_remark', models.CharField(blank=True, default='', max_length=255, verbose_name='科技网管理员备注信息')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='机构管理员备注信息')),
                ('start_address', models.PositiveIntegerField(verbose_name='起始地址')),
                ('end_address', models.PositiveIntegerField(verbose_name='截止地址')),
                ('mask_len', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(32)], verbose_name='子网掩码长度')),
            ],
            options={
                'verbose_name': 'IPv4地址段',
                'verbose_name_plural': 'IPv4地址段',
                'db_table': 'netbox_ipv4_range',
                'ordering': ('start_address',),
            },
        ),
        migrations.CreateModel(
            name='IPv4RangeRecord',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('record_type', models.CharField(choices=[('assign', '分配'), ('recover', '收回'), ('split', '拆分'), ('merge', '合并'), ('add', '添加'), ('change', '修改'), ('delete', '删除'), ('reserve', '预留')], max_length=16, verbose_name='记录类型')),
                ('ip_ranges', models.JSONField(blank=True, default=dict, verbose_name='拆分或合并的IP段')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注信息')),
                ('start_address', models.PositiveIntegerField(verbose_name='起始地址')),
                ('end_address', models.PositiveIntegerField(verbose_name='截止地址')),
                ('mask_len', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(32)], verbose_name='子网掩码长度')),
            ],
            options={
                'verbose_name': 'IPv4段操作记录',
                'verbose_name_plural': 'IPv4段操作记录',
                'db_table': 'netbox_ipv4_range_record',
                'ordering': ('-creation_time',),
            },
        ),
        migrations.CreateModel(
            name='IPv6Address',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='更新时间')),
                ('admin_remark', models.CharField(blank=True, default='', max_length=255, verbose_name='网络管理员备注信息')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='机构管理员备注信息')),
                ('ip_address', netbox.fields.ByteField(max_length=16, verbose_name='IP地址')),
            ],
            options={
                'verbose_name': 'IPv6地址',
                'verbose_name_plural': 'IPv6地址',
                'db_table': 'netbox_ipv6_addr',
                'ordering': ('ip_address',),
            },
        ),
        migrations.CreateModel(
            name='OrgVirtualObject',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='名称')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注信息')),
                ('contacts', models.ManyToManyField(blank=True, db_constraint=False, db_table='netbox_org_obj_contacts', related_name='+', to='netbox.contactperson', verbose_name='机构二级对象联系人')),
                ('organization', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='service.datacenter', verbose_name='机构')),
            ],
            options={
                'verbose_name': '02_机构二级',
                'verbose_name_plural': '02_机构二级',
                'db_table': 'netbox_org_virt_obj',
                'ordering': ('-creation_time',),
            },
        ),
        migrations.CreateModel(
            name='OpticalFiber',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.IntegerField(verbose_name='纤序')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('element', models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='netbox.element', verbose_name='网元记录')),
                ('fiber_cable', models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fibercable_opticalfiber', to='netbox.fibercable', verbose_name='光缆')),
            ],
            options={
                'verbose_name': '光纤',
                'verbose_name_plural': '光纤',
                'db_table': 'netbox_optical_fiber',
                'ordering': ('fiber_cable_id', 'sequence'),
            },
        ),
        migrations.CreateModel(
            name='NetBoxUserRole',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_ipam_admin', models.BooleanField(default=False, help_text='选中，用户拥有IP管理功能的管理员权限', verbose_name='IP管理员')),
                ('is_ipam_readonly', models.BooleanField(default=False, help_text='选中，用户拥有科技网IP管理功能的全局只读权限', verbose_name='IP管理全局只读权限')),
                ('is_link_admin', models.BooleanField(default=False, help_text='选中，用户拥有链路管理功能的管理员权限', verbose_name='链路管理员')),
                ('is_link_readonly', models.BooleanField(default=False, help_text='选中，用户拥有链路管理功能的全局只读权限', verbose_name='链路管理全局只读权限')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='更新时间')),
                ('organizations', models.ManyToManyField(blank=True, db_table='netbox_user_role_orgs', related_name='+', to='service.datacenter', verbose_name='拥有IP管理员权限的机构')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '01_网络管理用户角色和权限',
                'verbose_name_plural': '01_网络管理用户角色和权限',
                'db_table': 'netbox_user_role',
                'ordering': ('-creation_time',),
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
                ('elements', models.ManyToManyField(related_name='links', through='netbox.ElementLink', to='netbox.element', verbose_name='网元')),
            ],
            options={
                'verbose_name': '链路',
                'verbose_name_plural': '链路',
                'db_table': 'netbox_link',
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
                ('element', models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='netbox.element', verbose_name='网元记录')),
            ],
            options={
                'verbose_name': '租用线路',
                'verbose_name_plural': '租用线路',
                'db_table': 'netbox_lease_line',
                'ordering': ('-update_time',),
            },
        ),
        migrations.CreateModel(
            name='IPv6RangeRecord',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('record_type', models.CharField(choices=[('assign', '分配'), ('recover', '收回'), ('split', '拆分'), ('merge', '合并'), ('add', '添加'), ('change', '修改'), ('delete', '删除'), ('reserve', '预留')], max_length=16, verbose_name='记录类型')),
                ('ip_ranges', models.JSONField(blank=True, default=dict, verbose_name='拆分或合并的IP段')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注信息')),
                ('start_address', netbox.fields.ByteField(max_length=16, verbose_name='起始地址')),
                ('end_address', netbox.fields.ByteField(max_length=16, verbose_name='截止地址')),
                ('prefixlen', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(128)], verbose_name='前缀长度')),
                ('org_virt_obj', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='netbox.orgvirtualobject', verbose_name='分配给机构二级对象')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='操作用户')),
            ],
            options={
                'verbose_name': 'IPv6段操作记录',
                'verbose_name_plural': 'IPv6段操作记录',
                'db_table': 'netbox_ipv6_range_record',
                'ordering': ('-creation_time',),
            },
        ),
        migrations.CreateModel(
            name='IPv6Range',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=255, verbose_name='名称')),
                ('status', models.CharField(choices=[('assigned', '已分配'), ('reserved', '预留'), ('wait', '未分配')], default='wait', max_length=16, verbose_name='状态')),
                ('creation_time', models.DateTimeField(verbose_name='创建时间')),
                ('update_time', models.DateTimeField(verbose_name='更新时间')),
                ('assigned_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='分配时间')),
                ('admin_remark', models.CharField(blank=True, default='', max_length=255, verbose_name='科技网管理员备注信息')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='机构管理员备注信息')),
                ('start_address', netbox.fields.ByteField(max_length=16, verbose_name='起始地址')),
                ('end_address', netbox.fields.ByteField(max_length=16, verbose_name='截止地址')),
                ('prefixlen', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(128)], verbose_name='前缀长度')),
                ('asn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='netbox.asn', verbose_name='AS编号')),
                ('org_virt_obj', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='netbox.orgvirtualobject', verbose_name='分配给机构二级')),
            ],
            options={
                'verbose_name': 'IPv6地址段',
                'verbose_name_plural': 'IPv6地址段',
                'db_table': 'netbox_ipv6_range',
                'ordering': ('start_address',),
            },
        ),
        migrations.AddConstraint(
            model_name='ipv6address',
            constraint=models.UniqueConstraint(fields=('ip_address',), name='netbox_uniq_ipv6_addr'),
        ),
        migrations.AddField(
            model_name='ipv4rangerecord',
            name='org_virt_obj',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='netbox.orgvirtualobject', verbose_name='分配给机构二级对象'),
        ),
        migrations.AddField(
            model_name='ipv4rangerecord',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='操作用户'),
        ),
        migrations.AddField(
            model_name='ipv4range',
            name='asn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='netbox.asn', verbose_name='AS编号'),
        ),
        migrations.AddField(
            model_name='ipv4range',
            name='org_virt_obj',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='netbox.orgvirtualobject', verbose_name='分配给机构二级'),
        ),
        migrations.AddConstraint(
            model_name='ipv4address',
            constraint=models.UniqueConstraint(fields=('ip_address',), name='netbox_uniq_ipv4_addr'),
        ),
        migrations.AddField(
            model_name='elementlink',
            name='element',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='element_link', to='netbox.element', verbose_name='网元'),
        ),
        migrations.AddField(
            model_name='elementlink',
            name='link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='element_link', to='netbox.link', verbose_name='业务链路'),
        ),
        migrations.AddField(
            model_name='distriframeport',
            name='distribution_frame',
            field=models.ForeignKey(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distriframe_distriframeport', to='netbox.distributionframe', verbose_name='配线架'),
        ),
        migrations.AddField(
            model_name='distriframeport',
            name='element',
            field=models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='netbox.element', verbose_name='网元记录'),
        ),
        migrations.AddField(
            model_name='distributionframe',
            name='link_org',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='netbox.orgvirtualobject', verbose_name='机构二级'),
        ),
        migrations.AddField(
            model_name='connectorbox',
            name='element',
            field=models.OneToOneField(db_constraint=False, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='element_%(class)s', to='netbox.element', verbose_name='网元记录'),
        ),
        migrations.AddIndex(
            model_name='ipv6range',
            index=models.Index(fields=['start_address'], name='netbox_idx_ipv6rg_start_addr'),
        ),
        migrations.AddIndex(
            model_name='ipv6range',
            index=models.Index(fields=['end_address'], name='netbox_idx_ipv6rg_end_addr'),
        ),
    ]

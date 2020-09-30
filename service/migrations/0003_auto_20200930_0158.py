# Generated by Django 2.2.16 on 2020-09-30 01:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_auto_20200922_0253'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataCenterPrivateQuota',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='ID')),
                ('private_ip_total', models.IntegerField(default=0, verbose_name='总私网IP数')),
                ('private_ip_used', models.IntegerField(default=0, verbose_name='已用私网IP数')),
                ('public_ip_total', models.IntegerField(default=0, verbose_name='总公网IP数')),
                ('public_ip_used', models.IntegerField(default=0, verbose_name='已用公网IP数')),
                ('vcpu_total', models.IntegerField(default=0, verbose_name='总CPU核数')),
                ('vcpu_used', models.IntegerField(default=0, verbose_name='已用CPU核数')),
                ('ram_total', models.IntegerField(default=0, verbose_name='总内存大小(MB)')),
                ('ram_used', models.IntegerField(default=0, verbose_name='已用内存大小(MB)')),
                ('disk_size_total', models.IntegerField(default=0, verbose_name='总硬盘大小(GB)')),
                ('disk_size_used', models.IntegerField(default=0, verbose_name='已用硬盘大小(GB)')),
                ('enable', models.BooleanField(help_text='选中，资源配额生效；未选中，无法申请分中心资源', verbose_name='有效状态')),
                ('data_center', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_center_private_quota', to='service.DataCenter', verbose_name='数据中心')),
            ],
            options={
                'verbose_name': '数据中心私有资源配额',
                'verbose_name_plural': '数据中心私有资源配额',
                'db_table': 'data_center_private_quota',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='DataCenterShareQuota',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='ID')),
                ('private_ip_total', models.IntegerField(default=0, verbose_name='总私网IP数')),
                ('private_ip_used', models.IntegerField(default=0, verbose_name='已用私网IP数')),
                ('public_ip_total', models.IntegerField(default=0, verbose_name='总公网IP数')),
                ('public_ip_used', models.IntegerField(default=0, verbose_name='已用公网IP数')),
                ('vcpu_total', models.IntegerField(default=0, verbose_name='总CPU核数')),
                ('vcpu_used', models.IntegerField(default=0, verbose_name='已用CPU核数')),
                ('ram_total', models.IntegerField(default=0, verbose_name='总内存大小(MB)')),
                ('ram_used', models.IntegerField(default=0, verbose_name='已用内存大小(MB)')),
                ('disk_size_total', models.IntegerField(default=0, verbose_name='总硬盘大小(GB)')),
                ('disk_size_used', models.IntegerField(default=0, verbose_name='已用硬盘大小(GB)')),
                ('enable', models.BooleanField(help_text='选中，资源配额生效；未选中，无法申请分中心资源', verbose_name='有效状态')),
                ('data_center', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_center_share_quota', to='service.DataCenter', verbose_name='数据中心')),
            ],
            options={
                'verbose_name': '数据中心分享资源配额',
                'verbose_name_plural': '数据中心分享资源配额',
                'db_table': 'data_center_share_quota',
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='serviceconfig',
            name='extra',
            field=models.CharField(blank=True, default='', help_text='json格式', max_length=1024, verbose_name='其他配置'),
        ),
        migrations.DeleteModel(
            name='ServiceQuota',
        ),
    ]

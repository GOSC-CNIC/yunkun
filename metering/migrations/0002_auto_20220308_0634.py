# Generated by Django 3.2.5 on 2022-03-08 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0007_auto_20211119_0203'),
        ('metering', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeteringDisk',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('disk_id', models.CharField(max_length=36, verbose_name='云硬盘ID')),
                ('date', models.DateField(help_text='计量的资源使用量的所属日期', verbose_name='日期')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('user_id', models.CharField(blank=True, default='', max_length=36, verbose_name='用户ID')),
                ('vo_id', models.CharField(blank=True, default='', max_length=36, verbose_name='VO组ID')),
                ('owner_type', models.CharField(choices=[('user', '用户'), ('vo', 'VO组')], max_length=8, verbose_name='所有者类型')),
                ('size_hours', models.FloatField(blank=True, default=0, help_text='云硬盘Gib Hour数', verbose_name='云硬盘GiB Hour')),
                ('snapshot_hours', models.FloatField(blank=True, default=0, help_text='云硬盘快照GiB小时数', verbose_name='快照GiB Hour')),
                ('pay_type', models.CharField(choices=[('prepaid', '包年包月'), ('postpaid', '按量计费'), ('quota', '资源配额券')], max_length=16, verbose_name='云硬盘付费方式')),
                ('service', models.ForeignKey(db_index=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='service.serviceconfig', verbose_name='服务')),
            ],
            options={
                'verbose_name': '云硬盘资源计量',
                'verbose_name_plural': '云硬盘资源计量',
                'db_table': 'metering_disk',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.AddConstraint(
            model_name='meteringdisk',
            constraint=models.UniqueConstraint(fields=('date', 'disk_id'), name='unique_date_disk'),
        ),
    ]

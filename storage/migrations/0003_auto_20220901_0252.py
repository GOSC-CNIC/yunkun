# Generated by Django 3.2.13 on 2022-09-01 02:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storage', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bucket',
            name='access_perm',
        ),
        migrations.RemoveField(
            model_name='bucket',
            name='lock',
        ),
        migrations.RemoveField(
            model_name='bucket',
            name='token',
        ),
        migrations.RemoveField(
            model_name='bucketarchive',
            name='access_perm',
        ),
        migrations.RemoveField(
            model_name='bucketarchive',
            name='lock',
        ),
        migrations.AddField(
            model_name='bucketarchive',
            name='archiver',
            field=models.CharField(blank=True, default='', max_length=128, verbose_name='删除归档人'),
        ),
        migrations.AddField(
            model_name='bucketarchive',
            name='original_id',
            field=models.CharField(default='', help_text='存储桶删除前在存储桶表中原始id', max_length=36, verbose_name='存储桶删除前原始id'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='contact_address',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='联系人地址'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='contact_email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='联系人邮箱'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='contact_fixed_phone',
            field=models.CharField(blank=True, default='', max_length=16, verbose_name='联系人固定电话'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='contact_person',
            field=models.CharField(blank=True, default='', max_length=128, verbose_name='联系人名称'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='contact_telephone',
            field=models.CharField(blank=True, default='', max_length=16, verbose_name='联系人电话'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='ftp_domains',
            field=models.CharField(blank=True, default='', help_text='多个域名时以,分割', max_length=1024, verbose_name='FTP服务域名或IP'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='latitude',
            field=models.FloatField(blank=True, default=0, verbose_name='纬度'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='logo_url',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='LOGO url'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='longitude',
            field=models.FloatField(blank=True, default=0, verbose_name='经度'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='name_en',
            field=models.CharField(default='', max_length=255, verbose_name='服务英文名称'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='pay_app_service_id',
            field=models.CharField(default='', help_text='此服务对应的APP服务（注册在余额结算中的APP服务）id，扣费时需要此id，用于指定哪个服务发生的扣费', max_length=36, verbose_name='余额结算APP服务ID'),
        ),
        migrations.AddField(
            model_name='objectsservice',
            name='provide_ftp',
            field=models.BooleanField(default=True, verbose_name='是否提供FTP服务'),
        ),
        migrations.AlterField(
            model_name='bucket',
            name='creation_time',
            field=models.DateTimeField(verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='bucket',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='storage.objectsservice', verbose_name='所属服务'),
        ),
        migrations.AlterField(
            model_name='bucket',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='所属用户'),
        ),
        migrations.AlterField(
            model_name='bucketarchive',
            name='creation_time',
            field=models.DateTimeField(verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='bucketarchive',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='storage.objectsservice', verbose_name='所属服务'),
        ),
        migrations.AlterField(
            model_name='bucketarchive',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='所属用户'),
        ),
        migrations.AlterField(
            model_name='objectsservice',
            name='service_type',
            field=models.CharField(choices=[('iharbor', 'iHarbor'), ('swift', 'Swift'), ('s3', 'S3')], default='iharbor', max_length=16, verbose_name='服务平台类型'),
        ),
        migrations.AlterField(
            model_name='objectsservice',
            name='status',
            field=models.CharField(choices=[('enable', '服务中'), ('disable', '停止服务'), ('deleted', '删除')], default='enable', max_length=16, verbose_name='服务状态'),
        ),
    ]

# Generated by Django 3.2.5 on 2022-05-11 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bucket',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('bucket_id', models.CharField(max_length=36, verbose_name='存储桶ID')),
                ('name', models.CharField(max_length=63, verbose_name='存储桶名称')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('access_perm', models.CharField(choices=[('public', '公有'), ('private', '私有')], default='private', max_length=16, verbose_name='访问权限')),
                ('lock', models.CharField(choices=[('readwrite', '可读可写'), ('readonly', '只读'), ('forbidden', '禁止访问')], default='readwrite', max_length=16, verbose_name='读写锁')),
                ('token', models.CharField(max_length=36, verbose_name='桶读写token')),
            ],
            options={
                'verbose_name': '存储桶',
                'verbose_name_plural': '存储桶',
                'db_table': 'bucket',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.CreateModel(
            name='BucketArchive',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=63, verbose_name='存储桶名称')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('access_perm', models.CharField(choices=[('public', '公有'), ('private', '私有')], default='private', max_length=16, verbose_name='访问权限')),
                ('lock', models.CharField(choices=[('readwrite', '可读可写'), ('readonly', '只读'), ('forbidden', '禁止访问')], default='readwrite', max_length=16, verbose_name='读写锁')),
                ('bucket_id', models.CharField(max_length=36, verbose_name='存储桶ID')),
                ('delete_time', models.DateTimeField(auto_now_add=True, verbose_name='删除时间')),
            ],
            options={
                'verbose_name': '存储桶归档记录',
                'verbose_name_plural': '存储桶归档记录',
                'db_table': 'bucket_archive',
                'ordering': ['-delete_time'],
            },
        ),
        migrations.CreateModel(
            name='ObjectsService',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='服务名称')),
                ('service_type', models.CharField(choices=[('iharbor', 'iHarhor'), ('swift', 'Swift'), ('s3', 'S3')], default='iharbor', max_length=16, verbose_name='服务平台类型')),
                ('endpoint_url', models.CharField(help_text='http(s)://{hostname}:{port}/', max_length=255, unique=True, verbose_name='服务地址url')),
                ('api_version', models.CharField(default='v3', help_text='预留，主要iHarbor使用', max_length=64, verbose_name='API版本')),
                ('username', models.CharField(help_text='用于此服务认证的用户名', max_length=128, verbose_name='用户名')),
                ('password', models.CharField(max_length=128, verbose_name='密码')),
                ('add_time', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('status', models.CharField(choices=[('serving', '服务中'), ('out_of', '停止服务')], default='serving', max_length=16, verbose_name='服务状态')),
                ('remarks', models.CharField(blank=True, default='', max_length=255, verbose_name='备注')),
                ('extra', models.CharField(blank=True, default='', help_text='json格式', max_length=1024, verbose_name='其他配置')),
            ],
            options={
                'verbose_name': '对象存储服务接入配置',
                'verbose_name_plural': '对象存储服务接入配置',
                'db_table': 'object_service',
                'ordering': ['-add_time'],
            },
        ),
        migrations.CreateModel(
            name='StorageQuota',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_total', models.IntegerField(default=0, verbose_name='存储桶数')),
                ('count_used', models.IntegerField(default=0, verbose_name='已创建存储桶数')),
                ('size_gb_total', models.IntegerField(default=0, help_text='Gb', verbose_name='总存储容量')),
                ('size_gb_used', models.IntegerField(default=0, help_text='Gb', verbose_name='已用存储容量')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('expiration_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='过期时间')),
                ('deleted', models.BooleanField(default=False, verbose_name='删除')),
                ('is_email', models.BooleanField(default=False, help_text='是否邮件通知用户配额即将到期', verbose_name='是否邮件通知')),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='storage_quotas', to='storage.objectsservice', verbose_name='所属服务')),
            ],
            options={
                'verbose_name': '存储配额',
                'verbose_name_plural': '存储配额',
                'db_table': 'storage_quota',
                'ordering': ['-creation_time'],
            },
        ),
    ]

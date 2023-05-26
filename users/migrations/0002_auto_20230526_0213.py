# Generated by Django 3.2.13 on 2023-05-26 02:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='email',
            name='is_html',
            field=models.BooleanField(default=False, verbose_name='html格式信息'),
        ),
        migrations.AddField(
            model_name='email',
            name='tag',
            field=models.CharField(choices=[('year', '年度报表'), ('month', '月度报表'), ('ticket', '工单通知'), ('coupon', '代金券通知'), ('res-exp', '资源过期通知'), ('other', '其他')], default='other', max_length=16, verbose_name='标签'),
        ),
        migrations.AddField(
            model_name='email',
            name='status',
            field=models.CharField(choices=[('wait', '待发送'), ('success', '发送成功'), ('failed', '发送失败')], default='success', max_length=16, verbose_name='发送状态'),
        ),
        migrations.AddField(
            model_name='email',
            name='status_desc',
            field=models.CharField(default='', max_length=255, verbose_name='状态描述'),
        ),
        migrations.AddField(
            model_name='email',
            name='success_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='成功发送时间'),
        ),
    ]

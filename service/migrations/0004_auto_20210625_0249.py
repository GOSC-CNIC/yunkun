# Generated by Django 3.2.4 on 2021-06-25 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vo', '0001_initial'),
        ('service', '0003_auto_20210623_0637'),
    ]

    operations = [
        migrations.AddField(
            model_name='applyquota',
            name='classification',
            field=models.CharField(choices=[('personal', '个人的'), ('vo', 'VO组的')], default='personal', help_text='标识配额属于申请者个人的，还是vo组的', max_length=16, verbose_name='资源配额归属类型'),
        ),
        migrations.AddField(
            model_name='applyquota',
            name='vo',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vo_apply_quota_set', to='vo.virtualorganization', verbose_name='项目组'),
        ),
        migrations.AddField(
            model_name='userquota',
            name='classification',
            field=models.CharField(choices=[('personal', '个人的'), ('vo', 'VO组的')], default='personal', help_text='标识配额属于申请者个人的，还是vo组的', max_length=16, verbose_name='资源配额归属类型'),
        ),
    ]

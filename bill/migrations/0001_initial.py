# Generated by Django 3.2.5 on 2022-05-11 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentHistory',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_account', models.CharField(blank=True, default='', help_text='用户或VO余额ID, 及可能支持的其他账户', max_length=36, verbose_name='付款账户')),
                ('payment_method', models.CharField(choices=[('balance', '余额')], default='balance', max_length=16, verbose_name='付款方式')),
                ('executor', models.CharField(blank=True, default='', help_text='记录此次支付交易是谁执行完成的', max_length=128, verbose_name='交易执行人')),
                ('payer_id', models.CharField(blank=True, default='', help_text='user id or vo id', max_length=36, verbose_name='付款人ID')),
                ('payer_name', models.CharField(blank=True, default='', help_text='username or vo name', max_length=255, verbose_name='付款人名称')),
                ('payer_type', models.CharField(choices=[('user', '用户'), ('vo', 'VO组')], max_length=8, verbose_name='付款人类型')),
                ('amounts', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='金额')),
                ('before_payment', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='支付前余额')),
                ('after_payment', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='支付后余额')),
                ('payment_time', models.DateTimeField(auto_now_add=True, verbose_name='支付时间')),
                ('type', models.CharField(choices=[('recharge', '充值'), ('payment', '支付'), ('refund', '退款')], max_length=16, verbose_name='支付类型')),
                ('remark', models.CharField(blank=True, default='', max_length=255, verbose_name='备注信息')),
                ('order_id', models.CharField(blank=True, default='', max_length=36, verbose_name='订单ID')),
                ('resource_type', models.CharField(choices=[('vm', '云主机'), ('disk', '云硬盘'), ('bucket', '存储桶')], default='vm', max_length=16, verbose_name='资源类型')),
                ('service_id', models.CharField(blank=True, default='', max_length=36, verbose_name='服务ID')),
                ('instance_id', models.CharField(default='', help_text='云主机，硬盘id，存储桶名称', max_length=64, verbose_name='资源实例ID')),
            ],
            options={
                'verbose_name': '支付记录',
                'verbose_name_plural': '支付记录',
                'db_table': 'payment_history',
                'ordering': ['-payment_time'],
            },
        ),
        migrations.CreateModel(
            name='UserPointAccount',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default='0.00', max_digits=10, verbose_name='金额')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '用户账户',
                'verbose_name_plural': '用户账户',
                'db_table': 'user_point_account',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.CreateModel(
            name='VoPointAccount',
            fields=[
                ('id', models.CharField(blank=True, editable=False, max_length=36, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(decimal_places=2, default='0.00', max_digits=10, verbose_name='金额')),
                ('creation_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': 'VO组账户',
                'verbose_name_plural': 'VO组账户',
                'db_table': 'vo_point_account',
                'ordering': ['-creation_time'],
            },
        ),
    ]

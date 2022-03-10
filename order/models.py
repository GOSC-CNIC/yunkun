import random

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.model import UuidModel, OwnerType, PayType


def generate_order_sn():
    """
    生成订单编号
    长22位: 日期+纳秒+2位随机数
    """
    t = timezone.now()
    rand = random.randint(0, 99)
    return f"{t.year:04}{t.month:02}{t.day:02}{t.hour:02}{t.minute:02}{t.second:02}{t.microsecond:06}{rand:02}"


class ResourceType(models.TextChoices):
    VM = 'vm', _('云主机')
    DISK = 'disk', _('云硬盘')
    BUCKET = 'bucket', _('存储桶')


class Order(models.Model):
    OwnerType = OwnerType

    class OrderType(models.TextChoices):
        NEW = 'new', _('新购')
        RENEWAL = 'renewal', _('续费')
        UPGRADE = 'upgrade', _('升级')
        DOWNGRADE = 'downgrade', _('降级')
        REFUND = 'refund', _('退款')

    class Status(models.TextChoices):
        PAID = 'paid', _('已支付')
        UPPAID = 'unpaid', _('未支付')
        CANCELLED = 'cancelled', _('作废')

    id = models.CharField(verbose_name=_('订单编号'), max_length=32, primary_key=True, editable=False)
    order_type = models.CharField(
        verbose_name=_('订单类型'), max_length=16, choices=OrderType.choices, default=OrderType.NEW)
    status = models.CharField(
        verbose_name=_('订单状态'), max_length=16, choices=Status.choices, default=Status.PAID)
    total_amount = models.DecimalField(verbose_name=_('总金额'), max_digits=10, decimal_places=2, default=0.0)
    pay_amount = models.DecimalField(verbose_name=_('实付金额'), max_digits=10, decimal_places=2, default=0.0)

    service_id = models.CharField(verbose_name=_('服务id'), max_length=36, blank=True, default='')
    service_name = models.CharField(verbose_name=_('服务名称'), max_length=255, blank=True, default='')
    resource_type = models.CharField(
        verbose_name=_('资源类型'), max_length=16, choices=ResourceType.choices, default=ResourceType.VM)
    instance_config = models.JSONField(verbose_name=_('资源的规格和配置'), null=False, blank=True, default=dict)
    period = models.IntegerField(verbose_name=_('订购时长(月)'), blank=True, default=0)

    payment_time = models.DateTimeField(verbose_name=_('支付时间'), null=True, blank=True, default=None)
    pay_type = models.CharField(verbose_name=_('付费方式'), max_length=16, choices=PayType.choices)

    creation_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)
    user_id = models.CharField(verbose_name=_('用户ID'), max_length=36, blank=True, default='')
    username = models.CharField(verbose_name=_('用户名'), max_length=64, blank=True, default='')
    vo_id = models.CharField(verbose_name=_('VO组ID'), max_length=36, blank=True, default='')
    vo_name = models.CharField(verbose_name=_('VO组名'), max_length=256, blank=True, default='')
    owner_type = models.CharField(verbose_name=_('所有者类型'), max_length=8, choices=OwnerType.choices)

    class Meta:
        verbose_name = _('订单')
        verbose_name_plural = verbose_name
        db_table = 'order'
        ordering = ['-creation_time']

    def __repr__(self):
        return f'order[{self.id}]'

    @staticmethod
    def generate_order_sn():
        return generate_order_sn()

    def enforce_order_id(self):
        if not self.id:
            self.id = self.generate_order_sn()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.enforce_order_id()
        return super().save(force_insert=force_insert, force_update=force_update,
                            using=using, update_fields=update_fields)


class Resource(UuidModel):
    class InstanceStatus(models.TextChoices):
        WAIT = 'wait', _('待创建')
        SUCCESS = 'success', _('创建成功')
        FAILED = 'failed', _('创建失败')

    order = models.ForeignKey(
        to=Order, on_delete=models.DO_NOTHING, related_name='resource_set', verbose_name=_('订单'))
    resource_type = models.CharField(
        verbose_name=_('资源类型'), max_length=16, choices=ResourceType.choices)
    instance_id = models.CharField(verbose_name=_('资源实例id'), max_length=36, blank=True, default='')
    instance_status = models.CharField(
        verbose_name=_('资源创建结果'), max_length=16, choices=InstanceStatus.choices, default=InstanceStatus.WAIT)
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('订单资源')
        verbose_name_plural = verbose_name
        db_table = 'order_resource'
        ordering = ['-creation_time']

    def __repr__(self):
        return f'Resource([{self.resource_type}]{self.instance_id})'
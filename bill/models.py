from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.model import UuidModel, OwnerType
from utils import rand_utils
from order.models import ResourceType
from users.models import UserProfile
from vo.models import VirtualOrganization
from activity.models import CashCoupon


class BasePointAccount(UuidModel):
    class Status(models.TextChoices):
        NORMAL = 'normal', _('正常')
        FROZEN = 'frozen', _('冻结')

    balance = models.DecimalField(verbose_name=_('金额'), max_digits=10, decimal_places=2, default='0.00')
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)
    # status = models.CharField(
    #     verbose_name=_('状态'), max_length=16, choices=Status.choices, blank=True, default=Status.NORMAL.value)

    class Meta:
        abstract = True


class UserPointAccount(BasePointAccount):
    user = models.OneToOneField(to=UserProfile, on_delete=models.SET_NULL, null=True, default=None)

    class Meta:
        verbose_name = _('用户账户')
        verbose_name_plural = verbose_name
        db_table = 'user_point_account'
        ordering = ['-creation_time']

    def __repr__(self):
        if self.user:
            return f'UserPointAccount[{self.user.username}]<{self.balance}>'

        return f'UserPointAccount<{self.balance}>'


class VoPointAccount(BasePointAccount):
    vo = models.OneToOneField(to=VirtualOrganization, on_delete=models.SET_NULL, null=True, default=None)

    class Meta:
        verbose_name = _('VO组账户')
        verbose_name_plural = verbose_name
        db_table = 'vo_point_account'
        ordering = ['-creation_time']

    def __repr__(self):
        if self.vo:
            return f'VoPointAccount[{self.vo.name}]<{self.balance}>'

        return f'VoPointAccount<{self.balance}>'


class PaymentHistory(UuidModel):
    class Type(models.TextChoices):
        RECHARGE = 'recharge', _('充值')
        PAYMENT = 'payment', _('支付')
        REFUND = 'refund', _('退款')

    class PaymentMethod(models.TextChoices):
        BALANCE = 'balance', _('余额')
        CASH_COUPON = 'coupon', _('代金卷')
        BALANCE_COUPON = 'balance+coupon', _('余额+代金卷')

    payment_account = models.CharField(
        verbose_name=_('付款账户'), max_length=36, blank=True, default='',
        help_text=_('用户或VO余额ID, 及可能支持的其他账户'))
    payment_method = models.CharField(
        verbose_name=_('付款方式'), max_length=16, choices=PaymentMethod.choices, default=PaymentMethod.BALANCE)
    executor = models.CharField(
        verbose_name=_('交易执行人'), max_length=128, blank=True, default='', help_text=_('记录此次支付交易是谁执行完成的'))
    payer_id = models.CharField(verbose_name=_('付款人ID'), max_length=36, blank=True, default='',
                                help_text='user id or vo id')
    payer_name = models.CharField(verbose_name=_('付款人名称'), max_length=255, blank=True, default='',
                                  help_text='username or vo name')
    payer_type = models.CharField(verbose_name=_('付款人类型'), max_length=8, choices=OwnerType.choices)
    amounts = models.DecimalField(verbose_name=_('金额'), max_digits=10, decimal_places=2)
    before_payment = models.DecimalField(verbose_name=_('支付前余额'), max_digits=10, decimal_places=2)
    after_payment = models.DecimalField(verbose_name=_('支付后余额'), max_digits=10, decimal_places=2)
    payment_time = models.DateTimeField(verbose_name=_('支付时间'), auto_now_add=True)
    type = models.CharField(verbose_name=_('支付类型'), max_length=16, choices=Type.choices)
    remark = models.CharField(verbose_name=_('备注信息'), max_length=255, blank=True, default='')

    order_id = models.CharField(verbose_name=_('订单ID'), max_length=36, blank=True, default='')
    resource_type = models.CharField(
        verbose_name=_('资源类型'), max_length=16, choices=ResourceType.choices, default=ResourceType.VM)
    service_id = models.CharField(verbose_name=_('服务ID'), max_length=36, blank=True, default='')
    instance_id = models.CharField(
        verbose_name=_('资源实例ID'), max_length=64, default='', help_text='云主机，硬盘id，存储桶名称')
    coupon_amount = models.DecimalField(
        verbose_name=_('券金额'), max_digits=10, decimal_places=2, help_text=_('代金券或者抵扣金额'), default=Decimal('0'))

    class Meta:
        verbose_name = _('支付记录')
        verbose_name_plural = verbose_name
        db_table = 'payment_history'
        ordering = ['-payment_time']

    def __repr__(self):
        return f'PaymentHistory[{self.id}]<{self.get_type_display()}, {self.amounts}>'

    def enforce_id(self):
        """确保id有效"""
        if not self.id:
            self.id = rand_utils.timestamp20_rand4_sn()

        return self.id


class CashCouponPaymentHistory(UuidModel):
    payment_history = models.ForeignKey(to=PaymentHistory, on_delete=models.SET_NULL, null=True)
    cash_coupon = models.ForeignKey(to=CashCoupon, on_delete=models.SET_NULL, null=True)
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)
    amounts = models.DecimalField(verbose_name=_('金额'), max_digits=10, decimal_places=2)
    before_payment = models.DecimalField(verbose_name=_('支付前余额'), max_digits=10, decimal_places=2)
    after_payment = models.DecimalField(verbose_name=_('支付后余额'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('代金券扣费记录')
        verbose_name_plural = verbose_name
        db_table = 'cash_coupon_payment'
        ordering = ['-creation_time']

    def enforce_id(self):
        """确保id有效"""
        if not self.id:
            self.id = rand_utils.timestamp20_rand4_sn()

        return self.id
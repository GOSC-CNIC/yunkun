from django.db import models
from utils.model import UuidModel
from django.utils.translation import gettext_lazy as _


# Create your models here.

class AlertAbstractModel(UuidModel):
    fingerprint = models.CharField(blank=False, unique=True, db_index=True, max_length=40, verbose_name=_('指纹'))
    name = models.CharField(max_length=100, verbose_name=_('名称'))
    type = models.CharField(max_length=255, verbose_name=_('类型'))
    instance = models.CharField(null=False, default="", db_index=True, max_length=100, verbose_name=_('告警实例'))
    port = models.CharField(null=False, default="", db_index=True, max_length=100, verbose_name=_('告警端口'))
    cluster = models.CharField(db_index=True, max_length=50, verbose_name=_('集群名称'))
    severity = models.CharField(max_length=50, verbose_name=_('级别'))
    summary = models.TextField(null=False, blank=False, verbose_name=_('摘要'))
    description = models.TextField(null=False, blank=False, verbose_name=_('详情'))
    start = models.PositiveBigIntegerField(db_index=True, verbose_name=_('告警开始时间'))
    end = models.PositiveBigIntegerField(null=True, db_index=True, verbose_name=_('告警结束时间'))
    count = models.PositiveBigIntegerField(null=False, default=1, verbose_name=_('累加条数'))
    first_notification = models.PositiveBigIntegerField(null=True, verbose_name=_('首次通知时间'))
    last_notification = models.PositiveBigIntegerField(null=True, verbose_name=_('上次通知时间'))
    creation = models.PositiveBigIntegerField(null=True, verbose_name=_('创建时间'))
    modification = models.PositiveBigIntegerField(null=True, verbose_name=_('更新时间'))

    class Meta:
        abstract = True


class PreAlertModel(AlertAbstractModel):
    """
    需要预处理的告警
    如网站类 多个探针同时告警则判定为告警
    """

    class Meta:
        db_table = "alert_prepare"
        ordering = ['-start']
        verbose_name = _("预处理告警")
        verbose_name_plural = verbose_name


class AlertModel(AlertAbstractModel):
    """
    进行中的告警
    """

    class Meta:
        db_table = "alert_firing"
        ordering = ['-start']
        verbose_name = _("进行中告警")
        verbose_name_plural = verbose_name


class ResolvedAlertModel(AlertAbstractModel):
    """
    已恢复的告警
    """
    fingerprint = models.CharField(blank=False, db_index=True, max_length=40, verbose_name=_('指纹'))

    class Meta:
        db_table = "alert_resolved"
        ordering = ['-start']
        verbose_name = _("已恢复告警")
        verbose_name_plural = verbose_name
        unique_together = (
            ('fingerprint', 'start'),
        )


class AlertLifetimeModel(UuidModel):
    """
    告警的生命周期
    end：最终的结束时间
    PreAlertModel、 AlertModel、ResolvedAlertModel 中的end：预结束时间
    """

    class Status(models.TextChoices):
        FIRING = 'firing', '进行中'
        RESOLVED = 'resolved', '已恢复'
        WORK_ORDER = 'work order', '工单处理'

    status = models.CharField(max_length=20, null=False, choices=Status.choices, verbose_name=_("告警状态"))
    start = models.PositiveBigIntegerField(null=True, db_index=True, verbose_name=_('告警开始时间'))
    end = models.PositiveBigIntegerField(null=True, db_index=True, verbose_name=_('告警结束时间'))

    class Meta:
        db_table = "alert_lifetime"
        ordering = ['-start']
        verbose_name = _("告警生命周期")
        verbose_name_plural = verbose_name


class EmailNotification(UuidModel):
    """
    邮件通知记录
    """
    alert = models.CharField(null=False, db_index=True, max_length=40, verbose_name='告警ID')
    email = models.CharField(null=False, db_index=True, max_length=100, verbose_name='邮箱')
    timestamp = models.PositiveBigIntegerField(db_index=True, verbose_name='通知时间')

    class Meta:
        db_table = "alert_email_notification"
        ordering = ["-timestamp", "email"]
        unique_together = (('alert', 'email', 'timestamp'),)
        verbose_name = _("邮件通知记录")
        verbose_name_plural = verbose_name


class AlertWorkOrder(UuidModel):
    """
    告警工单
    """
    alert = models.OneToOneField(null=False,
                                 to=AlertModel,
                                 unique=True,
                                 on_delete=models.DO_NOTHING,
                                 related_name="work_order",
                                 verbose_name=_('告警'))
    creator = models.ForeignKey(null=False,
                                to="users.UserProfile",
                                on_delete=models.DO_NOTHING,
                                related_name="work_order",
                                verbose_name=_('创建者'))

    class OrderStatus(models.TextChoices):
        IGNORE = '无需处理', _('无需处理')
        FINISHED = '已完成', _('已完成')
        MISREPORT = '误报', _('误报')

    collect = models.CharField(max_length=40, null=False, verbose_name=_("集合ID"))
    status = models.CharField(max_length=10, default=OrderStatus.IGNORE.value, choices=OrderStatus.choices,
                              verbose_name=_("状态"))
    remark = models.TextField(default="", verbose_name=_('备注'))
    creation = models.PositiveBigIntegerField(null=True, verbose_name=_('创建时间'))
    modification = models.PositiveBigIntegerField(null=True, verbose_name=_('更新时间'))

    class Meta:
        db_table = "alert_work_order"
        ordering = ['-creation']
        verbose_name = _("告警工单")
        verbose_name_plural = verbose_name
        unique_together = (
            ('collect', 'alert',),
        )


class AlertMonitorJobServer(UuidModel):
    """
    主机集群监控单元
    """
    name = models.CharField(verbose_name=_('监控的主机集群名称'), max_length=255, default='')
    name_en = models.CharField(verbose_name=_('监控的主机集群英文名称'), max_length=255, default='')
    job_tag = models.CharField(
        verbose_name=_('主机集群标签名称'), max_length=255, default='', help_text=_('模板：xxx_node_metric'))
    prometheus = models.CharField(
        verbose_name=_('Prometheus接口'), max_length=255, blank=True, default='', help_text=_('http(s)://example.cn/'))
    creation = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)
    remark = models.TextField(verbose_name=_('备注'), blank=True, default='')
    users = models.ManyToManyField(
        to="users.UserProfile",
        db_table='alert_server_users',
        related_name='+',
        db_constraint=False,
        verbose_name=_('管理用户'),
        blank=True)
    sort_weight = models.IntegerField(verbose_name=_('排序值'), default=0, help_text=_('值越小排序越靠前'))
    grafana_url = models.CharField(verbose_name=_('Grafana连接'), max_length=255, blank=True, default='')
    dashboard_url = models.CharField(verbose_name=_('Dashboard连接'), max_length=255, blank=True, default='')

    def __str__(self):
        return self.name

    class Meta:
        db_table = "alert_monitorjobserver"
        ordering = ['-creation']
        verbose_name = _("告警集群")
        verbose_name_plural = verbose_name

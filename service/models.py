from django.db import models
from django.db import transaction
from django.utils.translation import gettext, gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

from utils.model import UuidModel, get_encryptor
from utils.validators import http_url_validator
from vo.models import VirtualOrganization

from users.models import UserProfile as User


app_name = 'service'


class Contacts(UuidModel):
    """机构联系人"""
    name = models.CharField(verbose_name=_('姓名'), max_length=128)
    telephone = models.CharField(verbose_name=_('电话'), max_length=11, default='')
    email = models.EmailField(_('邮箱地址'), blank=True, default='')
    address = models.CharField(verbose_name=_('联系地址'), max_length=255, help_text=_('详细的联系地址'))
    creation_time = models.DateTimeField(verbose_name=_('创建时间'))
    update_time = models.DateTimeField(verbose_name=_('更新时间'))
    remarks = models.CharField(max_length=255, default='', blank=True, verbose_name=_('备注'))

    class Meta:
        ordering = ('-creation_time',)
        db_table = 'contacts'
        verbose_name = _('机构联系人')
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'[ {self.name} ] Phone: {self.telephone}, Email: {self.email}, Address: {self.address}'


class DataCenter(UuidModel):
    STATUS_ENABLE = 1
    STATUS_DISABLE = 2
    CHOICE_STATUS = (
        (STATUS_ENABLE, _('开启状态')),
        (STATUS_DISABLE, _('关闭状态'))
    )

    name = models.CharField(verbose_name=_('名称'), max_length=255)
    name_en = models.CharField(verbose_name=_('英文名称'), max_length=255, default='')
    abbreviation = models.CharField(verbose_name=_('简称'), max_length=64, default='')
    independent_legal_person = models.BooleanField(verbose_name=_('独立法人单位'), default=True)
    country = models.CharField(verbose_name=_('国家/地区'), max_length=128, default='')
    province = models.CharField(verbose_name=_('省份'), max_length=128, default='')
    city = models.CharField(verbose_name=_('城市'), max_length=128, default='')
    postal_code = models.CharField(verbose_name=_('邮政编码'), max_length=32, default='')
    address = models.CharField(verbose_name=_('单位地址'), max_length=256, default='')
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), null=True, blank=True, default=None)
    status = models.SmallIntegerField(verbose_name=_('服务状态'), choices=CHOICE_STATUS, default=STATUS_ENABLE)
    desc = models.CharField(verbose_name=_('描述'), blank=True, max_length=255)

    logo_url = models.CharField(verbose_name=_('LOGO url'), max_length=256,
                                blank=True, default='')
    certification_url = models.CharField(verbose_name=_('机构认证代码url'), max_length=256,
                                         blank=True, default='')
    longitude = models.FloatField(verbose_name=_('经度'), blank=True, default=0)
    latitude = models.FloatField(verbose_name=_('纬度'), blank=True, default=0)
    sort_weight = models.IntegerField(verbose_name=_('排序值'), default=0, help_text=_('值越小排序越靠前'))
    contacts = models.ManyToManyField(
        verbose_name=_('机构联系人'), to=Contacts, related_name='+', db_table='data_center_contacts',
        db_constraint=False, blank=True
    )

    class Meta:
        ordering = ['sort_weight']
        verbose_name = _('机构')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.creation_time:
            self.creation_time = timezone.now()
            if update_fields and 'creation_time' not in update_fields:
                update_fields.append('creation_time')

        super(DataCenter, self).save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class OrgDataCenter(UuidModel):
    """机构下的数据中心"""
    name = models.CharField(verbose_name=_('名称'), max_length=255)
    name_en = models.CharField(verbose_name=_('英文名称'), max_length=255, default='')
    organization = models.ForeignKey(
        to=DataCenter, verbose_name=_('机构'), on_delete=models.SET_NULL, null=True, blank=False, db_constraint=False)
    users = models.ManyToManyField(
        to=User, verbose_name=_('管理员'), blank=True, related_name='+', db_table='org_data_center_users',
        db_constraint=False)
    longitude = models.FloatField(verbose_name=_('经度'), blank=True, default=0)
    latitude = models.FloatField(verbose_name=_('纬度'), blank=True, default=0)
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)
    sort_weight = models.IntegerField(verbose_name=_('排序值'), default=0, help_text=_('值越小排序越靠前'))
    remark = models.TextField(verbose_name=_('数据中心备注'), max_length=10000, blank=True, default='')

    # 指标数据服务
    thanos_endpoint_url = models.CharField(
        verbose_name=_('指标监控系统查询接口'), max_length=255, blank=True, default='', help_text=_('http(s)://example.cn/'))
    thanos_username = models.CharField(
        max_length=128, verbose_name=_('指标监控系统认证用户名'), blank=True, default='', help_text=_('用于此服务认证的用户名'))
    thanos_password = models.CharField(max_length=255, verbose_name=_('指标监控系统认证密码'), blank=True, default='')
    thanos_receive_url = models.CharField(
        verbose_name=_('指标监控系统接收接口'), max_length=255, blank=True, default='', help_text=_('http(s)://example.cn/'))
    thanos_remark = models.CharField(verbose_name=_('指标监控系统备注'), max_length=255, blank=True, default='')
    metric_monitor_url = models.CharField(
        verbose_name=_('指标监控系统监控网址'), max_length=255, blank=True, default='',
        help_text=_('如果填写有效网址会自动创建对应的站点监控任务，格式为 http(s)://example.cn/'))
    metric_task_id = models.CharField(
        verbose_name=_('指标监控系统监控任务ID'), max_length=36, blank=True, default='', editable=False,
        help_text=_('记录为指标监控系统监控地址创建的站点监控任务的ID'))

    # 日志服务
    loki_endpoint_url = models.CharField(
        verbose_name=_('日志聚合系统查询接口'), max_length=255, blank=True, default='', help_text=_('http(s)://example.cn/'))
    loki_username = models.CharField(
        max_length=128, verbose_name=_('日志聚合系统认证用户名'), blank=True, default='', help_text=_('用于此服务认证的用户名'))
    loki_password = models.CharField(max_length=255, verbose_name=_('日志聚合系统认证密码'), blank=True, default='')
    loki_receive_url = models.CharField(
        verbose_name=_('日志聚合系统接收接口'), max_length=255, blank=True, default='', help_text=_('http(s)://example.cn/'))
    loki_remark = models.CharField(verbose_name=_('日志聚合系统备注'), max_length=255, blank=True, default='')
    log_monitor_url = models.CharField(
        verbose_name=_('日志聚合系统监控网址'), max_length=255, blank=True, default='',
        help_text=_('如果填写有效网址会自动创建对应的站点监控任务，格式为 http(s)://example.cn/'))
    log_task_id = models.CharField(
        verbose_name=_('日志聚合系统监控任务ID'), max_length=36, blank=True, default='', editable=False,
        help_text=_('记录为日志聚合系统监控网址创建的站点监控任务的ID'))

    class Meta:
        db_table = 'org_data_center'
        ordering = ['sort_weight']
        verbose_name = _('机构数据中心')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def clean(self):
        if self.thanos_endpoint_url:
            try:
                http_url_validator(self.thanos_endpoint_url)
            except ValidationError:
                raise ValidationError(message={'thanos_endpoint_url': gettext('不是一个有效的网址')})

        if self.metric_monitor_url:
            try:
                http_url_validator(self.metric_monitor_url)
            except ValidationError:
                raise ValidationError(message={'metric_monitor_url': gettext('不是一个有效的网址')})

        if self.loki_endpoint_url:
            try:
                http_url_validator(self.loki_endpoint_url)
            except ValidationError:
                raise ValidationError(message={'loki_endpoint_url': gettext('不是一个有效的网址')})

        if self.log_monitor_url:
            try:
                http_url_validator(self.log_monitor_url)
            except ValidationError:
                raise ValidationError(message={'log_monitor_url': gettext('不是一个有效的网址')})

    @property
    def raw_thanos_password(self):
        """
        :return:
            str     # success
            None    # failed, invalid encrypted password
        """
        encryptor = get_encryptor()
        try:
            return encryptor.decrypt(self.thanos_password)
        except encryptor.InvalidEncrypted as e:
            return None

    @raw_thanos_password.setter
    def raw_thanos_password(self, raw_password: str):
        encryptor = get_encryptor()
        self.thanos_password = encryptor.encrypt(raw_password)

    @property
    def raw_loki_password(self):
        """
        :return:
            str     # success
            None    # failed, invalid encrypted password
        """
        encryptor = get_encryptor()
        try:
            return encryptor.decrypt(self.loki_password)
        except encryptor.InvalidEncrypted as e:
            return None

    @raw_loki_password.setter
    def raw_loki_password(self, raw_password: str):
        encryptor = get_encryptor()
        self.loki_password = encryptor.encrypt(raw_password)


class ApplyOrganization(UuidModel):
    """
    数据中心/机构申请
    """
    class Status(models.TextChoices):
        WAIT = 'wait', '待审批'
        CANCEL = 'cancel', _('取消申请')
        PENDING = 'pending', '审批中'
        REJECT = 'reject', '拒绝'
        PASS = 'pass', '通过'

    name = models.CharField(verbose_name=_('名称'), max_length=255)
    name_en = models.CharField(verbose_name=_('英文名称'), max_length=255, default='')
    abbreviation = models.CharField(verbose_name=_('简称'), max_length=64, default='')
    independent_legal_person = models.BooleanField(verbose_name=_('是否独立法人单位'), default=True)
    country = models.CharField(verbose_name=_('国家/地区'), max_length=128, default='')
    city = models.CharField(verbose_name=_('城市'), max_length=128, default='')
    postal_code = models.CharField(verbose_name=_('邮政编码'), max_length=32, default='')
    address = models.CharField(verbose_name=_('单位地址'), max_length=256, default='')

    endpoint_vms = models.CharField(max_length=255, verbose_name=_('云主机服务地址url'),
                                    null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_object = models.CharField(max_length=255, verbose_name=_('存储服务地址url'),
                                       null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_compute = models.CharField(max_length=255, verbose_name=_('计算服务地址url'),
                                        null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    endpoint_monitor = models.CharField(max_length=255, verbose_name=_('检测报警服务地址url'),
                                        null=True, blank=True, default=None, help_text='http(s)://{hostname}:{port}/')
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), null=True, blank=True, auto_now_add=True)
    status = models.CharField(verbose_name=_('状态'), max_length=16,
                              choices=Status.choices, default=Status.WAIT)
    desc = models.CharField(verbose_name=_('描述'), blank=True, max_length=255)
    data_center = models.OneToOneField(to=DataCenter, null=True, on_delete=models.SET_NULL,
                                       related_name='apply_data_center', blank=True,
                                       default=None, verbose_name=_('机构'),
                                       help_text=_('机构加入申请审批通过后对应的机构'))

    logo_url = models.CharField(verbose_name=_('LOGO url'), max_length=256,
                                blank=True, default='')
    certification_url = models.CharField(verbose_name=_('机构认证代码url'), max_length=256,
                                         blank=True, default='')

    user = models.ForeignKey(verbose_name=_('申请用户'), to=User, null=True, on_delete=models.SET_NULL)
    deleted = models.BooleanField(verbose_name=_('删除'), default=False)
    longitude = models.FloatField(verbose_name=_('经度'), blank=True, default=0)
    latitude = models.FloatField(verbose_name=_('纬度'), blank=True, default=0)

    class Meta:
        db_table = 'organization_apply'
        ordering = ['creation_time']
        verbose_name = _('机构加入申请')
        verbose_name_plural = verbose_name

    def is_pass(self):
        return self.status == self.Status.PASS

    def __str__(self):
        return self.name

    def do_pass_apply(self) -> DataCenter:
        organization = DataCenter()
        organization.name = self.name
        organization.name_en = self.name_en
        organization.abbreviation = self.abbreviation
        organization.independent_legal_person = self.independent_legal_person
        organization.country = self.country
        organization.city = self.city
        organization.postal_code = self.postal_code
        organization.address = self.address
        organization.endpoint_vms = self.endpoint_vms
        organization.endpoint_object = self.endpoint_object
        organization.endpoint_compute = self.endpoint_compute
        organization.endpoint_monitor = self.endpoint_monitor
        organization.desc = self.desc
        organization.logo_url = self.logo_url
        organization.certification_url = self.certification_url
        organization.longitude = self.longitude
        organization.latitude = self.latitude

        with transaction.atomic():
            organization.save()
            self.status = self.Status.PASS
            self.data_center = organization
            self.save(update_fields=['status', 'data_center'])

        return organization

from django.db import models
from django.utils.translation import gettext, gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone as dj_timezone

from core import errors
from utils.model import UuidModel
from users.models import UserProfile
from service.models import DataCenter


class NetBoxUserRole(UuidModel):
    """用户角色和权限"""
    user = models.OneToOneField(
        verbose_name=_('用户'), to=UserProfile, related_name='+', on_delete=models.CASCADE)
    is_ipam_admin = models.BooleanField(
        verbose_name=_('IP管理员'), default=False, help_text=_('选中，用户拥有IP管理功能的管理员权限'))
    is_ipam_readonly = models.BooleanField(
        verbose_name=_('IP管理全局只读权限'), default=False, help_text=_('选中，用户拥有科技网IP管理功能的全局只读权限'))
    organizations = models.ManyToManyField(
        verbose_name=_('拥有IP管理员权限的机构'), to=DataCenter, related_name='+', db_table='netbox_user_role_orgs', blank=True)
    is_link_admin = models.BooleanField(
        verbose_name=_('链路管理员'), default=False, help_text=_('选中，用户拥有链路管理功能的管理员权限'))
    is_link_readonly = models.BooleanField(
        verbose_name=_('链路管理全局只读权限'), default=False, help_text=_('选中，用户拥有链路管理功能的全局只读权限'))

    creation_time = models.DateTimeField(verbose_name=_('创建时间'))
    update_time = models.DateTimeField(verbose_name=_('更新时间'))

    class Meta:
        ordering = ('-creation_time',)
        db_table = 'netbox_user_role'
        verbose_name = _('01_网络管理用户角色和权限')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class ContactPerson(UuidModel):
    """机构二级联系人"""
    name = models.CharField(verbose_name=_('姓名'), max_length=128)
    telephone = models.CharField(verbose_name=_('电话'), max_length=16, default='')
    email = models.EmailField(_('邮箱地址'), blank=True, default='')
    address = models.CharField(verbose_name=_('联系地址'), max_length=255, blank=True, default='',
                               help_text=_('详细的联系地址'))
    creation_time = models.DateTimeField(verbose_name=_('创建时间'), blank=True)
    update_time = models.DateTimeField(verbose_name=_('更新时间'), blank=True)
    remarks = models.CharField(max_length=255, default='', blank=True, verbose_name=_('备注'))

    class Meta:
        ordering = ('-creation_time',)
        db_table = 'netbox_contact_person'
        verbose_name = _('03_机构二级对象联系人')
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'[ {self.name} ] Phone: {self.telephone}, Email: {self.email}, Address: {self.address}'

    def clean(self):
        qs = ContactPerson.objects.filter(name=self.name, telephone=self.telephone)
        if self.id:
            qs = qs.exclude(id=self.id)
        if qs.exists():
            msg = gettext('已存在姓名和手机号都相同的联系人')
            exc = ValidationError(message={'name': msg})
            exc.error = errors.TargetAlreadyExists(message=msg)
            raise exc

        if not self.creation_time:
            self.creation_time = dj_timezone.now()

        if not self.update_time:
            self.update_time = self.creation_time


class OrgVirtualObject(UuidModel):
    name = models.CharField(verbose_name=_('名称'), max_length=255)
    organization = models.ForeignKey(
        verbose_name=_('机构'), to=DataCenter, related_name='+',
        on_delete=models.SET_NULL, null=True, blank=True, default=None)
    creation_time = models.DateTimeField(verbose_name=_('创建时间'))
    remark = models.CharField(verbose_name=_('备注信息'), max_length=255, blank=True, default='')
    contacts = models.ManyToManyField(
        verbose_name=_('机构二级对象联系人'), to=ContactPerson, related_name='+', db_table='netbox_org_obj_contacts',
        db_constraint=False, blank=True
    )

    class Meta:
        ordering = ('-creation_time',)
        db_table = 'netbox_org_virt_obj'
        verbose_name = _('02_机构二级')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def clean(self):
        qs = OrgVirtualObject.objects.filter(organization_id=self.organization_id, name=self.name)
        if self.id:
            qs = qs.exclude(id=self.id)
        if qs.exists():
            raise ValidationError(message=gettext('同名的机构二级对象已存在'), code=errors.TargetAlreadyExists().code)

        if self.creation_time is None:
            self.creation_time = dj_timezone.now()

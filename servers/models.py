from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class ServiceConfig(models.Model):
    """
    资源服务接入配置
    """
    SERVICE_EVCLOUD = 0
    SERVICE_OPENSTACK = 1
    SERVICE_TYPE_CHOICES = (
        (SERVICE_EVCLOUD, 'EVCloud'),
        (SERVICE_OPENSTACK, 'OpenStack'),
    )

    id = models.AutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name=_('服务名称'))
    region_id = models.CharField(max_length=128, default='', blank=True, verbose_name=_('服务区域/分中心ID'))
    service_type = models.SmallIntegerField(choices=SERVICE_TYPE_CHOICES, default=SERVICE_EVCLOUD, verbose_name=_('服务平台类型'))
    endpoint_url = models.CharField(max_length=300, verbose_name=_('服务地址url'), help_text='http(s)://{hostname}:{port}/')
    api_version = models.CharField(max_length=64, default='v3', verbose_name=_('API版本'), help_text=_('预留，主要EVCloud使用'))
    username = models.CharField(max_length=128, verbose_name=_('用户名'), help_text=_('用于此服务认证的用户名'))
    password = models.CharField(max_length=128, verbose_name=_('密码'))
    add_time = models.DateTimeField(auto_now_add=True, verbose_name=_('添加时间'))
    active = models.BooleanField(default=True, verbose_name=_('可用状态'), help_text=_('指示此配置是否可用'))
    remarks = models.CharField(max_length=255, default='', blank=True, verbose_name=_('备注'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('服务接入配置')
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Server(models.Model):
    """
    虚拟服务器实例
    """
    id = models.AutoField(primary_key=True, verbose_name='ID')
    service = models.ForeignKey(to=ServiceConfig, null=True, on_delete=models.SET_NULL, related_name='server_set', verbose_name=_('接入的服务配置'))
    name = models.CharField(max_length=255, verbose_name=_('服务器实例名称'))
    instance_id = models.CharField(max_length=128, verbose_name=_('虚拟主机ID'), help_text=_('各接入服务中虚拟主机的ID'))
    flavor_id = models.CharField(max_length=128, verbose_name=_('硬件配置类型ID'), help_text=_('cpu数、内存大小等硬件配置'))
    vcpus = models.IntegerField(verbose_name=_('虚拟CPU数'), default=0)
    ram = models.IntegerField(verbose_name=_('内存MB'), default=0)
    ipv4 = models.CharField(max_length=128, verbose_name='IPV4', default='')
    image_id = models.CharField(max_length=128, verbose_name='镜像ID', default='')
    image = models.CharField(max_length=255, verbose_name='镜像系统名称', default='')
    creation_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    remarks = models.CharField(max_length=255, default='', verbose_name='备注')
    user = models.ForeignKey(to=User, verbose_name='创建者', on_delete=models.SET_NULL, related_name='user_vms', null=True)
    deleted = models.BooleanField(default=False, editable=False, verbose_name=_('删除'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('虚拟服务器')
        verbose_name_plural = verbose_name

    def user_has_perms(self, user):
        """
        用户是否有访问此宿主机的权限

        :param user: 用户
        :return:
            True    # has
            False   # no
        """
        if not isinstance(user.id, int):    # 未认证用户
            return False

        if user.is_superuser:
            return True

        if self.user_id == user.id:
            return True

        return False

    def do_soft_delete(self):
        """
        :return: True or False
        """
        try:
            self.deleted = True
            self.save(update_fields=['deleted'])
        except Exception as e:
            return False

        return True
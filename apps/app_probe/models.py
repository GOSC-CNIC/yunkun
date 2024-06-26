from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.


class ProbeMonitorWebsite(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=_('ID'))
    is_tamper_resistant = models.BooleanField(verbose_name=_('防篡改'), default=False)
    url = models.CharField(verbose_name=_('要监控的网址'), max_length=2048, default='')
    url_hash = models.CharField(verbose_name=_('网址hash值'), unique=True, max_length=64, default='')
    creation = models.DateTimeField(verbose_name=_('创建时间'), auto_now_add=True)

    class Meta:
        db_table = 'app_probe_monitor_website'
        ordering = ['-creation']
        verbose_name = _('探针任务')
        verbose_name_plural = verbose_name


class ProbeDetails(models.Model):

    INSTANCE_ID = 1
    id = models.AutoField(primary_key=True, verbose_name=_('ID'), default=INSTANCE_ID)
    probe_name = models.CharField(verbose_name=_('探针服务名称'), max_length=255, default=None)
    version = models.IntegerField(verbose_name=_('版本号'), default=0, blank=True)

    class Meta:
        db_table = 'app_probe_details'
        verbose_name = _('探针信息')
        verbose_name_plural = verbose_name

    @classmethod
    def get_instance(cls):
        inst = cls.objects.filter(id=cls.INSTANCE_ID).first()
        if not inst:
            return None

        return inst

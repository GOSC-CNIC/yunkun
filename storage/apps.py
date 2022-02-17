from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StorageConfig(AppConfig):
    name = 'storage'
    verbose_name = _('存储')

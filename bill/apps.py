from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BillConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bill'
    verbose_name = _('账单')

from django.contrib import admin
from apps.app_alert.models import AlertWhiteListModel
from apps.app_alert.models import AlertMonitorJobServer
from utils.model import BaseModelAdmin


# Register your models here.
@admin.register(AlertWhiteListModel)
class MenuCategoryAdmin(BaseModelAdmin):
    list_display = [
        'id',
        'remark',
        'creation',
        'modification', ]
    list_display_links = (
        'id',
        'remark',
        'creation',
        'modification',)


@admin.register(AlertMonitorJobServer)
class AlertMonitorJobServerAdmin(BaseModelAdmin):
    list_display = [
        'id',
        'name',
        'sort_weight',
        'remark', ]
    list_display_links = (
        'id',
        'name',
        'sort_weight',
        'remark',)

    filter_horizontal = (
        "users",
    )

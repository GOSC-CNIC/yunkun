from django.utils.translation import gettext_lazy, gettext as _
from django.db.models import Max
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.app_screenvis.utils import errors
from apps.app_screenvis.models import DataCenter, ServerService, ServerServiceTimedStats
from apps.app_screenvis import serializers
from apps.app_screenvis.permissions import ScreenAPIIPPermission
from . import NormalGenericViewSet


class ServerServiceViewSet(NormalGenericViewSet):
    queryset = []
    permission_classes = [ScreenAPIIPPermission]
    pagination_class = None
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary=gettext_lazy('查询一个数据中心下各云主机服务单元总的统计数据'),
        responses={
            200: ''''''
        }
    )
    @action(methods=['GET'], detail=False, url_path=r'dc/(?P<dc_id>[^/]+)', url_name='dc')
    def odc_units(self, request, *args, **kwargs):
        """
        查询一个数据中心下各服务单元总的统计数据

            http code 200:
            {
              "server_count": 44,
              "disk_count": 46,
              "ip_count": 136,
              "ip_used_count": 26,
              "mem_size": 44260,        # GiB
              "mem_used_size": 4460,    # GiB
              "cpu_count": 45040,
              "cpu_used_count": 480
            }
        """
        unit_ids = ServerService.objects.filter(
            data_center_id=kwargs['dc_id'],
            status__in=[ServerService.Status.ENABLE.value, ServerService.Status.DISABLE.value]
        ).values_list('id', flat=True)
        if not unit_ids:
            return self.exception_response(
                errors.TargetNotExist(message=_('数据中心不存在，或者数据中心下没有云主机服务单元')))

        obj_list = []
        for unit_id in set(unit_ids):
            obj = ServerServiceTimedStats.objects.filter(service_id=unit_id).order_by('-timestamp').first()
            if obj:
                obj_list.append(obj)

        server_count = 0
        disk_count = 0
        ip_count = 0
        ip_used_count = 0
        mem_size = 0
        mem_used_size = 0
        cpu_count = 0
        cpu_used_count = 0
        for obj in obj_list:
            obj: ServerServiceTimedStats
            server_count = server_count + obj.server_count
            disk_count = disk_count + obj.disk_count
            ip_count = ip_count + obj.ip_count
            ip_used_count = ip_used_count + obj.ip_used_count
            mem_size = mem_size + obj.mem_size
            mem_used_size = mem_used_size + obj.mem_used_size
            cpu_count = cpu_count + obj.cpu_count
            cpu_used_count = cpu_used_count + obj.cpu_used_count

        return Response(data={
            'server_count': server_count,
            'disk_count': disk_count,
            'ip_count': ip_count,
            'ip_used_count': ip_used_count,
            'mem_size': mem_size,
            'mem_used_size': mem_used_size,
            'cpu_count': cpu_count,
            'cpu_used_count': cpu_used_count
        })

    def get_serializer_class(self):
        return Serializer

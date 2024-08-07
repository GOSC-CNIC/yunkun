from django.utils.translation import gettext_lazy
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.app_screenvis.models import MetricMonitorUnit, ScreenConfig
from apps.app_screenvis import serializers
from apps.app_screenvis.permissions import ScreenAPIIPPermission
from apps.app_screenvis.configs_manager import screen_configs
from . import NormalGenericViewSet


class DataCenterViewSet(NormalGenericViewSet):
    queryset = []
    permission_classes = [ScreenAPIIPPermission]
    pagination_class = None
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary=gettext_lazy('查询数据中心下的各指标单元信息'),
        responses={
            200: ''''''
        }
    )
    @action(methods=['GET'], detail=False, url_path='units', url_name='units')
    def list_dc_units(self, request, *args, **kwargs):
        """
        查询数据中心下的各指标单元信息

            http code 200:
            {
                "metric_units": [
                    {
                        "id": "37",
                        "name": "ceph1 name",
                        "name_en": "ceph1 name en",
                        "unit_type": "ceph",        # host, ceph, tidb, vm
                        "job_tag": "ceph1_metric",
                        "creation_time": "2024-03-11T15:02:46.002211+08:00",
                        "remark": "",
                        "sort_weight": 0,
                        "grafana_url": "",
                        "dashboard_url": ""
                    }
                ]
            }
        """
        return self.list_dc_units_response()

    @staticmethod
    def list_dc_units_response():
        # monitor server单元
        metric_units = MetricMonitorUnit.objects.all()
        metric_units_data = serializers.MetricMntrUnitSerializer(metric_units, many=True).data
        return Response(data={
            'metric_units': metric_units_data,
            'log_units': []
        })

    def get_serializer_class(self):
        return Serializer


class ConfigsViewSet(NormalGenericViewSet):
    queryset = []
    permission_classes = [ScreenAPIIPPermission]
    pagination_class = None
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary=gettext_lazy('列举大屏展示配置信息'),
        responses={
            200: ''
        }
    )
    def list(self, request, *args, **kwargs):
        """
        列举大屏展示配置信息

            Http Code 200:
            {
                "org_name": "机构名称",
                "org_name_en": "机构英文名称"
            }
        """
        return_configs = [
            ScreenConfig.ConfigName.ORG_NAME.value, ScreenConfig.ConfigName.ORG_NAME_EN.value
        ]
        data = {key: screen_configs.get(key) for key in return_configs}
        return Response(data=data, status=200)

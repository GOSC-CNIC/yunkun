from django.utils.translation import gettext_lazy, gettext as _
from rest_framework.decorators import action
from rest_framework.serializers import Serializer
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from apps.app_screenvis.utils import errors
from apps.app_screenvis.models import DataCenter, MetricMonitorUnit, LogMonitorUnit, ScreenConfig
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
        operation_summary=gettext_lazy('列举数据中心'),
        responses={
            200: ''
        }
    )
    def list(self, request, *args, **kwargs):
        """
        列举数据中心

            Http Code 200:
            {
                "results": [
                    {
                        "id": 32,
                        "creation_time": "2024-03-11T15:02:45.980022+08:00",
                        "update_time": "2024-03-11T15:02:45.980022+08:00",
                        "name": "name1",
                        "name_en": "name1_en",
                        "longitude": 0.0,
                        "latitude": 0.0,
                        "sort_weight": 0,
                        "remark": ""
                    }
                ]
            }
        """
        qs = DataCenter.objects.all()
        dcs = serializers.DataCenterSerializer(qs, many=True).data
        return Response(data={'results': dcs}, status=200)

    @swagger_auto_schema(
        operation_summary=gettext_lazy('查询一个数据中心下关联的各服务单元信息'),
        responses={
            200: ''''''
        }
    )
    @action(methods=['GET'], detail=True, url_path='units', url_name='units')
    def odc_units(self, request, *args, **kwargs):
        """
        查询一个数据中心下关联的各服务单元信息

            http code 200:
            {
                "data_center": {
                    "id": 34,
                    "creation_time": "2024-03-11T15:02:46.001436+08:00",
                    "update_time": "2024-03-11T15:02:46.001436+08:00",
                    "name": "name1",
                    "name_en": "name1_en",
                    "longitude": 0.0,
                    "latitude": 0.0,
                    "sort_weight": 0,
                    "remark": ""
                },
                "metric_units": [
                    {
                        "id": "37",
                        "name": "ceph1 name",
                        "name_en": "ceph1 name en",
                        "unit_type": "ceph",        # host, ceph, tidb
                        "job_tag": "ceph1_metric",
                        "creation_time": "2024-03-11T15:02:46.002211+08:00",
                        "remark": "",
                        "sort_weight": 0,
                        "grafana_url": "",
                        "dashboard_url": "",
                        "data_center": {
                            "id": 34,
                            "name": "name1",
                            "name_en": "name1_en",
                            "sort_weight": 0
                        }
                    }
                ],
                "log_units": [
                    {
                        "id": 11,
                        "creation_time": "2024-03-11T15:02:46.005009+08:00",
                        "update_time": "2024-03-11T15:02:46.005009+08:00",
                        "name": "log1 name",
                        "name_en": "log1 name en",
                        "log_type": "nat",          # http, nat
                        "job_tag": "log1_metric",
                        "sort_weight": 0,
                        "remark": "",
                        "data_center": {
                            "id": 34,
                            "name": "name1",
                            "name_en": "name1_en",
                            "sort_weight": 0
                        }
                    }
                ]
            }
        """
        odc = DataCenter.objects.filter(id=kwargs[self.lookup_field]).first()
        if odc is None:
            return self.exception_response(
                errors.TargetNotExist(message=_('数据中心不存在')))

        # monitor server单元
        metric_units = []
        for u in MetricMonitorUnit.objects.filter(data_center_id=odc.id):
            u.data_center = odc
            metric_units.append(u)

        # 日志单元
        log_units = []
        for u in LogMonitorUnit.objects.filter(data_center_id=odc.id):
            u.data_center = odc
            log_units.append(u)

        odc_data = serializers.DataCenterSerializer(instance=odc).data
        metric_units_data = serializers.MetricMntrUnitSerializer(metric_units, many=True).data
        log_units_data = serializers.LogMntrUnitSimpleSerializer(log_units, many=True).data
        return Response(data={
            'data_center': odc_data,
            'metric_units': metric_units_data,
            'log_units': log_units_data
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
            200: f'config names: {ScreenConfig.ConfigName.choices}'
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

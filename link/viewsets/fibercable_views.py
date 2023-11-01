from api.viewsets import NormalGenericViewSet
from django.utils.translation import gettext_lazy, gettext as _
from api.paginations import NewPageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from link.handlers.fibercable_handler import FiberCableHandler
from link.serializers.fibercable_serializer import FiberCableSerializer
from drf_yasg import openapi
from rest_framework.decorators import action


class FiberCableViewSet(NormalGenericViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = NewPageNumberPagination
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_summary=gettext_lazy('创建光缆'),
        responses={
            200: ''
        }
    )
    def create(self, request, *args, **kwargs):
        """
        创建光缆

            http Code 200 Ok:
                {
                    "id": "k9rkav5ffd8jnijbpk8yjiegc",
                    "number": "sm-test",
                    "fiber_count": 10,
                    "length": "10.60",
                    "endpoint_1": "微生物所",
                    "endpoint_2": "软件园",
                    "remarks": ""
                }

        """
        return FiberCableHandler.creat_fibercable(view=self, request=request)

    @swagger_auto_schema(
        operation_summary=gettext_lazy('列举光缆'),
        manual_parameters=[
            openapi.Parameter(
                name='search',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
                description='过滤条件，关键词模糊查询（光缆编号、端点1、端点2、备注）'
            ),
        ],
        responses={
            200: ''
        }
    )
    def list(self, request, *args, **kwargs):
        """
        列举光缆信息

            http Code 200 Ok:
                {
                    "count": 141,
                    "page_num": 8,
                    "page_size": 20,
                    "results": [
                        {
                            "id": "k9rkav5ffd8jnijbpk8yjiegc",
                            "number": "sm-test",
                            "fiber_count": 10,
                            "length": "10.60",
                            "endpoint_1": "微生物所",
                            "endpoint_2": "软件园",
                            "remarks": ""
                        }
                    ]
                }

        """
        return FiberCableHandler.list_fibercable(view=self, request=request)

    # @swagger_auto_schema(
    #     operation_summary=gettext_lazy('列举光缆的光纤详情'),
    #     responses={
    #         200: ''
    #     }
    # )
    # @action(methods=['get'], detail=True, url_path='opticalfiber', url_name='list-opticalfiber')
    # def list_opticalfiber(self, request, *args, **kwargs):
    #     """
    #     列举光缆的光纤信息

    #         http Code 200 Ok:
    #             {
    #                 "count": 2,
    #                 "page_num": 1,
    #                 "page_size": 20,
    #                 "results": [
    #                     {
    #                         "is_linked": false,
    #                         "id": "k9rzvhvs77b6qbny7qivdmc9x",
    #                         "sequence": 1
    #                     },
    #                     {
    #                         "is_linked": false,
    #                         "id": "k9tb77x4301025oooh0ur0bv7",
    #                         "sequence": 2
    #                     }
    #                 ]
    #             }

    #     """

    #     return FiberCableHandler.list_opticalfiber(view=self, request=request, kwargs=kwargs)

    def get_serializer_class(self):
        return FiberCableSerializer

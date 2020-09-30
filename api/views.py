from django.utils.translation import gettext_lazy, gettext as _
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import Serializer
from drf_yasg.utils import swagger_auto_schema, no_body
from drf_yasg import openapi

from servers.models import Server, Flavor
from adapters import inputs, outputs
from . import exceptions
from . import serializers
from .viewsets import CustomGenericViewSet, str_to_int_or_default


def serializer_error_msg(errors, default=''):
    """
    获取一个错误信息

    :param errors: serializer.errors
    :param default:
    :return:
        str
    """
    msg = default
    try:
        if isinstance(errors, list):
            for err in errors:
                msg = str(err)
                break
        elif isinstance(errors, dict):
            for key in errors:
                val = errors[key]
                msg = f'{key}, {str(val[0])}'
                break
    except:
        pass

    return msg


class ServersViewSet(CustomGenericViewSet):
    """
    虚拟服务器实例视图
    """
    permission_classes = [IsAuthenticated, ]
    pagination_class = LimitOffsetPagination
    lookup_field = 'id'
    # lookup_value_regex = '[0-9a-z-]+'

    # @swagger_auto_schema(
    #     operation_summary=gettext_lazy('服务器列表'),
    # )
    # def list(self, request, *args, **kwargs):
    #     servers_qs = Server.objects.filter(user=request.user, deleted=False).all()

    @swagger_auto_schema(
        operation_summary=gettext_lazy('创建服务器实例'),
        manual_parameters=[
            openapi.Parameter(
                name='service_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='服务端点id'
            ),
        ],
        responses={
            201: '''    
                {
                    "id": "xxx"     # 服务器id; 创建成功
                }
            ''',
            202: '''
                {
                    "id": "xxx"     # 服务器id; 已接受创建请求，正在创建中；
                }            
            '''
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid(raise_exception=False):
            msg = serializer_error_msg(serializer.errors)
            exc = exceptions.BadRequest(msg)
            return Response(data=exc.err_data(), status=exc.status_code)

        data = serializer.validated_data
        image_id = data.get('image_id', '')
        flavor_id = str_to_int_or_default(data.get('flavor_id', 0), 0)
        network_id = data.get('network_id', '')
        remarks = data.get('remarks', request.user.username)

        flavor = Flavor.objects.filter(id=flavor_id).first()
        if not flavor:
            exc = exceptions.BadRequest(message=_('无效的flavor id'))
            return Response(exc.err_data(), status=exc.status_code)

        try:
            service = self.get_service(request, in_='body')
        except exceptions.APIException as exc:
            return Response(exc.err_data(), status=exc.status_code)

        params = inputs.ServerCreateInput(ram=flavor.ram, vcpu=flavor.vcpus, image_id=image_id,
                                          region_id=service.region_id, network_id=network_id, remarks=remarks)
        try:
            out = self.request_service(service=service, method='server_create', params=params)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        out_server = out.server
        server = Server(service=service,
                        instance_id=out_server.uuid,
                        remarks=remarks,
                        user=request.user,
                        vcpus=flavor.vcpus,
                        ram=flavor.ram,
                        task_status=Server.TASK_IN_CREATING
                        )
        server.save()
        if service.service_type == service.SERVICE_EVCLOUD:
            if self._update_server_detail(server):
                Response(data={'id': server.id}, status=status.HTTP_201_CREATED)

        return Response(data={'id': server.id}, status=status.HTTP_202_ACCEPTED)

    def _update_server_detail(self, server, task_status: int = None):
        """
        尝试更新服务器的详细信息
        :param server:
        :param task_status: 设置server的创建状态；默认None忽略
        :return:
            True    # success
            False   # failed
        """
        # 尝试获取详细信息
        params = inputs.ServerDetailInput(server_id=server.instance_id)
        try:
            out = self.request_service(service=server.service, method='server_detail', params=params)
            out_server = out.server
        except exceptions.APIException as exc:      #
            return False

        try:
            server.name = out_server.name if out_server.name else out_server.uuid
            if out_server.vcpu:
                server.vcpus = out_server.vcpu
            if out_server.ram:
                server.ram = out_server.ram

            server.ipv4 = out_server.ip.ipv4
            server.image = out_server.image.name
            server.public_ip = out_server.ip.public_ipv4 if out_server.ip.public_ipv4 else False
            server.task_status = task_status if task_status is not None else server.TASK_CREATED_OK     # 创建成功
            server.save()
        except Exception as e:
            return False

        return True

    @swagger_auto_schema(
        operation_summary=gettext_lazy('查询服务器实例信息'),
        responses={
            200: ''''''
        }
    )
    def retrieve(self, request, *args, **kwargs):
        server_id = kwargs.get(self.lookup_field, '')

        try:
            server = self.get_server(server_id=server_id, user=request.user)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        if server.ipv4 and server.image:
            serializer = serializers.ServerSerializer(server)
            return Response(data={'server': serializer.data})

        service = server.service
        params = inputs.ServerDetailInput(server_id=server.instance_id)
        try:
            out = self.request_service(service=service, method='server_detail', params=params)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        server.ipv4 = out.server.ip.ipv4
        server.image = out.server.image.name
        pub_ip = out.server.ip.public_ipv4
        if pub_ip is not None:
            server.public_ip = pub_ip

        try:
            server.save()
        except Exception as e:
            pass

        serializer = serializers.ServerSerializer(server)
        return Response(data={'server': serializer.data})

    @swagger_auto_schema(
        operation_summary=gettext_lazy('删除服务器实例')
    )
    def destroy(self, request, *args, **kwargs):
        server_id = kwargs.get(self.lookup_field, '')

        try:
            server = self.get_server(server_id=server_id, user=request.user)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        service = server.service
        try:
            self.request_service(service, method='server_delete', server_id=server.instance_id)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        server.do_archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_summary=gettext_lazy('操作服务器'),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'op': openapi.Schema(
                    title='操作',
                    type=openapi.TYPE_STRING,
                    enum=['start', 'reboot', 'shutdown', 'poweroff', 'delete', 'delete_force'],
                    description="操作选项",
                )
            }
        ),
        responses={
            200: '''
                {
                    'code': 200,
                    'code_text': '操作成功'
                }
                '''
        }
    )
    @action(methods=['post'], url_path='action', detail=True, url_name='server-action')
    def server_action(self, request, *args, **kwargs):
        server_id = kwargs.get(self.lookup_field, '')
        try:
            op = request.data.get('op', None)
        except Exception as e:
            exc = exceptions.InvalidArgument(_('参数有误') + ',' + str(e))
            return Response(data=exc.err_data(), status=exc.status_code)

        ops = inputs.ServerAction.values    # ['start', 'reboot', 'shutdown', 'poweroff', 'delete', 'delete_force']
        if not op or op not in ops:
            exc = exceptions.InvalidArgument(_('op参数无效'))
            return Response(data=exc.err_data(), status=exc.status_code)

        try:
            server = self.get_server(server_id=server_id, user=request.user)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        params = inputs.ServerActionInput(server_id=server.instance_id, action=op)
        service = server.service
        try:
            r = self.request_service(service, method='server_action', params=params)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        if op in ['delete', 'delete_force']:
            server.do_archive()
        return Response({'code': 'OK', 'message': 'Success'})

    @swagger_auto_schema(
        operation_summary=gettext_lazy('服务器状态查询'),
        responses={
            200: '''
                {
                }
                '''
        }
    )
    @action(methods=['get'], url_path='status', detail=True, url_name='server_status')
    def server_status(self, request, *args, **kwargs):
        server_id = kwargs.get(self.lookup_field, '')

        try:
            server = self.get_server(server_id=server_id, user=request.user)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        params = inputs.ServerStatusInput(server_id=server.instance_id)
        service = server.service
        try:
            r = self.request_service(service, method='server_status', params=params)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        status_code = r.status
        if status_code in outputs.ServerStatus.normal_values():     # 虚拟服务器状态正常
            if server.task_status == server.TASK_IN_CREATING:   #
                self._update_server_detail(server, task_status=server.TASK_CREATED_OK)

        return Response(data={
            'status': {
                'status_code': status_code,
                'status_test': r.status_mean
            }
        })

    @swagger_auto_schema(
        operation_summary=gettext_lazy('服务器VNC'),
        responses={
            200: '''
                    {
                    }
                    '''
        }
    )
    @action(methods=['get'], url_path='vnc', detail=True, url_name='server_vnc')
    def server_vnc(self, request, *args, **kwargs):
        server_id = kwargs.get(self.lookup_field, '')

        try:
            server = self.get_server(server_id=server_id, user=request.user)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        service = server.service
        params = inputs.ServerVNCInput(server_id=server.instance_id)
        try:
            r = self.request_service(service, method='server_vnc', params=params)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        return Response(data={'vnc': {
            'url': r.vnc.url
        }})

    @swagger_auto_schema(
        operation_summary=gettext_lazy('修改云服务器备注信息'),
        request_body=no_body,
        manual_parameters=[
            openapi.Parameter(
                name='remark',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description='新的备注信息'
            )
        ],
        responses={
            200: '''
                {
                    "remarks": "xxx"
                }
            '''
        }
    )
    @action(methods=['patch'], url_path='remark', detail=True, url_name='server-remark')
    def server_remark(self, request, *args, **kwargs):
        server_id = kwargs.get(self.lookup_field, '')
        remarks = request.query_params.get('remark', None)
        if remarks is None:
            return Response(data=exceptions.InvalidArgument(message='query param "remark" is required'))

        try:
            r = Server.objects.filter(pk=server_id).update(remarks=remarks)
        except Exception as exc:
            return Response(data=exceptions.APIException(extend_msg=str(exc)), status=500)

        if r == 0:
            return Response(data=exceptions.NotFound(extend_msg='云服务器不存在'))

        return Response(data={'remarks': remarks})

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ServerCreateSerializer

        return Serializer

    @staticmethod
    def get_server(server_id: int, user):
        server = Server.objects.filter(id=server_id).select_related('service', 'user').first()
        if not server:
            raise exceptions.NotFound(_('服务器实例不存在'))

        if not server.user_has_perms(user):
            raise exceptions.AccessDenied(_('无权限访问此服务器实例'))

        return server


class ImageViewSet(CustomGenericViewSet):
    """
    系统镜像视图
    """
    permission_classes = [IsAuthenticated, ]
    pagination_class = LimitOffsetPagination
    lookup_field = 'id'
    lookup_value_regex = '[0-9a-z-]+'
    serializer_class = Serializer

    @swagger_auto_schema(
        operation_summary=gettext_lazy('镜像列表'),
        manual_parameters=[
            openapi.Parameter(
                name='service_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='服务端点id'
            ),
        ],
        responses={
            200: """
                [
                  {
                    "id": "10",
                    "name": "空天院_ubuntu1804_radi",
                    "system": "空天院_ubuntu1804_radi",
                    "system_type": "Linux",
                    "creation_time": "2020-09-23T07:15:20.087505Z",
                    "desc": "空天院_ubuntu1804_radi"
                  }
                ]
            """
        }
    )
    def list(self, request, *args, **kwargs):
        try:
            service = self.get_service(request)
        except exceptions.APIException as exc:
            return Response(exc.err_data(), status=exc.status_code)

        params = inputs.ListImageInput(region_id=service.region_id)
        try:
            r = self.request_service(service, method='list_images', params=params)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        serializer = serializers.ImageSerializer(r.images, many=True)
        return Response(data=serializer.data)


class NetworkViewSet(CustomGenericViewSet):
    """
    网络子网视图
    """
    permission_classes = [IsAuthenticated, ]
    pagination_class = LimitOffsetPagination
    lookup_field = 'id'
    lookup_value_regex = '[0-9a-z-]+'
    serializer_class = Serializer

    @swagger_auto_schema(
        operation_summary=gettext_lazy('网络列表'),
        manual_parameters=[
            openapi.Parameter(
                name='service_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
                description='服务id'
            ),
        ],
        responses={
            200: """
                [
                  {
                    "id": "2",
                    "name": "private_10.108.50.0",
                    "public": false,
                    "segment": "10.108.50.0"
                  }
                ]
            """
        }
    )
    def list(self, request, *args, **kwargs):
        try:
            service = self.get_service(request)
        except exceptions.APIException as exc:
            return Response(exc.err_data(), status=exc.status_code)

        params = inputs.ListNetworkInput(region_id=service.region_id)
        try:
            r = self.request_service(service, method='list_networks', params=params)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)

        serializer = serializers.NetworkSerializer(r.networks, many=True)
        return Response(data=serializer.data)


class VPNViewSet(CustomGenericViewSet):
    """
    VPN相关API
    """
    queryset = []
    permission_classes = [IsAuthenticated]
    pagination_class = None
    lookup_field = 'service_id'

    @swagger_auto_schema(
        operation_summary=gettext_lazy('获取VPN口令'),
        responses={
            status.HTTP_200_OK: ''
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        获取VPN口令信息

            Http Code: 状态码200，返回数据：
            {
                "vpn": {
                    "username": "testuser",
                    "password": "password",
                    "active": true,
                    "create_time": "2020-07-29T15:12:08.715731+08:00",
                    "modified_time": "2020-07-29T15:12:08.715998+08:00"
                }
            }
        """
        try:
            service = self.get_service(request, lookup=self.lookup_field, in_='path')
        except exceptions.APIException as exc:
            return Response(exc.err_data(), status=exc.status_code)

        try:
            r = self.request_vpn_service(service, method='get_vpn_or_create', username=request.user.username)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)
        return Response(data={'vpn': r})

    @swagger_auto_schema(
        operation_summary=gettext_lazy('修改vpn口令'),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='The new password of vpn'
                )
            }
        ),
        responses={
            status.HTTP_201_CREATED: """
                {
                    "vpn": {
                        "username": "testuser",
                        "password": "password",
                        "active": true,
                        "create_time": "2020-07-29T15:12:08.715731+08:00",
                        "modified_time": "2020-07-29T15:12:08.715998+08:00"
                    }
                }
            """,
            status.HTTP_400_BAD_REQUEST: """
                    {
                        "code": 'xxx',
                        "message": "xxx"
                    }
                """
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """
        修改vpn口令
        """
        password = request.data.get('password')

        try:
            service = self.get_service(request, lookup=self.lookup_field, in_='path')
        except exceptions.APIException as exc:
            return Response(exc.err_data(), status=exc.status_code)

        try:
            r = self.request_vpn_service(service, method='vpn_change_password', username=request.user.username,
                                         password=password)
        except exceptions.AuthenticationFailed as exc:
            return Response(data=exc.err_data(), status=500)
        except exceptions.APIException as exc:
            return Response(data=exc.err_data(), status=exc.status_code)
        return Response(data={'vpn': r})

    def get_serializer_class(self):
        return Serializer


class FlavorViewSet(CustomGenericViewSet):
    """
    Flavor相关API
    """
    queryset = []
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    @swagger_auto_schema(
        operation_summary=gettext_lazy('列举配置样式flavor'),
        responses={
            status.HTTP_200_OK: ''
        }
    )
    def list(self, request, *args, **kwargs):
        """
        列举配置样式flavor

            Http Code: 状态码200，返回数据：
            {
              "flavors": [
                {
                  "id": 4,
                  "vcpus": 4,
                  "ram": 4096
                }
              ]
            }
        """
        try:
            flavors = Flavor.objects.filter(enable=True).order_by('vcpus').all()
            serializer = serializers.FlavorSerializer(flavors, many=True)
        except Exception as exc:
            err = exceptions.APIException(message=str(exc))
            return Response(err.err_data(), status=err.status_code)

        return Response(data={"flavors": serializer.data})


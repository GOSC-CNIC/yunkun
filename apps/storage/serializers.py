from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class BucketCreateSerializer(serializers.Serializer):
    service_id = serializers.CharField(label=_('服务单元ID'), max_length=36, required=True)
    name = serializers.CharField(label=_('存储桶名称'), max_length=73, required=True)


class BucketSerializer(serializers.Serializer):
    id = serializers.CharField(label=_('存储桶ID'))
    name = serializers.CharField(label=_('存储桶名称'))
    creation_time = serializers.DateTimeField(label=_('创建时间'))
    user_id = serializers.CharField(label=_('用户id'))
    username = serializers.SerializerMethodField(method_name='get_username')
    service = serializers.SerializerMethodField(method_name='get_service')
    storage_size = serializers.IntegerField(label=_('桶存储容量'))
    object_count = serializers.IntegerField(label=_('桶对象数量'))
    stats_time = serializers.DateTimeField(label=_('桶资源统计时间'))

    @staticmethod
    def get_username(obj):
        if obj.user:
            return obj.user.username

        return ''

    @staticmethod
    def get_service(obj):
        if obj.service:
            return {'id': obj.service.id, 'name': obj.service.name, 'name_en': obj.service.name_en}

        return {'id': None, 'name': None, 'name_en': None}


class AdminBucketSerializer(BucketSerializer):
    task_status = serializers.CharField(label='创建状态', max_length=16)
    situation = serializers.CharField(label='过期欠费管控情况', max_length=16, help_text='欠费状态下存储桶读写锁定管控情况')
    situation_time = serializers.DateTimeField(label='管控情况时间', help_text='欠费管控开始时间')


class ObjectsServiceSerializer(serializers.Serializer):
    id = serializers.CharField(label=_('存储桶ID'))
    name = serializers.CharField(label=_('服务名称'))
    name_en = serializers.CharField(label=_('服务英文名称'))
    service_type = serializers.CharField()
    endpoint_url = serializers.CharField(label=_('服务地址url'), help_text='http(s)://{hostname}:{port}/')
    add_time = serializers.DateTimeField(label=_('添加时间'))
    status = serializers.CharField(label=_('服务状态'))
    remarks = serializers.CharField(label=_('备注'))
    provide_ftp = serializers.BooleanField(label=_('是否提供FTP服务'))
    ftp_domains = serializers.SerializerMethodField(method_name='get_ftp_domains')
    longitude = serializers.FloatField(label=_('经度'))
    latitude = serializers.FloatField(label=_('纬度'))
    pay_app_service_id = serializers.CharField(label=_('余额结算APP服务ID'))
    org_data_center = serializers.SerializerMethodField(label=_('机构数据中心'), method_name='get_org_data_center')
    sort_weight = serializers.IntegerField(label=_('排序权重'), default=0, help_text=_('值越大排序越靠前'))
    # loki_tag = serializers.CharField(
    #     label=_('对应loki日志中集群标识'), max_length=128,
    #     help_text=_('服务单元在Loki访问日志中对应的对象存储集群标识，用于计量网络流量、请求量等信息时标识对应关系'))
    version = serializers.CharField(max_length=32, label=_('版本号'))
    version_update_time = serializers.DateTimeField(label=_('版本号更新时间'))

    @staticmethod
    def get_ftp_domains(obj):
        return obj.ftp_domains_list()

    @staticmethod
    def get_org_data_center(obj):
        odc = obj.org_data_center
        if odc is None:
            return None

        data = {
            'id': odc.id, 'name': odc.name, 'name_en': odc.name_en, 'sort_weight': odc.sort_weight
        }
        org = odc.organization
        if org is None:
            data['organization'] = None
        else:
            data['organization'] = {
                'id': org.id, 'name': org.name, 'name_en': org.name_en, 'sort_weight': org.sort_weight
            }

        return data


class AdminObjectsServiceSerializer(ObjectsServiceSerializer):
    username = serializers.CharField(max_length=128, label=_('用户名'), help_text=_('用于此服务认证的用户名'))


class ObjectsServiceWithAdminsSerializer(ObjectsServiceSerializer):
    admin_users = serializers.SerializerMethodField(label=_('服务单元管理员'), method_name='get_admin_users')

    @staticmethod
    def get_admin_users(obj):
        return obj.admin_users

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class PeriodSerializer(serializers.Serializer):
    id = serializers.CharField(label=_('ID'))
    period = serializers.IntegerField(label=_('月数'))
    enable = serializers.BooleanField(label='启用')
    creation_time = serializers.DateTimeField(label=_('创建时间'))
    service_id = serializers.CharField(label=_('服务单元ID'), max_length=36, required=True)


class FlavorSerializer(serializers.Serializer):
    id = serializers.CharField()
    flavor_id = serializers.CharField(label=_('服务端规格ID'))
    vcpus = serializers.IntegerField(label=_('虚拟CPU数'))
    ram = serializers.IntegerField(label=_('内存GiB'))
    disk = serializers.IntegerField(label=_('硬盘GB'))
    service_id = serializers.CharField(label=_('服务单元id'))
    enable = serializers.BooleanField(label='启用')
    ram_gib = serializers.SerializerMethodField(method_name='get_ram_gib', label=_('内存GiB'))

    @staticmethod
    def get_ram_gib(obj):
        return obj.ram


class FlavorCreateSerializer(serializers.Serializer):
    service_id = serializers.CharField(label=_('服务单元id'), required=True)
    vcpus = serializers.IntegerField(label=_('CPU数'), required=True)
    ram = serializers.IntegerField(label=_('内存GiB'), required=True)
    enable = serializers.BooleanField(label=_('是否启用'), required=True)


class ImageSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    release = serializers.CharField()
    version = serializers.CharField()
    architecture = serializers.CharField()
    system_type = serializers.CharField()
    creation_time = serializers.DateTimeField()
    desc = serializers.CharField()
    default_user = serializers.CharField()
    default_password = serializers.CharField()
    min_sys_disk_gb = serializers.IntegerField()
    min_ram_mb = serializers.IntegerField()


class ImageOldSerializer(ImageSerializer):
    system = serializers.SerializerMethodField(method_name='get_system')

    @staticmethod
    def get_system(obj):
        return obj.release


class NetworkSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    public = serializers.BooleanField()
    segment = serializers.CharField()


class AvailabilityZoneSerializer(serializers.Serializer):
    id = serializers.CharField(label=_('可用区ID'))
    name = serializers.CharField(label=_('可用区名称'))
    available = serializers.BooleanField(label=_('是否可用'))


class ServerBaseSerializer(serializers.Serializer):
    """
    虚拟服务器实例序列化器基类
    """
    id = serializers.CharField()
    name = serializers.CharField()
    vcpus = serializers.IntegerField()
    ram = serializers.SerializerMethodField(method_name='get_ram')
    ram_gib = serializers.IntegerField()
    ipv4 = serializers.CharField()
    public_ip = serializers.BooleanField()
    image = serializers.CharField()
    creation_time = serializers.DateTimeField()
    expiration_time = serializers.DateTimeField()
    remarks = serializers.CharField()
    classification = serializers.CharField()
    image_id = serializers.CharField()
    image_desc = serializers.CharField()
    default_user = serializers.CharField()
    default_password = serializers.SerializerMethodField(method_name='get_default_password')
    pay_type = serializers.CharField()
    img_sys_type = serializers.CharField(max_length=32, label=_('镜像系统类型'))
    img_sys_arch = serializers.CharField(max_length=32, label=_('镜像系统架构'))
    img_release = serializers.CharField(max_length=32, label=_('镜像系统发行版'))
    img_release_version = serializers.CharField(max_length=32, label=_('镜像系统发行版版本'))

    @staticmethod
    def get_default_password(obj):
        return obj.raw_default_password

    @staticmethod
    def get_ram(obj):
        return obj.ram_gib


class ServerSimpleSerializer(ServerBaseSerializer):
    pass


class ServerSerializer(ServerBaseSerializer):
    """
    虚拟服务器实例序列化器
    """
    service = serializers.SerializerMethodField(method_name='get_service')
    center_quota = serializers.IntegerField()
    vo_id = serializers.CharField()
    vo = serializers.SerializerMethodField(method_name='get_vo')
    user = serializers.SerializerMethodField(method_name='get_user')
    lock = serializers.CharField(label=_('锁'), max_length=16)

    @staticmethod
    def get_service(obj):
        service = obj.service
        if service:
            return {
                'id': service.id,
                'name': service.name,
                'name_en': service.name_en,
                'service_type': service.service_type
            }

        return None

    @staticmethod
    def get_user(obj):
        user = obj.user
        if user:
            return {
                'id': user.id,
                'username': user.username
            }

        return None

    @staticmethod
    def get_vo(obj):
        vo = obj.vo
        if vo:
            return {
                'id': vo.id,
                'name': vo.name
            }

        return None


class ServerCreateSerializer(serializers.Serializer):
    """
    创建虚拟服务器序列化器
    """
    pay_type = serializers.CharField(label=_('付费模式'), required=True, max_length=16)
    service_id = serializers.CharField(label=_('服务'), required=True, help_text=_('服务提供商配置ID'))
    image_id = serializers.CharField(label=_('镜像id'), required=True, help_text=_('系统镜像id'))
    flavor_id = serializers.CharField(label=_('配置样式id'), required=True, help_text=_('硬件配置样式ID'))
    network_id = serializers.CharField(label=_('子网id'), required=True, help_text=_('子网ID'))
    systemdisk_size = serializers.IntegerField(
        label=_('系统盘大小（GiB）'), min_value=50, max_value=500, required=False, allow_null=True,
        help_text=_('指定云服务期的系统盘大小，单位GiB，只允许50的倍数值，50、100、150等'), default=None)
    remarks = serializers.CharField(label=_('备注'), required=False, allow_blank=True, max_length=255, default='')
    azone_id = serializers.CharField(label=_('可用区'), required=False, allow_null=True, max_length=36, default=None)
    vo_id = serializers.CharField(
        label=_('vo组id'), required=False, allow_null=True, max_length=36, default=None,
        help_text=_('通过vo_id指定为vo组创建云服务器'))
    period = serializers.IntegerField(
        label=_('订购时长（月）'), required=False, allow_null=True, default=None,
        help_text=_('付费模式为预付费时，必须指定订购时长'))
    number = serializers.IntegerField(label=_('订购资源数量'), required=False, allow_null=True, default=1)

    def validate(self, attrs):
        return attrs


class ServerArchiveSerializer(ServerBaseSerializer):
    """
    虚拟服务器归档记录序列化器
    """
    server_id = serializers.CharField()
    service = serializers.SerializerMethodField(method_name='get_service')
    center_quota = serializers.IntegerField()
    deleted_time = serializers.DateTimeField()
    vo_id = serializers.CharField()

    @staticmethod
    def get_service(obj):
        service = obj.service
        if service:
            return {
                'id': service.id,
                'name': service.name,
                'name_en': service.name_en,
                'service_type': service.service_type
            }

        return None


class ServerRebuildSerializer(serializers.Serializer):
    """
    创建虚拟服务器序列化器
    """
    image_id = serializers.CharField(label=_('镜像id'), required=True, help_text=_('系统镜像id'))


class VmServiceSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    name_en = serializers.CharField()
    service_type = serializers.CharField()
    cloud_type = serializers.CharField()
    add_time = serializers.DateTimeField()
    need_vpn = serializers.BooleanField()
    status = serializers.CharField()
    org_data_center = serializers.SerializerMethodField(label=_('机构数据中心'), method_name='get_org_data_center')
    longitude = serializers.FloatField(label=_('经度'), default=0)
    latitude = serializers.FloatField(label=_('纬度'), default=0)
    pay_app_service_id = serializers.CharField(label=_('余额结算APP服务ID'), max_length=36)
    sort_weight = serializers.IntegerField(label=_('排序权重'), default=0, help_text=_('值越大排序越靠前'))
    disk_available = serializers.BooleanField(label=_('提供云硬盘服务'))

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
                'id': org.id, 'name': org.name, 'name_en': org.name_en
            }

        return data


class AdminServiceSerializer(VmServiceSerializer):
    region_id = serializers.CharField(max_length=128, label=_('服务区域/分中心ID'))
    endpoint_url = serializers.CharField(
        max_length=255, label=_('服务地址url'), help_text='http(s)://{hostname}:{port}/')
    api_version = serializers.CharField(
        max_length=64, label=_('API版本'), help_text=_('预留，主要EVCloud使用'))
    username = serializers.CharField(max_length=128, label=_('用户名'), help_text=_('用于此服务认证的用户名'))
    extra = serializers.CharField(max_length=1024, label=_('其他配置'), help_text=_('json格式'))
    remarks = serializers.CharField(max_length=255, label=_('备注'))


class VmServiceBaseQuotaUpdateSerializer(serializers.Serializer):
    private_ip_total = serializers.IntegerField(
        label=_('总私网IP数'), min_value=0, required=False, allow_null=True, default=None,
        help_text=_('不更改不要提交此内容'))
    public_ip_total = serializers.IntegerField(
        label=_('总公网IP数'), min_value=0, required=False, allow_null=True, default=None,
        help_text=_('不更改不要提交此内容'))
    vcpu_total = serializers.IntegerField(
        label=_('总CPU核数'), min_value=0, required=False, allow_null=True, default=None,
        help_text=_('不更改不要提交此内容'))
    ram_total = serializers.IntegerField(
        label=_('总内存大小(GB)'), min_value=0, required=False, allow_null=True, default=None,
        help_text=_('不更改不要提交此内容'))
    disk_size_total = serializers.IntegerField(
        label=_('总硬盘大小(GB)'), min_value=0, required=False, allow_null=True, default=None,
        help_text=_('不更改不要提交此内容'))


class VmServicePrivateQuotaUpdateSerializer(VmServiceBaseQuotaUpdateSerializer):
    pass


class VmServiceShareQuotaUpdateSerializer(VmServiceBaseQuotaUpdateSerializer):
    pass


class VmServiceBaseQuotaSerializer(VmServiceBaseQuotaUpdateSerializer):
    private_ip_used = serializers.IntegerField(label=_('已用私网IP数'), read_only=True)
    public_ip_used = serializers.IntegerField(label=_('已用公网IP数'), read_only=True)
    vcpu_used = serializers.IntegerField(label=_('已用CPU核数'), read_only=True)
    ram_used = serializers.IntegerField(label=_('已用内存大小(GiB)'), read_only=True)
    disk_size_used = serializers.IntegerField(label=_('已用硬盘大小(GB)'), read_only=True)
    creation_time = serializers.DateTimeField(label=_('创建时间'), read_only=True)
    enable = serializers.BooleanField(label=_('有效状态'), read_only=True,
                                      help_text=_('选中，资源配额生效；未选中，无法申请分中心资源'))
    service = serializers.SerializerMethodField(method_name='get_service')

    @staticmethod
    def get_service(obj):
        if obj.service:
            return {'id': obj.service.id, 'name': obj.service.name, 'name_en': obj.service.name_en}

        return {'id': None, 'name': None, 'name_en': None}


class VmServicePrivateQuotaSerializer(VmServiceBaseQuotaSerializer):
    pass


class VmServiceShareQuotaSerializer(VmServiceBaseQuotaSerializer):
    pass


class ServiceSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    name_en = serializers.CharField()
    service_type = serializers.CharField()
    cloud_type = serializers.CharField()
    add_time = serializers.DateTimeField()
    need_vpn = serializers.BooleanField()
    status = serializers.CharField()
    org_data_center = serializers.SerializerMethodField(label=_('机构数据中心'), method_name='get_org_data_center')
    longitude = serializers.FloatField(label=_('经度'), default=0)
    latitude = serializers.FloatField(label=_('纬度'), default=0)
    pay_app_service_id = serializers.CharField(label=_('余额结算APP服务ID'), max_length=36)
    sort_weight = serializers.IntegerField(label=_('排序权重'), default=0, help_text=_('值越大排序越靠前'))
    disk_available = serializers.BooleanField(label=_('提供云硬盘服务'))
    only_admin_visible = serializers.BooleanField(label=_('仅管理员可见'))

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
                'id': org.id, 'name': org.name, 'name_en': org.name_en
            }

        return data

from rest_framework import serializers
from apps.app_netflow.models import MenuModel
from apps.app_netflow.models import ChartModel
from apps.app_netflow.models import Menu2Chart
from apps.app_netflow.models import Menu2Member
from apps.app_netflow.models import GlobalAdminModel
from apps.app_netflow.permission import PermissionManager
from apps.users.models import UserProfile


class ChartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartModel
        fields = "__all__"


class GlobalAdminSerializer(serializers.ModelSerializer):
    member = serializers.EmailField(required=True, write_only=True, label='用户邮箱')
    username = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = GlobalAdminModel

        fields = [
            'id',
            'username',
            'member',
            'role',
            'inviter',
            'creation',
            'modification',
        ]

    def get_username(self, obj):
        return obj.member.username

    def validate_member(self, value):
        user = UserProfile.objects.filter(username=value).first()
        if not user:
            raise serializers.ValidationError(f"Invalid User {value}")
        return user


class GlobalAdminWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalAdminModel

        fields = [
            'id',
            'role',
        ]

    def get_username(self, obj):
        return obj.member.username


class Menu2MemberSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    member = serializers.EmailField(required=True, write_only=True, label='用户邮箱')

    def validate_member(self, value):
        from apps.users.models import UserProfile
        user = UserProfile.objects.filter(username=value).first()
        if not user:
            raise serializers.ValidationError(f"Invalid User {value}")
        return user

    class Meta:
        model = Menu2Member
        extra_kwargs = {
            'menu': {'write_only': True},
        }
        fields = (
            "id",
            "role",
            "inviter",
            "creation",
            "menu",
            "member",
            "username",
        )

    def get_username(self, obj):
        return obj.member.username


class Menu2MemberWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu2Member
        fields = [
            "id",
            "role",
        ]


class Menu2ChartSerializer(serializers.ModelSerializer):
    instance_name = serializers.SerializerMethodField(read_only=True)
    global_title = serializers.SerializerMethodField(read_only=True)
    global_remark = serializers.SerializerMethodField(read_only=True)
    if_alias = serializers.SerializerMethodField(read_only=True)
    if_address = serializers.SerializerMethodField(read_only=True)
    device_ip = serializers.SerializerMethodField(read_only=True)
    port_name = serializers.SerializerMethodField(read_only=True)
    class_uuid = serializers.SerializerMethodField(read_only=True)
    band_width = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Menu2Chart
        extra_kwargs = {
            'menu': {'write_only': True},
            'chart': {'write_only': True}
        }
        fields = [
            "id",
            "instance_name",
            "global_title",
            "global_remark",
            "title",
            "remark",
            "sort_weight",
            "if_alias",
            "if_address",
            "device_ip",
            "port_name",
            "class_uuid",
            "band_width",
            "menu",
            "chart",
        ]

    def get_global_title(self, obj):
        return obj.chart.title

    def get_global_remark(self, obj):
        return obj.chart.remark

    def get_instance_name(self, obj):
        return obj.chart.instance_name

    def get_if_alias(self, obj):
        return obj.chart.if_alias

    def get_device_ip(self, obj):
        return obj.chart.device_ip

    def get_if_address(self, obj):
        return obj.chart.if_address

    def get_port_name(self, obj):
        return obj.chart.port_name

    def get_class_uuid(self, obj):
        return obj.chart.class_uuid

    def get_band_width(self, obj):
        return obj.chart.band_width


class Menu2ChartWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu2Chart
        fields = [
            "id",
            "title",
            "remark",
            "sort_weight",
        ]


class MenuWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuModel
        fields = [
            "id",
            "name",
            "sort_weight",
            "remark",
        ]


class MenuModelSerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField(read_only=True)
    father_id = serializers.PrimaryKeyRelatedField(
        queryset=MenuModel.objects.all(),
        source='father',
        write_only=True,
        default=None
    )

    def get_sub_categories(self, obj):
        """
        根据用户角色，返回目录结构
        """
        request = self.context.get('request')
        perm = PermissionManager(request=request)
        children = obj.sub_categories.all()
        if perm.is_global_admin():  # 全局管理员
            return MenuModelSerializer(children, many=True, context=self.context).data
        groups = perm.user_group_list()
        exclude = []
        for child in children:
            for group_node in groups:
                flag = perm.is_branch_relationship(child, group_node)
                if flag:
                    break
            else:
                exclude.append(child.id)
        return MenuModelSerializer(children.exclude(id__in=exclude), many=True, context=self.context).data

    class Meta:
        model = MenuModel
        fields = (
            'id',
            'name',
            'sort_weight',
            'remark',
            'level',
            'sub_categories',
            'father_id',
        )
        depth = 0


class CustomSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        self.meta = dict()
        super().__init__(*args, **kwargs)


class TimestampRangeSerializer(CustomSerializer):
    start = serializers.IntegerField(
        label="起始时间戳",
        help_text='起始时间戳',
        required=True,
        error_messages={'required': "起始时间戳start不能为空"}
    )
    end = serializers.IntegerField(
        label="结束时间戳",
        help_text='结束时间戳',
        required=True,
        error_messages={'required': "结束时间戳end不能为空"}
    )

    def validate_start(self, start):
        if not self.s_or_ns(start):
            raise serializers.ValidationError("start仅支持10位或19位.请检查: {}".format(start))
        self.meta["start"] = start
        return start

    def validate_end(self, end):
        if not self.s_or_ns(end):
            raise serializers.ValidationError("end仅支持10位或19位.请检查: {}".format(end))
        self.meta["end"] = end
        if self.meta.get("start") > end:
            raise serializers.ValidationError("start 应小于等于 end")
        return end

    @staticmethod
    def s_or_ns(ts):
        return len(str(ts)) in [10, 19]


class TrafficSerializer(TimestampRangeSerializer):
    chart = serializers.CharField(
        label="元素id",
        help_text='元素id',
        required=True,
        error_messages={'required': "元素id不能为空"}
    )
    metrics_ids = serializers.JSONField(
        label="查询字段",
        help_text='查询字段',
        required=True,
        error_messages={'required': "查询字段不能为空"}
    )

    def validate_chart(self, chart):
        element = Menu2Chart.objects.filter(id=chart).first()
        if not element:
            raise serializers.ValidationError("无效的chart参数")
        return element.chart.id

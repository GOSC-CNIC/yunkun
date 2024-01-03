from typing import Union, List

from django.utils.translation import gettext as _
from django.db.models import Q
from django.db import transaction

from users.models import UserProfile
from service.models import ServiceConfig, OrgDataCenter, DataCenter as Organization
from core import errors
from bill.models import PayAppService
from storage.models import ObjectsService


class OrgDataCenterManager:
    @staticmethod
    def get_org(org_id: str):
        org = Organization.objects.filter(id=org_id).first()
        if org is None:
            raise errors.TargetNotExist(message=_('机构不存在'))

        return org

    @staticmethod
    def get_odc(odc_id: str):
        """
        :raises: Error
        """
        odc = OrgDataCenter.objects.select_related('organization').filter(id=odc_id).first()
        if odc is None:
            raise errors.TargetNotExist(message=_('机构数据中心不存在'))

        return odc

    @staticmethod
    def _update_odc_fields(
            org_dc: OrgDataCenter,
            name: str = None, name_en: str = None, organization_id: str = None,
            longitude: float = None, latitude: float = None, sort_weight: int = None, remark: str = None,
            thanos_endpoint_url: str = None, thanos_username: str = None, thanos_password: str = None,
            thanos_receive_url: str = None, thanos_remark: str = None,
            loki_endpoint_url: str = None, loki_username: str = None, loki_password: str = None,
            loki_receive_url: str = None, loki_remark: str = None
    ):
        """
        创建或更新机构下的数据中心
        """
        if name is not None:
            org_dc.name = name
        if name_en is not None:
            org_dc.name_en = name_en
        if longitude is not None:
            org_dc.organization_id = organization_id
        if longitude is not None:
            org_dc.longitude = longitude
        if latitude is not None:
            org_dc.latitude = latitude
        if sort_weight is not None:
            org_dc.sort_weight = sort_weight
        if remark is not None:
            org_dc.remark = remark

        if thanos_endpoint_url is not None:
            org_dc.thanos_endpoint_url = thanos_endpoint_url
        if thanos_username is not None:
            org_dc.thanos_username = thanos_username
        if thanos_password is not None:
            org_dc.raw_thanos_password = thanos_password
        if thanos_receive_url is not None:
            org_dc.thanos_receive_url = thanos_receive_url
        if thanos_remark is not None:
            org_dc.thanos_remark = thanos_remark

        if loki_endpoint_url is not None:
            org_dc.loki_endpoint_url = loki_endpoint_url
        if loki_username is not None:
            org_dc.loki_username = loki_username
        if loki_password is not None:
            org_dc.raw_loki_password = loki_password
        if loki_receive_url is not None:
            org_dc.loki_receive_url = loki_receive_url
        if loki_remark is not None:
            org_dc.loki_remark = loki_remark

        return org_dc

    @staticmethod
    def create_org_dc(
            name: str, name_en: str, organization_id: str,
            longitude: float = None, latitude: float = None, sort_weight: int = None, remark: str = None,
            thanos_endpoint_url: str = None, thanos_username: str = None, thanos_password: str = None,
            thanos_receive_url: str = None, thanos_remark: str = None,
            loki_endpoint_url: str = None, loki_username: str = None, loki_password: str = None,
            loki_receive_url: str = None, loki_remark: str = None
    ) -> OrgDataCenter:
        odc = OrgDataCenter()
        OrgDataCenterManager._update_odc_fields(
            org_dc=odc, name=name, name_en=name_en, organization_id=organization_id,
            longitude=longitude, latitude=latitude, sort_weight=sort_weight, remark=remark,
            thanos_endpoint_url=thanos_endpoint_url, thanos_receive_url=thanos_receive_url,
            thanos_username=thanos_username, thanos_password=thanos_password, thanos_remark=thanos_remark,
            loki_endpoint_url=loki_endpoint_url, loki_receive_url=loki_receive_url,
            loki_username=loki_username, loki_password=loki_password, loki_remark=loki_remark
        )
        odc.save(force_insert=True)
        return odc

    @staticmethod
    def update_org_dc(
            odc_or_id: Union[str, OrgDataCenter], name: str = None, name_en: str = None, organization_id: str = None,
            longitude: float = None, latitude: float = None, sort_weight: int = None, remark: str = None,
            thanos_endpoint_url: str = None, thanos_username: str = None, thanos_password: str = None,
            thanos_receive_url: str = None, thanos_remark: str = None,
            loki_endpoint_url: str = None, loki_username: str = None, loki_password: str = None,
            loki_receive_url: str = None, loki_remark: str = None
    ) -> OrgDataCenter:
        """
        :raises: Error
        """
        if not isinstance(odc_or_id, OrgDataCenter):
            odc = OrgDataCenterManager.get_odc(odc_id=odc_or_id)
        else:
            odc = odc_or_id

        OrgDataCenterManager._update_odc_fields(
            org_dc=odc, name=name, name_en=name_en, organization_id=organization_id,
            longitude=longitude, latitude=latitude, sort_weight=sort_weight, remark=remark,
            thanos_endpoint_url=thanos_endpoint_url, thanos_receive_url=thanos_receive_url,
            thanos_username=thanos_username, thanos_password=thanos_password, thanos_remark=thanos_remark,
            loki_endpoint_url=loki_endpoint_url, loki_receive_url=loki_receive_url,
            loki_username=loki_username, loki_password=loki_password, loki_remark=loki_remark
        )
        odc.save(force_update=True)
        return odc

    @staticmethod
    def filter_queryset(queryset, org_id: str, search: str):
        """
        search: 关键字查询，name,name_en,remark
        """
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(name_en__icontains=search) | Q(remark__icontains=search))

        return queryset

    @staticmethod
    def get_odc_queryset(org_id: str, search: str):
        queryset = OrgDataCenter.objects.select_related('organization').order_by('creation_time')
        return OrgDataCenterManager.filter_queryset(queryset=queryset, org_id=org_id, search=search)

    @staticmethod
    def _validate_usernames(usernames: list) -> List[UserProfile]:
        if not usernames:
            return []

        username_set = set(usernames)
        if len(username_set) != len(usernames):
            raise errors.InvalidArgument(message=_('提交的用户名列表中存在重复的用户名'))

        usernames = list(username_set)
        if len(usernames) == 1:
            users = UserProfile.objects.filter(username=usernames[0])
        else:
            users = UserProfile.objects.filter(username__in=usernames)

        users = list(users)
        if len(users) != len(username_set):
            exists_usernames_set = {u.username for u in users}
            not_exists_usernames = username_set.difference(exists_usernames_set)
            raise errors.InvalidArgument(message=_('指定的用户不存在：') + '' + '、'.join(not_exists_usernames))

        return users

    @staticmethod
    def add_admins_for_odc(odc: OrgDataCenter, usernames: list):
        users = OrgDataCenterManager._validate_usernames(usernames)
        if not users:
            return odc

        with transaction.atomic():
            odc.users.add(*users)    # 底层不会重复添加已存在的用户
            OrgDataCenterManager.sync_odc_admin_to_pay_service(odc=odc, add_admins=users, remove_admins=[])

        return odc

    @staticmethod
    def remove_admins_from_odc(odc: OrgDataCenter, usernames: list):
        users = OrgDataCenterManager._validate_usernames(usernames)
        if not users:
            return odc

        with transaction.atomic():
            odc.users.remove(*users)
            OrgDataCenterManager.sync_odc_admin_to_pay_service(odc=odc, add_admins=[], remove_admins=users)

        return odc

    @staticmethod
    def get_odc_pay_service_qs(odc: OrgDataCenter):
        server_pay_ids = ServiceConfig.objects.filter(
            org_data_center_id=odc.id).values_list('pay_app_service_id', flat=True)
        storage_pay_ids = ObjectsService.objects.filter(
            org_data_center_id=odc.id).values_list('pay_app_service_id', flat=True)
        pay_service_ids = [i for i in server_pay_ids if i] + [i for i in storage_pay_ids if i]
        if pay_service_ids:
            return PayAppService.objects.filter(id__in=pay_service_ids)

        return None

    @staticmethod
    def sync_odc_admin_to_pay_service(odc: OrgDataCenter, remove_admins: list, add_admins: list):
        """
        数据中心下云主机和存储服务单元对应的钱包结算单元管理员设置
        """
        pay_services = OrgDataCenterManager.get_odc_pay_service_qs(odc=odc)
        if pay_services is None:
            return []

        with transaction.atomic():
            for pay in pay_services:
                if remove_admins:
                    pay.users.remove(*remove_admins)
                if add_admins:
                    pay.users.add(*add_admins)

        return pay_services

    @staticmethod
    def is_admin_of_odc(odc_id, user_id):
        return OrgDataCenter.objects.filter(id=odc_id, users__id=user_id).exists()

    @staticmethod
    def get_odc_admin_emails(odc_ids: list):
        if not odc_ids:
            return []
        if len(odc_ids) == 1:
            lookups = {'id': odc_ids[0]}
        else:
            lookups = {'id__in': odc_ids}

        qs = OrgDataCenter.objects.filter(**lookups).values_list('users__username', flat=True)
        return list(qs)

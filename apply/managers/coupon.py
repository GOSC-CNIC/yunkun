from typing import Union
from datetime import datetime
from decimal import Decimal

from django.utils.translation import gettext as _
from django.utils import timezone as dj_timezone
from django.db import transaction

from core import errors
from utils.model import OwnerType
from service.models import OrgDataCenter
from service.odc_manager import OrgDataCenterManager
from vo.managers import VoManager
from apply.models import CouponApply


class CouponApplyManager:
    @staticmethod
    def create_apply(
            service_type: str, odc: Union[OrgDataCenter, None], service_id: str, service_name: str,
            service_name_en: str, pay_service_id: str, face_value: Decimal, expiration_time: datetime,
            apply_desc: str, user_id: str, username: str, vo_id: str, vo_name: str, owner_type: str,
            creation_time: datetime = None, status: str = CouponApply.Status.WAIT.value,
            approver: str = '', reject_reason: str = '', approved_amount: Decimal = Decimal('0.00'),
            coupon_id: str = '', deleted: bool = False, delete_user: str = ''
    ):
        if not creation_time:
            creation_time = dj_timezone.now()

        apply = CouponApply(
            service_type=service_type, odc=odc, service_id=service_id, service_name=service_name,
            service_name_en=service_name_en, pay_service_id=pay_service_id,
            face_value=face_value, expiration_time=expiration_time, apply_desc=apply_desc,
            user_id=user_id, username=username, vo_id=vo_id, vo_name=vo_name, owner_type=owner_type,
            creation_time=creation_time, update_time=creation_time,
            status=status, approver=approver, reject_reason=reject_reason, approved_amount=approved_amount,
            coupon_id=coupon_id, deleted=deleted, delete_user=delete_user
        )
        apply.save(force_insert=True)
        return apply

    @staticmethod
    def update_apply(
            apply, service_type: str, odc: Union[OrgDataCenter, None], service_id: str, service_name: str,
            service_name_en: str, pay_service_id: str, face_value: Decimal, expiration_time: datetime,
            apply_desc: str, user_id: str, username: str
    ):
        apply.service_type = service_type
        apply.odc = odc
        apply.service_id = service_id
        apply.service_name = service_name
        apply.service_name_en = service_name_en
        apply.pay_service_id = pay_service_id
        apply.face_value = face_value
        apply.expiration_time = expiration_time
        apply.apply_desc = apply_desc
        apply.update_time = dj_timezone.now()
        if user_id:
            apply.user_id = user_id
        if username:
            apply.username = username
        apply.status = CouponApply.Status.WAIT.value
        apply.reject_reason = ''
        apply.approver = ''
        apply.save(force_update=True)
        return apply

    @staticmethod
    def get_perm_apply(_id: str, user, select_for_update: bool = False) -> CouponApply:
        if select_for_update:
            apply = CouponApply.objects.select_related('odc').select_for_update().filter(id=_id).first()
        else:
            apply = CouponApply.objects.select_related('odc').filter(id=_id).first()

        if apply is None or apply.deleted:
            raise errors.TargetNotExist(message=_('申请记录不存在'))

        if apply.owner_type == OwnerType.VO.value:
            VoManager.has_vo_permission(vo_id=apply.vo_id, user=user, read_only=False)
        else:
            if apply.user_id != user.id:
                raise errors.AccessDenied(message=_('你没有申请记录访问权限'))

        return apply

    @staticmethod
    def get_admin_perm_apply(_id: str, admin_user, select_for_update: bool = False) -> CouponApply:
        if select_for_update:
            apply = CouponApply.objects.select_related('odc').select_for_update().filter(id=_id).first()
        else:
            apply = CouponApply.objects.select_related('odc').filter(id=_id).first()

        if apply is None or apply.deleted:
            raise errors.TargetNotExist(message=_('申请记录不存在'))

        if admin_user.is_federal_admin():
            return apply

        if apply.service_type in [CouponApply.ServiceType.MONITOR_SITE.value, CouponApply.ServiceType.SCAN.value]:
            raise errors.AccessDenied(message=_('你没有申请记录访问权限，申请服务类型需要联邦管理员权限'))

        if not OrgDataCenterManager.is_admin_of_odc(odc_id=apply.odc_id, user_id=admin_user.id):
            raise errors.AccessDenied(message=_('你没有申请记录访问权限，需要数据中心管理员权限'))

        return apply

    def filter_user_apply_qs(
            self, user_id,
            service_type: str = None,
            status: str = None,
            start_time: datetime = None,
            end_time: datetime = None
    ):
        """
        查询user申请记录查询集
        """
        return self.filter_apply_queryset(
                service_type=service_type, status=status, start_time=start_time, end_time=end_time,
                vo_id=None, user_id=user_id, is_deleted=False
        )

    def filter_vo_apply_qs(
            self, user,
            vo_id: str,
            service_type: str = None,
            status: str = None,
            start_time: datetime = None,
            end_time: datetime = None
    ):
        """
        查询vo组申请记录查询集

        :rasies: AccessDenied, NotFound, Error
        """
        VoManager().has_vo_permission(vo_id=vo_id, user=user, read_only=True)
        return self.filter_apply_queryset(
                service_type=service_type, status=status, start_time=start_time, end_time=end_time,
                vo_id=vo_id, user_id=None, is_deleted=False
        )

    def admin_filter_apply_qs(
            self, admin_user,
            service_type: str = None,
            status: str = None,
            start_time: datetime = None,
            end_time: datetime = None,
            user_id: str = None,
            vo_id: str = None
    ):
        """
        管理员查询

        :rasies: AccessDenied, NotFound, Error
        """
        queryset = self.filter_apply_queryset(
                service_type=service_type, status=status, start_time=start_time, end_time=end_time,
                vo_id=vo_id, user_id=user_id, is_deleted=False
            )

        if admin_user.is_federal_admin():
            return queryset

        odc_ids = OrgDataCenterManager.get_admin_perm_odc_ids(user_id=admin_user.id)
        if not odc_ids:
            raise errors.AccessDenied(message=_('你没有管理员权限'))

        return queryset.filter(odc_id__in=odc_ids)

    @staticmethod
    def filter_apply_queryset(
            service_type: str = None,
            status: str = None,
            start_time: datetime = None,
            end_time: datetime = None,
            user_id: str = None,
            vo_id: str = None,
            is_deleted: bool = False
    ):
        if user_id and vo_id:
            raise errors.Error(_('查询条件不能同时包含"user_id"和"vo_id"'))

        lookups = {}
        if user_id:
            lookups['owner_type'] = OwnerType.USER.value
            lookups['user_id'] = user_id

        if vo_id:
            lookups['owner_type'] = OwnerType.VO.value
            lookups['vo_id'] = vo_id

        if service_type:
            lookups['service_type'] = service_type

        if status:
            lookups['status'] = status

        if start_time:
            lookups['creation_time__gte'] = start_time

        if end_time:
            lookups['creation_time__lte'] = end_time

        if is_deleted is not None:
            lookups['deleted'] = is_deleted

        return CouponApply.objects.filter(**lookups).order_by('-creation_time')

    @staticmethod
    def delete_apply(apply_id: str, user):
        apply = CouponApplyManager.get_perm_apply(
            _id=apply_id, user=user, select_for_update=False
        )
        apply.deleted = True
        apply.update_time = dj_timezone.now()
        apply.delete_user = user.username
        apply.save(update_fields=['deleted', 'update_time', 'delete_user'])
        return apply

    @staticmethod
    def cancel_apply(apply_id: str, user):
        with transaction.atomic():
            apply = CouponApplyManager.get_perm_apply(
                _id=apply_id, user=user, select_for_update=True
            )
            if apply.status == CouponApply.Status.PASS.value:
                raise errors.ConflictError(message=_('申请已通过'))

            if apply.status == CouponApply.Status.CANCEL.value:
                return apply

            apply.status = CouponApply.Status.CANCEL.value
            apply.update_time = dj_timezone.now()
            apply.delete_user = user.username
            apply.save(update_fields=['status', 'update_time', 'delete_user'])
            return apply

    @staticmethod
    def pending_apply(apply_id: str, admin_user):
        with transaction.atomic():
            apply = CouponApplyManager.get_admin_perm_apply(
                _id=apply_id, admin_user=admin_user, select_for_update=True
            )
            if apply.status != CouponApply.Status.WAIT.value:
                raise errors.ConflictError(message=_('只能挂起外审批状态申请'))

            apply.status = CouponApply.Status.PENDING.value
            apply.update_time = dj_timezone.now()
            apply.approver = admin_user.username
            apply.save(update_fields=['status', 'update_time', 'approver'])
            return apply

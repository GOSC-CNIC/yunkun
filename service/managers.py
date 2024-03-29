from django.utils.translation import gettext as _
from django.utils import timezone


from users.models import UserProfile
from core import errors
from core.utils import test_service_ok, InvalidServiceError
from servers.models import ApplyVmService
from .models import DataCenter, ApplyOrganization


class OrganizationApplyManager:
    model = ApplyOrganization

    @staticmethod
    def get_apply_by_id(_id: str) -> ApplyOrganization:
        """
        :return:
            None                    # not exists
            ApplyOrganization()
        """
        return OrganizationApplyManager.model.objects.select_related(
            'user').filter(id=_id, deleted=False).first()

    def get_user_apply(self, _id: str, user) -> ApplyOrganization:
        """
        查询用户的申请

        :return:
            ApplyOrganization()

        :raises: Error
        """
        apply = self.get_apply_by_id(_id)
        if apply is None:
            raise errors.OrganizationApplyNotExists()

        if apply.user_id and apply.user_id == user.id:
            return apply

        raise errors.AccessDenied(message=_('无权限访问此申请'))

    @staticmethod
    def get_apply_queryset():
        return OrganizationApplyManager.model.objects.all()

    def get_not_delete_apply_queryset(self, user=None):
        filters = {
            'deleted': False
        }
        if user:
            filters['user'] = user

        qs = self.get_apply_queryset()
        return qs.filter(**filters)

    @staticmethod
    def filter_queryset(queryset, deleted: bool = None, status: list = None):
        if deleted is not None:
            queryset = queryset.filter(deleted=deleted)

        if status:
            queryset = queryset.filter(status__in=status)

        return queryset

    def filter_user_apply_queryset(self, user, deleted: bool = None, status: list = None):
        """
        过滤用户申请查询集

        :param user: 用户对象
        :param deleted: 删除状态筛选，默认不筛选，True(已删除申请记录)，False(未删除申请记录)
        :param status: 过滤指定状态的申请记录
        """
        queryset = self.get_apply_queryset().filter(user=user)
        return self.filter_queryset(queryset=queryset, deleted=deleted, status=status)

    def admin_filter_apply_queryset(self, deleted: bool = None, status: list = None):
        """
        管理员过滤申请查询集

        :param deleted: 删除状态筛选，默认不筛选，True(已删除申请记录)，False(未删除申请记录)
        :param status: 过滤指定状态的申请记录
        """
        queryset = self.get_apply_queryset()
        return self.filter_queryset(queryset=queryset, deleted=deleted, status=status)

    def get_in_progress_apply_queryset(self, user=None):
        """
        处于申请中的申请查询集
        """
        qs = self.get_not_delete_apply_queryset(user=user)
        in_progress = [self.model.Status.WAIT, self.model.Status.PENDING]
        return qs.filter(status__in=in_progress)

    def get_in_progress_apply_count(self, user=None):
        """
        处于申请中的申请数量
        """
        qs = self.get_in_progress_apply_queryset(user=user)
        return qs.count()

    @staticmethod
    def create_apply(data: dict, user) -> ApplyOrganization:
        """
        创建一个机构申请

        :param data: dict, ApplyDataCenterSerializer.validated_data
        :param user:

        :raises: Error
        """
        apply = OrganizationApplyManager.model()
        apply.name = data.get('name')
        apply.name_en = data.get('name_en')
        apply.abbreviation = data.get('abbreviation')
        apply.independent_legal_person = data.get('independent_legal_person')
        apply.country = data.get('country')
        apply.city = data.get('city')
        apply.postal_code = data.get('postal_code')
        apply.address = data.get('address')
        apply.endpoint_vms = data.get('endpoint_vms')
        apply.endpoint_object = data.get('endpoint_object')
        apply.endpoint_compute = data.get('endpoint_compute')
        apply.endpoint_monitor = data.get('endpoint_monitor')
        apply.desc = data.get('desc')
        apply.logo_url = data.get('logo_url')
        apply.certification_url = data.get('certification_url')
        apply.user = user
        apply.longitude = data.get('longitude', 0)
        apply.latitude = data.get('latitude', 0)
        try:
            apply.save()
        except Exception as e:
            raise errors.Error.from_error(e)

        return apply

    def pending_apply(self, _id: str, user: UserProfile) -> ApplyOrganization:
        """
        挂起审批申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有访问权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply is None:
            raise errors.OrganizationApplyNotExists()

        if apply.status == apply.Status.PENDING:
            return apply
        elif apply.status != apply.Status.WAIT:
            raise errors.ConflictError(message=_('只允许挂起处于“待审批”状态的资源配额申请'))

        apply.status = apply.Status.PENDING
        try:
            apply.save(update_fields=['status'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def cancel_apply(self, _id: str, user: UserProfile) -> ApplyOrganization:
        """
        取消申请

        :raises: Error
        """
        apply = self.get_user_apply(_id=_id, user=user)

        if apply.status == apply.Status.CANCEL:
            return apply
        elif apply.status != apply.Status.WAIT:
            raise errors.ConflictError(message=_('只允取消处于“待审批”状态的资源配额申请'))

        apply.status = apply.Status.CANCEL
        try:
            apply.save(update_fields=['status'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def delete_apply(self, _id: str, user: UserProfile) -> ApplyOrganization:
        """
        删除申请

        :raises: Error
        """
        apply = self.get_user_apply(_id=_id, user=user)
        if apply.status == apply.Status.PENDING:
            raise errors.ConflictError(message=_('不能删除审批中的申请'))
        if apply.deleted:
            return apply

        apply.deleted = True
        try:
            apply.save(update_fields=['deleted'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def reject_apply(self, _id: str, user: UserProfile) -> ApplyOrganization:
        """
        拒绝申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有访问权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply is None:
            raise errors.OrganizationApplyNotExists()

        if apply.status == apply.Status.REJECT:
            return apply
        elif apply.status != apply.Status.PENDING:
            raise errors.ConflictError(message=_('只允拒绝处于“审批中”状态的资源配额申请'))

        apply.status = apply.Status.REJECT
        try:
            apply.save(update_fields=['status'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def pass_apply(self, _id: str, user: UserProfile) -> ApplyOrganization:
        """
        通过申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有访问权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply is None:
            raise errors.OrganizationApplyNotExists()

        if apply.is_pass():
            return apply
        elif apply.status != apply.Status.PENDING:
            raise errors.ConflictError(message=_('只允通过处于“审批中”状态的资源配额申请'))

        try:
            apply.do_pass_apply()
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply


class VmServiceApplyManager:
    model = ApplyVmService

    @staticmethod
    def get_apply_by_id(_id: str) -> ApplyVmService:
        """
        :return:
            None                    # not exists
            ApplyVmService()
        """
        return VmServiceApplyManager.model.objects.select_related(
            'user').filter(id=_id, deleted=False).first()

    def get_user_apply(self, _id: str, user) -> ApplyVmService:
        """
        查询用户的申请

        :return:
            ApplyVmService()

        :raises: Error
        """
        apply = self.get_apply_by_id(_id)
        if apply is None:
            raise errors.NotFound(message=_('申请不存在'))

        if apply.user_id and apply.user_id == user.id:
            return apply

        raise errors.AccessDenied(message=_('无权限访问此申请'))

    @staticmethod
    def get_apply_queryset():
        return VmServiceApplyManager.model.objects.all()

    @staticmethod
    def filter_queryset(queryset, deleted: bool = None, organization_id: str = None, status: list = None):
        if deleted is not None:
            queryset = queryset.filter(deleted=deleted)

        if organization_id:
            queryset = queryset.filter(organization__id=organization_id)

        if status:
            queryset = queryset.filter(status__in=status)

        return queryset

    def filter_user_apply_queryset(self, user, deleted: bool = None,
                                   organization_id: str = None, status: list = None):
        """
        过滤用户申请查询集

        :param user: 用户对象
        :param deleted: 删除状态筛选，默认不筛选，True(已删除申请记录)，False(未删除申请记录)
        :param organization_id: 机构id
        :param status: 过滤指定状态的申请记录
        """
        queryset = self.get_apply_queryset().filter(user=user)
        return self.filter_queryset(queryset=queryset, deleted=deleted,
                                    organization_id=organization_id, status=status)

    def admin_filter_apply_queryset(self, deleted: bool = None,
                                    organization_id: str = None, status: list = None):
        """
        管理员过滤申请查询集

        :param deleted: 删除状态筛选，默认不筛选，True(已删除申请记录)，False(未删除申请记录)
        :param organization_id: 机构id
        :param status: 过滤指定状态的申请记录
        """
        queryset = self.get_apply_queryset()
        return self.filter_queryset(queryset=queryset, deleted=deleted,
                                    organization_id=organization_id, status=status)

    def get_not_delete_apply_queryset(self, user=None):
        filters = {
            'deleted': False
        }
        if user:
            filters['user'] = user

        qs = self.get_apply_queryset()
        return qs.filter(**filters)

    def get_in_progress_apply_queryset(self, user=None):
        """
        处于申请中的申请查询集
        """
        qs = self.get_not_delete_apply_queryset(user=user)
        in_progress = [self.model.Status.WAIT, self.model.Status.PENDING,
                       self.model.Status.FIRST_PASS, self.model.Status.TEST_PASS]
        return qs.filter(status__in=in_progress)

    def get_in_progress_apply_count(self, user=None):
        """
        处于申请中的申请数量
        """
        qs = self.get_in_progress_apply_queryset(user=user)
        return qs.count()

    @staticmethod
    def create_apply(data: dict, user) -> ApplyVmService:
        """
        创建一个服务接入申请

        :param data: dict, ApplyVmServiceSerializer.validated_data
        :param user:
        :return:
            ApplyVmService()

        :raises: Error
        """
        apply_service = VmServiceApplyManager.model()
        organization_id = data.get('organization_id')
        if not organization_id:
            raise errors.NoCenterBelongToError()

        center = DataCenter.objects.filter(id=organization_id).first()
        if center is None:
            raise errors.OrganizationNotExists()

        apply_service.organization_id = organization_id

        service_type = data.get('service_type')
        if service_type not in apply_service.ServiceType.values:
            raise errors.BadRequest(message='service_type值无效')

        cloud_type = data.get('cloud_type')
        if cloud_type not in apply_service.CLoudType.values:
            raise errors.BadRequest(message='cloud_type值无效')

        apply_service.user = user
        apply_service.service_type = service_type
        apply_service.cloud_type = cloud_type
        apply_service.name = data.get('name')
        apply_service.name_en = data.get('name_en')
        apply_service.endpoint_url = data.get('endpoint_url')
        apply_service.region = data.get('region', '')
        apply_service.api_version = data.get('api_version', '')
        apply_service.username = data.get('username', '')
        apply_service.set_password(data.get('password', ''))
        apply_service.project_name = data.get('project_name', '')
        apply_service.project_domain_name = data.get('project_domain_name', '')
        apply_service.user_domain_name = data.get('user_domain_name', '')
        apply_service.remarks = data.get('remarks', '')
        apply_service.need_vpn = data.get('need_vpn')
        apply_service.vpn_endpoint_url = data.get('vpn_endpoint_url', '')
        apply_service.vpn_api_version = data.get('vpn_api_version', '')
        apply_service.vpn_username = data.get('vpn_username', '')
        apply_service.set_vpn_password(data.get('vpn_password', ''))
        apply_service.longitude = data.get('longitude', 0)
        apply_service.latitude = data.get('latitude', 0)
        apply_service.contact_person = data.get('contact_person', '')
        apply_service.contact_email = data.get('contact_email', '')
        apply_service.contact_telephone = data.get('contact_telephone', '')
        apply_service.contact_fixed_phone = data.get('contact_fixed_phone', '')
        apply_service.contact_address = data.get('contact_address', '')
        apply_service.logo_url = data.get('logo_url', '')

        try:
            apply_service.save()
        except Exception as e:
            raise errors.Error.from_error(e)

        return apply_service

    def cancel_apply(self, _id: str, user: UserProfile) -> ApplyVmService:
        """
        取消申请

        :raises: Error
        """
        apply = self.get_user_apply(_id=_id, user=user)
        if apply.status == apply.Status.CANCEL:
            return apply

        if apply.status != apply.Status.WAIT:
            raise errors.ConflictError(message=_('不能取消待审批状态的申请'))

        apply.status = apply.Status.CANCEL
        try:
            apply.save(update_fields=['status'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def pending_apply(self, _id: str, user: UserProfile) -> ApplyVmService:
        """
        挂起申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有审批权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply.status == apply.Status.PENDING:
            return apply

        if apply.status != apply.Status.WAIT:
            raise errors.ConflictError(message=_('不能挂起处于待审批状态的申请'))

        apply.status = apply.Status.PENDING
        apply.approve_time = timezone.now()
        try:
            apply.save(update_fields=['status', 'approve_time'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def first_reject_apply(self, _id: str, user: UserProfile) -> ApplyVmService:
        """
        初审拒绝申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有审批权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply.status == apply.Status.FIRST_REJECT:
            return apply

        if apply.status != apply.Status.PENDING:
            raise errors.ConflictError(message=_('只能拒绝处于挂起状态的申请'))

        apply.status = apply.Status.FIRST_REJECT
        apply.approve_time = timezone.now()
        try:
            apply.save(update_fields=['status', 'approve_time'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def first_pass_apply(self, _id: str, user: UserProfile) -> ApplyVmService:
        """
        初审通过申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有审批权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply.status == apply.Status.FIRST_PASS:
            return apply

        if apply.status != apply.Status.PENDING:
            raise errors.ConflictError(message=_('只能审批通过处于挂起状态的申请'))

        apply.status = apply.Status.FIRST_PASS
        apply.approve_time = timezone.now()
        try:
            apply.save(update_fields=['status', 'approve_time'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def test_apply(self, _id: str, user: UserProfile) -> (ApplyVmService, str):
        """
        测试申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有审批权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply.status not in [apply.Status.FIRST_PASS, apply.Status.TEST_PASS, apply.Status.TEST_FAILED]:
            raise errors.ConflictError(message=_('初审通过的申请才可以测试'))

        test_msg = ''
        test_result = apply.Status.TEST_PASS
        service = apply.convert_to_service()
        try:
            test_service_ok(service=service)
        except InvalidServiceError as exc:
            test_result = apply.Status.TEST_FAILED
            test_msg = str(exc)

        apply.status = test_result
        try:
            apply.save(update_fields=['status'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply, test_msg

    def reject_apply(self, _id: str, user: UserProfile) -> ApplyVmService:
        """
        拒绝申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有审批权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply.status == apply.Status.REJECT:
            return apply

        if apply.status == apply.Status.PASS:
            raise errors.ConflictError(message=_('不能再次审批已完成审批过程的申请'))

        if apply.status not in [apply.Status.FIRST_PASS, apply.Status.TEST_PASS, apply.Status.TEST_FAILED]:
            raise errors.ConflictError(message=_('只能审批通过初审的申请'))

        apply.status = apply.Status.REJECT
        apply.approve_time = timezone.now()
        try:
            apply.save(update_fields=['status', 'approve_time'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def pass_apply(self, _id: str, user: UserProfile) -> ApplyVmService:
        """
        通过申请

        :raises: Error
        """
        if not user.is_federal_admin():
            raise errors.AccessDenied(message=_('你没有审批权限，需要联邦管理员权限'))

        apply = self.get_apply_by_id(_id=_id)
        if apply.status == apply.Status.PASS:
            return apply

        if apply.status == apply.Status.REJECT:
            raise errors.ConflictError(message=_('不能再次审批已完成审批过程的申请'))

        if apply.status not in [apply.Status.FIRST_PASS, apply.Status.TEST_PASS, apply.Status.TEST_FAILED]:
            raise errors.ConflictError(message=_('只能审批通过初审的申请'))

        try:
            apply.do_pass_apply()
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

    def delete_apply(self, _id: str, user: UserProfile) -> ApplyVmService:
        """
        删除申请

        :raises: Error
        """
        apply = self.get_user_apply(_id=_id, user=user)
        if apply.status in [apply.Status.PENDING, apply.Status.FIRST_PASS, apply.Status.TEST_PASS]:
            raise errors.ConflictError(message=_('不能删除处于审批过程中的申请'))

        if apply.deleted:
            return apply

        apply.deleted = True
        try:
            apply.save(update_fields=['deleted'])
        except Exception as e:
            raise errors.APIException(message='更新数据库失败' + str(e))

        return apply

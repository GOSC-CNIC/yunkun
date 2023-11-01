from django.utils.translation import gettext as _
from api.viewsets import NormalGenericViewSet
from link.managers.userrole_manager import UserRoleWrapper
from link.managers.distriframeport_manager import DistriFramePortManager
from core import errors

class DistriFramePortHandler:
    @staticmethod
    def list_distriframeport(view: NormalGenericViewSet, request):
        ur_wrapper = UserRoleWrapper(user=request.user)
        if not ur_wrapper.has_read_permission():
            return view.exception_response(errors.AccessDenied(message=_('你没有科技网链路管理功能的可读权限')))
        try:
            params = DistriFramePortHandler._list_validate_params(request=request)
        except errors.Error as exc:
            return view.exception_response(exc)
        queryset = DistriFramePortManager.get_queryset().order_by('distribution_frame', 'row', 'col')
        try:
            datas = view.paginate_queryset(queryset)
            serializer = view.get_serializer(instance=datas, many=True)
            return view.get_paginated_response(serializer.data)
        except errors.Error as exc:
            return view.exception_response(exc)

    @staticmethod
    def _list_validate_params(request):
        pass


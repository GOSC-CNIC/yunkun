from django.utils.translation import gettext as _
from api.viewsets import NormalGenericViewSet
from link.managers.userrole_manager import UserRoleWrapper
from link.managers.distriframe_manager import DistriFrameManager
from core import errors


class DistriFrameHandler:
    @staticmethod
    def list_distriframe(view: NormalGenericViewSet, request):
        ur_wrapper = UserRoleWrapper(user=request.user)
        if not ur_wrapper.has_read_permission():
            return view.exception_response(errors.AccessDenied(message=_('你没有科技网链路管理功能的可读权限')))
        try:
            params = DistriFrameHandler._list_validate_params(request=request)
        except errors.Error as exc:
            return view.exception_response(exc)
        queryset = DistriFrameManager.get_queryset()
        try:
            datas = view.paginate_queryset(queryset)
            serializer = view.get_serializer(instance=datas, many=True)
            return view.get_paginated_response(serializer.data)
        except errors.Error as exc:
            return view.exception_response(exc)

    @staticmethod
    def _list_validate_params(request):
        pass

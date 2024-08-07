from rest_framework.permissions import BasePermission
from apps.app_alert.utils.utils import hash_md5

from apps.app_global.configs_manager import IPAccessWhiteListManager
from utils.iprestrict import IPRestrictor


class AlertAPIIPRestrictor(IPRestrictor):
    """
    流量模块 IP 白名单
    """

    def load_ip_rules(self):
        return IPAccessWhiteListManager.get_module_ip_whitelist(
            module_name=IPAccessWhiteListManager.ModuleName.ALERT.value)

    @staticmethod
    def clear_cache():
        IPAccessWhiteListManager.clear_cache()

    @staticmethod
    def add_ip_rule(ip_value: str):
        return IPAccessWhiteListManager.add_whitelist_obj(
            module_name=IPAccessWhiteListManager.ModuleName.ALERT.value, ip_value=ip_value)

    @staticmethod
    def get_remote_ip(request):
        """
        获取客户端的ip地址和代理ip

            X-Forwarded-For 可能伪造，需要在服务一级代理防范处理
            比如nginx：
            uwsgi_param X-Forwarded-For $remote_addr;     不能使用 $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-For $remote_addr;     不能使用 $proxy_add_x_forwarded_for;

        :return: (
            str,    # 客户端真实ip地址
            list    # 经过的代理ip地址列表
        )
        """
        if 'X-Forwarded-For' in request.META:
            h = request.META.get('X-Forwarded-For')
        elif 'HTTP_X-Forwarded-For' in request.META:
            h = request.META.get('HTTP_X-Forwarded-For')
        else:
            # 标头 X-Forwarded-For 不存在
            # 没有经过代理时， REMOTE_ADDR是客户端地址
            # 经过代理时，socket方式时， REMOTE_ADDR是客户端地址；http方式时，REMOTE_ADDR是代理地址（如果代理到本机，获取的ip可能是127.0.0.1）
            return request.META.get('REMOTE_ADDR', ''), []

        ips = h.split(',')
        ips = [i.strip(' ') for i in ips]
        return ips.pop(0), ips

    def check_restricted(self, request):
        """
        :return:
            ip: str
        :raises: AccessDenied
        """
        client_ip, proxy_ips = self.get_remote_ip(request)
        self.is_restricted(client_ip=client_ip)
        return client_ip


class ReceiverPermission(BasePermission):
    """
    Allow ip whitelist
    """

    def has_permission(self, request, view):
        AlertAPIIPRestrictor().check_restricted(request=request)
        return True

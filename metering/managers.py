from datetime import date

from django.utils.translation import gettext as _
from django.db.models import Subquery, Sum, Count

from core import errors
from service.managers import ServiceManager
from servers.managers import ServerManager
from servers.models import Server, ServerArchive
from vo.managers import VoManager
from utils.model import OwnerType
from .models import MeteringServer
from users.models import UserProfile
from vo.models import VirtualOrganization
from service.models import ServiceConfig


class MeteringServerManager:
    @staticmethod
    def get_metering_server_queryset():
        return MeteringServer.objects.all()

    def filter_user_server_metering(
            self, user,
            service_id: str = None,
            server_id: str = None,
            date_start: date = None,
            date_end: date = None
    ):
        """
        查询用户云主机计量用量账单查询集
        """
        return self.filter_server_metering_queryset(
            service_id=service_id, server_id=server_id, date_start=date_start,
            date_end=date_end, user_id=user.id
        )

    def filter_vo_server_metering(
            self, user,
            vo_id: str,
            service_id: str = None,
            server_id: str = None,
            date_start: date = None,
            date_end: date = None
    ):
        """
        查询vo组云主机计量用量账单查询集

        :rasies: AccessDenied, NotFound, Error
        """
        VoManager().get_has_read_perm_vo(vo_id=vo_id, user=user)
        return self.filter_server_metering_queryset(
            service_id=service_id, server_id=server_id, date_start=date_start,
            date_end=date_end, vo_id=vo_id
        )

    def filter_server_metering_by_admin(    
            self, user,
            service_id: str = None,
            server_id: str = None,
            date_start: date = None,
            date_end: date = None,
            vo_id: str = None,
            user_id: str = None
    ):
        """
        查询vo组云主机计量用量账单查询集

        :rasies: AccessDenied, NotFound, Error
        """
        if user.is_federal_admin():     
            return self.filter_server_metering_queryset(
                service_id=service_id, server_id=server_id, date_start=date_start, date_end=date_end,
                vo_id=vo_id, user_id=user_id
            )

        if server_id:                    
            server_or_archieve = ServerManager.get_server_or_archive(server_id=server_id) 
            
            if server_or_archieve is None:         
                return MeteringServer.objects.none()
            
            if service_id:      
                if service_id != server_or_archieve.service_id:
                    return MeteringServer.objects.none()
            else:              
                service_id = server_or_archieve.service_id

        if service_id:      
            service = ServiceManager.get_service_if_admin(user=user, service_id=service_id)
            if service is None:
                raise errors.AccessDenied(message=_('您没有指定服务的访问权限'))

        queryset = self.filter_server_metering_queryset(
                service_id=service_id, server_id=server_id, date_start=date_start, date_end=date_end,
                vo_id=vo_id, user_id=user_id
            )

        if not service_id and not server_id:
            qs = ServiceManager.get_all_has_perm_service(user)
            subq = Subquery(qs.values_list('id', flat=True))
            queryset = queryset.filter(service_id__in=subq)

        return queryset

    def filter_server_metering_queryset(       
            self, service_id: str = None,
            server_id: str = None,
            date_start: date = None,
            date_end: date = None,
            user_id: str = None,
            vo_id: str = None
    ):
        """
        查询云主机计量用量账单查询集
        """
        if user_id and vo_id:
            raise errors.Error(_('云主机计量用量账单查询集查询条件不能同时包含"user_id"和"vo_id"'))

        lookups = {}
        if date_start:
            lookups['date__gte'] = date_start

        if date_end:
            lookups['date__lte'] = date_end

        if service_id:
            lookups['service_id'] = service_id

        if server_id:
            lookups['server_id'] = server_id

        if user_id:
            lookups['owner_type'] = OwnerType.USER.value
            lookups['user_id'] = user_id

        if vo_id:
            lookups['owner_type'] = OwnerType.VO.value
            lookups['vo_id'] = vo_id

        queryset = self.get_metering_server_queryset()      
        return queryset.filter(**lookups).order_by('-creation_time')    

    def aggregate_server_metering_by_uuid_by_admin(
            self, user,
            date_start: date = None,
            date_end: date = None,
            user_id: str = None,
            service_id: str = None,
            vo_id: str = None
    ):
        """
            管理员获取以server_id聚合的查询集
        """
        if user.is_federal_admin():
            queryset = self.filter_server_metering_queryset(
                service_id=service_id, date_start=date_start, date_end=date_end, user_id=user_id, vo_id=vo_id
            )
            return self.aggregate_queryset_by_server(queryset)

        if service_id:
            service = ServiceManager.get_service_if_admin(user=user, service_id=service_id)
            if service is None:
                raise errors.AccessDenied(message=_('您没有指定服务的访问权限'))

        queryset = self.filter_server_metering_queryset(
            service_id=service_id, date_start=date_start, date_end=date_end, user_id=user_id, vo_id=vo_id
        )

        if not service_id:
            qs = ServiceManager.get_all_has_perm_service(user)  
            subq = Subquery(qs.values_list('id', flat=True))   
            queryset = queryset.filter(service_id__in=subq)

        return self.aggregate_queryset_by_server(queryset)

    def aggregate_server_metering_by_uuid_by_user(
            self, user,
            date_start: date = None,
            date_end: date = None,
            service_id: str = None
    ):
        """
        普通用户获取自己名下以server_id聚合的查询集
        """
        queryset = self.filter_server_metering_queryset(
            service_id=service_id, date_start=date_start,
            date_end=date_end, user_id=user.id
        )
        return self.aggregate_queryset_by_server(queryset)

    def aggregate_server_metering_by_uuid_by_vo(
            self, user,
            date_start: date = None,
            date_end: date = None,
            service_id: str = None,
            vo_id: str = None
    ):
        """
        指定vo组下以server_id聚合的查询集
        """
        VoManager().get_has_read_perm_vo(vo_id=vo_id, user=user)
        queryset = self.filter_server_metering_queryset(
            service_id=service_id, date_start=date_start,
            date_end=date_end, vo_id=vo_id
        )
        return self.aggregate_queryset_by_server(queryset)

    @staticmethod
    def aggregate_queryset_by_server(queryset):
        """
        聚合云主机计量数据
        """
        queryset = queryset.values('server_id').annotate(   
            total_cpu_hours=Sum('cpu_hours'),
            total_ram_hours=Sum('ram_hours'),
            total_disk_hours=Sum('disk_hours'),
            total_public_ip_hours=Sum('public_ip_hours'),
            total_original_amount=Sum('original_amount'),
            total_trade_amount=Sum('trade_amount')
        ).order_by('server_id')

        return queryset

    @staticmethod
    def aggregate_by_server_mixin_data(data: list):
        """
        按server id聚合数据分页后混合其他数据
        """
        server_ids = [i['server_id'] for i in data]
        servers = Server.objects.filter(id__in=server_ids).values('id', 'ipv4', 'ram', 'vcpus', 'service__name')
        archives = ServerArchive.objects.filter(
            server_id__in=server_ids, archive_type=ServerArchive.ArchiveType.ARCHIVE.value
        ).values('server_id', 'ipv4', 'ram', 'vcpus', 'service__name')

        server_dict = {}
        for s in servers:
            d = {
                'service_name': s.pop('service__name', None),
                'server': s
            }
            server_dict[s['id']] = d

        for a in archives:
            server_id = a['id'] = a.pop('server_id', None)
            if server_id and server_id not in server_dict:
                d = {
                    'service_name': a.pop('service__name', None),
                    'server': a
                }
                server_dict[server_id] = d

        for i in data:
            i: dict
            sid = i['server_id']
            if sid in server_dict:
                i.update(server_dict[sid])
            else:
                i['service_name'] = None
                i['server'] = None

        return data

    def aggregate_server_metering_by_userid_by_admin(
            self, user,
            date_start: date = None,
            date_end: date = None,
            service_id: str = None,
    ):
        """
            管理员获取以user_id聚合的查询集
        """
        queryset = self.filter_server_metering_queryset(   
            date_start=date_start, date_end=date_end, service_id=service_id
        ).filter(owner_type=OwnerType.USER.value)             
               
        if user.is_federal_admin():     
            return self.aggregate_queryset_by_user(queryset)    
        
        if service_id:     
            service = ServiceManager.get_service_if_admin(user=user, service_id=service_id)
            if service is None:
                raise errors.AccessDenied(message=_('您没有指定服务的访问权限'))
        else:               
            qs = ServiceManager.get_all_has_perm_service(user)  
            subq = Subquery(qs.values_list('id', flat=True))   
            queryset = queryset.filter(service_id__in=subq)

        return self.aggregate_queryset_by_user(queryset)

    @staticmethod
    def aggregate_queryset_by_user(queryset):
        """
        聚合用户的云主机计量数据
        """
        queryset = queryset.values('user_id').annotate(
            total_original_amount=Sum('original_amount'),
            total_trade_amount=Sum('trade_amount'),
            total_server=Count('server_id', distinct=True),
        ).order_by('user_id')

        return queryset

    @staticmethod
    def aggregate_by_user_mixin_data(data: list):
        """
        按user id聚合数据分页后混合其他数据
        """
        user_ids = [i['user_id'] for i in data]     
        users = UserProfile.objects.filter(id__in=user_ids).values('id', 'username', 'company')

        user_dict = {}
        for user in users:
            user_id = user['id']
            u = {
                'user': user
            }
            user_dict[user_id] = u

        for i in data:
            i: dict
            i.update(user_dict[i['user_id']])

        return data

    def aggregate_server_metering_by_void_by_admin(
            self, user,
            date_start: date = None,
            date_end: date = None,
            service_id: str = None,
    ):
        """
            管理员获取以vo_id聚合的查询集
        """
        queryset = self.filter_server_metering_queryset(   
            date_start=date_start, date_end=date_end, service_id=service_id
        ).filter(owner_type=OwnerType.VO.value)              
        
        if user.is_federal_admin():     
            return self.aggregate_queryset_by_vo(queryset)   
        
        if service_id:      
            service = ServiceManager.get_service_if_admin(user=user, service_id=service_id)
            if service is None:
                raise errors.AccessDenied(message=_('您没有指定服务的访问权限'))
        else:       
            qs = ServiceManager.get_all_has_perm_service(user)  
            subq = Subquery(qs.values_list('id', flat=True))   
            queryset = queryset.filter(service_id__in=subq)

        return self.aggregate_queryset_by_vo(queryset)

    @staticmethod
    def aggregate_queryset_by_vo(queryset):
        """
        聚合vo组的云主机计量数据
        """
        queryset = queryset.values('vo_id').annotate(
            total_original_amount=Sum('original_amount'),
            total_trade_amount=Sum('trade_amount'),
            total_server=Count('server_id', distinct=True),
        ).order_by('vo_id')

        return queryset

    @staticmethod
    def aggregate_by_vo_mixin_data(data: list):
        """
        按vo id聚合数据分页后混合其他数据
        """
        vo_ids = [i['vo_id'] for i in data]    
        vos = VirtualOrganization.objects.filter(id__in=vo_ids).values('id', 'name', 'company')

        vo_dict = {}
        for vo in vos:
            vo_id = vo['id']
            v = {
                'vo': vo
            }
            vo_dict[vo_id] = v

        for i in data:
            i: dict
            i.update(vo_dict[i['vo_id']])

        return data
    
    def aggregate_server_metering_by_serviceid_by_admin(
            self, user,
            date_start: date = None,
            date_end: date = None,
    ):
        """
            管理员获取以service_id聚合的查询集
        """
        queryset = self.filter_server_metering_queryset(    
            date_start=date_start, date_end=date_end, 
        )      
        
        if user.is_federal_admin():     
            return self.aggregate_queryset_by_service(queryset)    
        
        qs = ServiceManager.get_all_has_perm_service(user)  
        subq = Subquery(qs.values_list('id', flat=True))   
        queryset = queryset.filter(service_id__in=subq)

        return self.aggregate_queryset_by_service(queryset)

    @staticmethod
    def aggregate_queryset_by_service(queryset):
        """
        聚合服务节点的云主机计量数据
        """
        queryset = queryset.values('service_id').annotate(
            total_original_amount=Sum('original_amount'),
            total_trade_amount=Sum('trade_amount'),
            total_server=Count('server_id', distinct=True),
        ).order_by('service_id')

        return queryset

    @staticmethod
    def aggregate_by_service_mixin_data(data: list):
        """
        按service id聚合数据分页后混合其他数据
        """
        service_ids = [i['service_id'] for i in data]    
        services = ServiceConfig.objects.filter(id__in=service_ids).values('id', 'name')

        service_dict = {}
        for service in services:
            service_id = service['id']
            s = {
                'service': service
            }
            service_dict[service_id] = s

        for i in data:
            i: dict
            i.update(service_dict[i['service_id']])

        return data
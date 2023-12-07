import datetime
import ipaddress
from urllib import parse

from django.urls import reverse
from django.utils import timezone as dj_timezone

from utils.test import get_or_create_user, MyAPITransactionTestCase, get_or_create_organization
from ..managers import UserIpamRoleWrapper, IPv4RangeManager
from ..models import OrgVirtualObject, IPv4Range, IPv4Address


class IPv4AddressTests(MyAPITransactionTestCase):
    def setUp(self):
        self.user1 = get_or_create_user(username='tom@qq.com')
        self.user2 = get_or_create_user(username='lisi@cnic.cn')

    def test_remark(self):
        org1 = get_or_create_organization(name='org1')
        virt_obj1 = OrgVirtualObject(name='org virt obj1', organization=org1, creation_time=dj_timezone.now())
        virt_obj1.save(force_insert=True)

        nt = dj_timezone.now()
        ip_range1 = IPv4RangeManager.create_ipv4_range(
            name='已分配1', start_ip='127.0.0.1', end_ip='127.0.0.255', mask_len=24, asn=66,
            create_time=nt, update_time=nt, status_code=IPv4Range.Status.ASSIGNED.value,
            org_virt_obj=virt_obj1, assigned_time=nt, admin_remark='admin1', remark='remark1'
        )
        nt = dj_timezone.now()
        ip_range2 = IPv4RangeManager.create_ipv4_range(
            name='预留2', start_ip='159.0.1.1', end_ip='159.0.2.255', mask_len=22, asn=88,
            create_time=nt, update_time=nt, status_code=IPv4Range.Status.RESERVED.value,
            org_virt_obj=virt_obj1, assigned_time=nt, admin_remark='admin remark2', remark='remark2'
        )

        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': 'tes6'})
        response = self.client.post(base_url)
        self.assertEqual(response.status_code, 401)

        # ipv4
        self.client.force_login(self.user1)
        response = self.client.post(base_url)
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=response)

        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': -1})
        response = self.client.post(base_url)
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=response)
        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': 2**32})
        response = self.client.post(base_url)
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=response)

        # remark
        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('10.8.8.6'))})
        response = self.client.post(base_url)
        self.assertErrorResponse(status_code=400, code='BadRequest', response=response)

        query = parse.urlencode(query={'admin_remark': 'ss', 'as-admin': ''})
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        # 分配机构管理员
        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('10.8.8.6'))})
        query = parse.urlencode(query={'remark': 'test'})
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('127.0.0.1'))})
        query = parse.urlencode(query={'remark': 'test'})
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        uirw = UserIpamRoleWrapper(self.user1)
        uirw.user_role = uirw.get_or_create_user_ipam_role()
        uirw.user_role.organizations.add(org1)
        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('127.0.0.1'))})
        query = parse.urlencode(query={'remark': 'test'})
        response = self.client.post(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertKeysIn(['id', 'ip_address', 'remark'], response.data)
        self.assertNotIn('admin_remark', response.data)

        ip_addr: IPv4Address = IPv4Address.objects.first()
        self.assertEqual(ip_addr.ip_address, int(ipaddress.IPv4Address('127.0.0.1')))
        self.assertEqual(ip_addr.remark, 'test')
        self.assertEqual(ip_addr.admin_remark, '')

        query = parse.urlencode(query={'remark': 'test888'})
        response = self.client.post(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        ip_addr.refresh_from_db()
        self.assertEqual(ip_addr.remark, 'test888')
        self.assertEqual(ip_addr.admin_remark, '')

        query = parse.urlencode(query={'admin_remark': 'testadmin'})
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=400, code='BadRequest', response=response)

        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('159.0.1.1'))})
        query = parse.urlencode(query={'remark': 'test'})
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('66.0.0.1'))})
        query = parse.urlencode(query={'remark': 'test'})
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        # ---- test kjw admin -----
        uirw.user_role.organizations.remove(org1)

        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('66.0.0.1'))})
        query = parse.urlencode(query={'remark': 'test', 'as-admin': ''})
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        uirw.user_role.is_readonly = True
        uirw.user_role.save(update_fields=['is_readonly'])
        response = self.client.post(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        uirw.user_role.is_admin = True
        uirw.user_role.save(update_fields=['is_admin'])

        query = parse.urlencode(query={'remark': 'test88', 'admin_remark': 'admin remark88', 'as-admin': ''})
        response = self.client.post(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertKeysIn(['id', 'ip_address', 'remark', 'admin_remark'], response.data)
        ip_addr = IPv4Address.objects.get(ip_address=int(ipaddress.IPv4Address('66.0.0.1')))
        self.assertEqual(ip_addr.remark, 'test88')
        self.assertEqual(ip_addr.admin_remark, 'admin remark88')

        query = parse.urlencode(query={'remark': '测试test', 'as-admin': ''})
        response = self.client.post(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        ip_addr.refresh_from_db()
        self.assertEqual(ip_addr.remark, '测试test')
        self.assertEqual(ip_addr.admin_remark, 'admin remark88')

        query = parse.urlencode(query={'admin_remark': '测试66', 'as-admin': ''})
        response = self.client.post(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        ip_addr.refresh_from_db()
        self.assertEqual(ip_addr.remark, '测试test')
        self.assertEqual(ip_addr.admin_remark, '测试66')

        base_url = reverse('ipam-api:ipam-ipv4address-remark', kwargs={'ipv4': int(ipaddress.IPv4Address('16.6.6.8'))})
        query = parse.urlencode(query={'remark': 'test88', 'admin_remark': 'admin remark88', 'as-admin': ''})
        response = self.client.post(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertKeysIn(['id', 'ip_address', 'remark', 'admin_remark'], response.data)
        ip_addr = IPv4Address.objects.get(ip_address=int(ipaddress.IPv4Address('16.6.6.8')))
        self.assertEqual(ip_addr.remark, 'test88')
        self.assertEqual(ip_addr.admin_remark, 'admin remark88')
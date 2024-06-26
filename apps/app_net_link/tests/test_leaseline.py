import json
from urllib import parse
from datetime import date

from django.urls import reverse

from utils.test import get_or_create_user, MyAPITransactionTestCase
from apps.app_net_link.managers.link import LeaseLineManager, LinkManager
from apps.app_net_link.managers.common import NetLinkUserRoleWrapper
from apps.app_net_link.models import LeaseLine, Element, Link
from apps.app_net_link.permissions import LinkIPRestrictor


class LeaseLineTests(MyAPITransactionTestCase):
    def setUp(self):
        self.user1 = get_or_create_user(username='tom@qq.com')
        self.user2 = get_or_create_user(username='lisi@cnic.cn')
        self.user3 = get_or_create_user(username='zhangs@cnic.cn')

        u2_roler = NetLinkUserRoleWrapper(self.user2)
        u2_roler.user_role = u2_roler.get_or_create_user_role()
        u2_roler.set_link_readonly(True)

        u3_roler = NetLinkUserRoleWrapper(self.user3)
        u3_roler.user_role = u3_roler.get_or_create_user_role()
        u3_roler.set_link_admin(True)

        LinkIPRestrictor.add_ip_rule(ip_value='0.0.0.0/0')
        LinkIPRestrictor.clear_cache()

        self.leaseline1 = LeaseLineManager.create_leaseline(
            private_line_number='00645713',
            lease_line_code='天津空港物流加工区西七道32号',
            line_username='天津工业生物技术研究所',
            endpoint_a='北京市海淀区中关村南四街4号',
            endpoint_z='天津空港物流加工区西七道32号',
            line_type='接入网',
            cable_type='MSTP电路',
            bandwidth=400,
            length=None,
            provider='联通（北京）',
            enable_date=date.fromisoformat('2021-10-05'),
            is_whithdrawal=False,
            money=300.20,
            remarks='电路代号：北京天津ANE0365NP，起租时间2010.08.16,2014-1-1日由30M扩容为100M，2017年7月28日'
                    '由100M扩容至150M,2019年8月由150M升级为250M.20201017升级到400M。'
        )
        self.leaseline2 = LeaseLineManager.create_leaseline(
            private_line_number='26001927719',
            lease_line_code='',
            line_username='国家气象中心云岗通信台',
            endpoint_a='北京市海淀区中关村南四街4号',
            endpoint_z='',
            line_type='接入网',
            cable_type='MSTP电路',
            bandwidth=170,
            length=None,
            provider='移动（北京）',
            enable_date=date.fromisoformat('2014-11-22'),
            is_whithdrawal=True,
            money=300.20,
            remarks=''
        )

    def test_creat(self):
        base_url = reverse('net_link-api:link-leaseline-list')
        data = json.dumps({
            'private_line_number': '510GXN12603174',
            'lease_line_code': '0F0001NP',
            'line_username': '广州联通互联互通',
            'endpoint_a': '广州市天河乐意居广州化学所',
            'endpoint_z': '广州联通科学城2数据机房',
            'line_type': '骨干网',
            'cable_type': '裸光纤',
            'bandwidth': '400',
            'length': '',
            'provider': '联通（北京）',
            'enable_date': '2023-06-15',
            'is_whithdrawal': 'false',
            'money': '300.20',
            'remarks': '电路编号：中科院广州化学有限公司-科学城2数据机房0F0001NP'
        })

        # user role 
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.client.force_login(self.user1)
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        self.client.force_login(self.user2)
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        self.client.force_login(self.user3)
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # data
        leaseline = response.data
        self.assertKeysIn([
            'id', 'private_line_number', 'lease_line_code', 'line_username', 'endpoint_a', 'endpoint_z',
            'line_type', 'cable_type', 'bandwidth', 'length', 'provider', 'enable_date', 'is_whithdrawal',
            'money', 'remarks', 'is_linked', 'element_id'
        ], leaseline)
        self.assertEqual(response.data['private_line_number'], '510GXN12603174')
        self.assertEqual(response.data['lease_line_code'], '0F0001NP')
        leaseline = LeaseLine.objects.filter(private_line_number='510GXN12603174').first()
        self.assertEqual(leaseline.element.object_type, Element.Type.LEASE_LINE)
        self.assertEqual(leaseline.element.object_id, leaseline.id)
        self.assertEqual(leaseline.element.element_leaseline.id, leaseline.id)

    def test_list(self):
        # user role 
        base_url = reverse('net_link-api:link-leaseline-list')
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 401)
        self.client.force_login(self.user1)
        response = self.client.get(base_url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        self.client.force_login(self.user2)
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)
        self.client.force_login(self.user3)
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)

        # data
        self.assertKeysIn(['count', 'page_num', 'page_size', 'results'], response.data)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['page_num'], 1)
        self.assertEqual(response.data['page_size'], 20)
        self.assertEqual(len(response.data['results']), 2)
        leaseline = response.data['results'][0]
        self.assertKeysIn([
            'id', 'private_line_number', 'lease_line_code', 'line_username', 'endpoint_a', 'endpoint_z',
            'line_type', 'cable_type', 'bandwidth', 'length', 'provider', 'enable_date', 'is_whithdrawal',
            'money', 'remarks', 'is_linked', 'element_id'
        ], leaseline)

        # query "page"、"page_size"
        query = parse.urlencode(query={'page': 2, 'page_size': 1})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['page_num'], 2)
        self.assertEqual(response.data['page_size'], 1)
        self.assertEqual(len(response.data['results']), 1)

        # query 'is_whithdrawal'
        query = parse.urlencode(query={'is_whithdrawal': '1'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=response)
        query = parse.urlencode(query={'is_whithdrawal': 'true'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['is_whithdrawal'], True)

        # query "search"
        query = parse.urlencode(query={'search': '南京'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        query = parse.urlencode(query={'search': '天津空港物流'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        query = parse.urlencode(query={'search': '天津空港物流', 'is_whithdrawal': 'true'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        # query "enable_date"
        query = parse.urlencode(query={'enable_date_start': '2017.07.14'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=response)
        query = parse.urlencode(query={'enable_date_start': '2003-07-14'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        query = parse.urlencode(query={'enable_date_start': '2017-07-14'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        query = parse.urlencode(query={'enable_date_start': '2023-10-26'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        query = parse.urlencode(query={'enable_date_start': '2023-10-26', 'enable_date_end': '2021-10-26'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=response)
        query = parse.urlencode(query={'enable_date_start': '2003-07-14', 'enable_date_end': '2017-07-14'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

        # verify is_linked
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['is_linked'], False)
        self.assertEqual(response.data['results'][1]['is_linked'], False)
        link = LinkManager.create_link(
            number="KY23092702",
            user="空天院-中国遥感卫星地面站",
            endpoint_a="空天院新技术园区B座A301机房，王萌13811835852",
            endpoint_z="海淀区丰贤东路5号，中国资源卫星应用中心一期楼三层机房A301，吴郡13811754165，光缆施工联系沈老师13810428468，布跳线联系徐工13521066224",
            bandwidth=None,
            description="中国遥感卫星地面站至中国资源卫星应用中心高分项目专线（裸纤）",
            line_type="科技云科技专线",
            business_person="周建虎",
            build_person="胡亮亮、王振伟",
            link_status=Link.LinkStatus.USING,
            remarks="adaeda",
            enable_date="2014-07-01",
            link_element=[
                {
                    "index": 1,
                    "sub_index": 1,
                    "element_id": self.leaseline1.element.id
                }
            ]
        )
        query = parse.urlencode(query={'search': self.leaseline1.private_line_number})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['is_linked'], True)
        query = parse.urlencode(query={'search': self.leaseline2.private_line_number})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['is_linked'], False)

        # query "is_linked"
        query = parse.urlencode(query={'is_linked': '1'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=response)
        query = parse.urlencode(query={'is_linked': 'true'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['is_linked'], True)
        query = parse.urlencode(query={'is_linked': 'False'})
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['is_linked'], False)

    def test_update(self):
        base_url = reverse('net_link-api:link-leaseline-update-leaseline', kwargs={'id': 'test'})
        data = json.dumps({
            'private_line_number': '510GXN12603174',
            'lease_line_code': '0F0001NP',
            'line_username': '广州联通互联互通',
            'endpoint_a': '广州市天河乐意居广州化学所',
            'endpoint_z': '广州联通科学城2数据机房',
            'line_type': '骨干网',
            'cable_type': '裸光纤',
            'bandwidth': '400',
            'length': '',
            'provider': '联通（北京）',
            'enable_date': '2023-06-15',
            'is_whithdrawal': 'false',
            'money': '300.20',
            'remarks': '电路编号：中科院广州化学有限公司-科学城2数据机房0F0001NP'
        })

        # user role
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.client.force_login(self.user1)
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        self.client.force_login(self.user2)
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        self.client.force_login(self.user3)
        response = self.client.post(base_url, data=data, content_type='application/json')

        # LeaseLineNotExist
        self.assertErrorResponse(status_code=404, code='LeaseLineNotExist', response=response)
        id = LeaseLine.objects.all().first().id
        base_url = reverse('net_link-api:link-leaseline-update-leaseline', kwargs={'id': id})
        response = self.client.post(base_url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # data
        leaseline = response.data
        self.assertKeysIn([
            'id', 'private_line_number', 'lease_line_code', 'line_username', 'endpoint_a', 'endpoint_z',
            'line_type', 'cable_type', 'bandwidth', 'length', 'provider', 'enable_date', 'is_whithdrawal',
            'money', 'remarks', 'is_linked', 'element_id'
        ], leaseline)
        self.assertEqual(response.data['private_line_number'], '510GXN12603174')
        self.assertEqual(response.data['lease_line_code'], '0F0001NP')
        leaseline = LeaseLine.objects.filter(private_line_number='510GXN12603174').first()
        self.assertEqual(leaseline.element.object_type, Element.Type.LEASE_LINE)
        self.assertEqual(leaseline.element.object_id, leaseline.id)

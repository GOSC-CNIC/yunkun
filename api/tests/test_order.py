from decimal import Decimal
from urllib import parse
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from servers.models import Flavor
from utils.model import PayType, OwnerType
from order.models import Price, Order, ResourceType
from order.managers import OrderManager
from order.managers.instance_configs import ServerConfig, DiskConfig
from utils.decimal_utils import quantize_10_2
from utils.test import get_or_create_user, get_or_create_service
from vo.models import VirtualOrganization, VoMember
from bill.managers import PaymentManager
from bill.models import PaymentHistory
from activity.models import CashCoupon, CouponType, ApplicableResourceField
from api.handlers.order_handler import CASH_COUPON_BALANCE
from . import set_auth_header, MyAPITestCase


class OrderTests(MyAPITestCase):
    def setUp(self):
        self.user = set_auth_header(self)
        self.user2 = get_or_create_user(username='user2')
        price = Price(
            vm_ram=Decimal('0.12'),
            vm_cpu=Decimal('0.066'),
            vm_disk=Decimal('0.122'),
            vm_pub_ip=Decimal('0.66'),
            vm_upstream=Decimal('0.33'),
            vm_downstream=Decimal('1.446'),
            vm_disk_snap=Decimal('0.65'),
            disk_size=Decimal('1.02'),
            disk_snap=Decimal('0.77'),
            obj_size=Decimal('0'),
            obj_upstream=Decimal('0'),
            obj_downstream=Decimal('0'),
            obj_replication=Decimal('0.2'),
            obj_get_request=Decimal('0'),
            obj_put_request=Decimal('0'),
            prepaid_discount=66
        )
        price.save()
        self.price = price
        self.flavor = Flavor(vcpus=2, ram=4 * 1024)
        self.flavor.save()
        self.vo = VirtualOrganization(
            name='test vo', owner=self.user
        )
        self.vo.save()
        self.service = get_or_create_service()

    def test_list_order(self):
        omgr = OrderManager()
        base_url = reverse('api:order-list')

        # list user order
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)
        self.assertKeysIn(['count', 'page_num', 'page_size', 'orders'], response.data)
        self.assertIsInstance(response.data['orders'], list)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        # list vo order
        query = parse.urlencode(query={
            'vo_id': self.vo.id
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertKeysIn(['count', 'page_num', 'page_size', 'orders'], response.data)
        self.assertIsInstance(response.data['orders'], list)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        order_instance_config = ServerConfig(
            vm_cpu=2, vm_ram=2048, systemdisk_size=100, public_ip=True,
            image_id='image_id', network_id='network_id', azone_id='azone_id', azone_name='azone_name'
        )
        order, resource = omgr.create_order(
            order_type=Order.OrderType.NEW.value,
            service_id='test',
            service_name='test',
            resource_type=ResourceType.VM.value,
            instance_config=order_instance_config,
            period=2,
            pay_type=PayType.PREPAID.value,
            user_id=self.user.id,
            username=self.user.username,
            vo_id='', vo_name='',
            owner_type=OwnerType.USER.value
        )

        # list user order
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['orders']), 1)
        self.assertKeysIn(["id", "order_type", "status", "total_amount", "pay_amount",
                           "service_id", "service_name", "resource_type", "instance_config", "period",
                           "payment_time", "pay_type", "creation_time", "user_id", "username",
                           "vo_id", "vo_name", "owner_type"], response.data['orders'][0])
        self.assert_is_subdict_of({
            "id": order.id,
            "order_type": order.order_type,
            "status": order.status,
            "total_amount": str(quantize_10_2(order.total_amount)),
            "pay_amount": str(quantize_10_2(order.pay_amount)),
            "service_id": order.service_id,
            "service_name": order.service_name,
            "resource_type": ResourceType.VM.value,
            "instance_config": order.instance_config,
            "period": order.period,
            "pay_type": PayType.PREPAID.value,
            "user_id": self.user.id,
            "username": self.user.username,
            "vo_id": order.vo_id,
            "vo_name": order.vo_name,
            "owner_type": OwnerType.USER.value
        }, response.data['orders'][0])
        self.assertEqual(order_instance_config, ServerConfig.from_dict(response.data['orders'][0]['instance_config']))

        # list vo order
        query = parse.urlencode(query={
            'vo_id': self.vo.id
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        order2_instance_config = DiskConfig(disk_size=166, azone_id='azone_id', azone_name='azone_name')
        order2, resource2 = omgr.create_order(
            order_type=Order.OrderType.UPGRADE.value,
            service_id='test',
            service_name='test',
            resource_type=ResourceType.DISK.value,
            instance_config=order2_instance_config,
            period=2,
            pay_type=PayType.POSTPAID.value,
            user_id='',
            username='',
            vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value
        )

        # list user order
        response = self.client.get(base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['orders']), 1)

        # list vo order
        query = parse.urlencode(query={
            'vo_id': self.vo.id
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['orders']), 1)
        self.assert_is_subdict_of({
            "id": order2.id,
            "order_type": order2.order_type,
            "status": order2.status,
            "total_amount": str(quantize_10_2(order2.total_amount)),
            "pay_amount": str(quantize_10_2(order2.pay_amount)),
            "service_id": order2.service_id,
            "service_name": order2.service_name,
            "resource_type": ResourceType.DISK.value,
            "instance_config": order2.instance_config,
            "period": order2.period,
            "pay_type": PayType.POSTPAID.value,
            "user_id": order2.user_id,
            "username": order2.username,
            "vo_id": self.vo.id,
            "vo_name": self.vo.name,
            "owner_type": OwnerType.VO.value
        }, response.data['orders'][0])
        self.assertEqual(order2_instance_config, DiskConfig.from_dict(response.data['orders'][0]['instance_config']))

        self.list_user_order_query_test()
        self.list_vo_order_query_test()

    def list_user_order_query_test(self):
        base_url = reverse('api:order-list')

        # list user order, filter query "resource_type"
        query = parse.urlencode(query={
            'resource_type': ResourceType.DISK.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['orders']), 1)
        self.assertEqual(response.data['orders'][0]['resource_type'], ResourceType.VM.value)

        # list user order, filter query "resource_type, order_type"
        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.UPGRADE.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['orders']), 1)
        self.assertEqual(response.data['orders'][0]['resource_type'], ResourceType.VM.value)
        self.assertEqual(response.data['orders'][0]['order_type'], Order.OrderType.NEW.value)

        def check_user_order_response(_self, _url: str):
            _response = _self.client.get(_url)
            _self.assertEqual(_response.status_code, 200)
            _self.assertEqual(_response.data['count'], 1)
            _self.assertEqual(len(_response.data['orders']), 1)
            _self.assertEqual(_response.data['orders'][0]['order_type'], Order.OrderType.NEW.value)
            _self.assertEqual(_response.data['orders'][0]['status'], Order.Status.UNPAID.value)
            _self.assertEqual(_response.data['orders'][0]['resource_type'], ResourceType.VM.value)

        # list user order, filter query "resource_type, order_type, status"
        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.PAID.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.UNPAID.value
        })
        check_user_order_response(self, f'{base_url}?{query}')

        # list user order, filter query "resource_type, order_type, status, time_start"
        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.UNPAID.value, 'time_start': timezone.now()
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.UNPAID.value, 'time_start': timezone.now() - timedelta(hours=1)
        })
        check_user_order_response(self, f'{base_url}?{query}')

        # list user order, filter query "resource_type, order_type, status, time_end"
        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.UNPAID.value, 'time_end': timezone.now()
        })
        check_user_order_response(self, f'{base_url}?{query}')

        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.UNPAID.value, 'time_end': timezone.now() - timedelta(hours=1)
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        # list user order, filter query "resource_type, order_type, status, time_start, time_end"
        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.UNPAID.value,
            'time_start': timezone.now() - timedelta(hours=1), 'time_end': timezone.now()
        })
        check_user_order_response(self, f'{base_url}?{query}')

        query = parse.urlencode(query={
            'resource_type': ResourceType.VM.value, 'order_type': Order.OrderType.NEW.value,
            'status': Order.Status.UNPAID.value,
            'time_start': timezone.now(), 'time_end': timezone.now()
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

    def list_vo_order_query_test(self):
        base_url = reverse('api:order-list')

        # list vo order, filter query "resource_type"
        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.VM.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['orders']), 1)
        self.assertEqual(response.data['orders'][0]['resource_type'], ResourceType.DISK.value)

        # list vo order, filter query "resource_type, order_type"
        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.RENEWAL.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['orders']), 1)
        self.assertEqual(response.data['orders'][0]['resource_type'], ResourceType.DISK.value)
        self.assertEqual(response.data['orders'][0]['order_type'], Order.OrderType.UPGRADE.value)

        def check_vo_order_response(_self, _url: str):
            _r = _self.client.get(_url)
            _self.assertEqual(_r.status_code, 200)
            _self.assertEqual(_r.data['count'], 1)
            _self.assertEqual(len(_r.data['orders']), 1)
            _self.assertEqual(_r.data['orders'][0]['resource_type'], ResourceType.DISK.value)
            _self.assertEqual(_r.data['orders'][0]['order_type'], Order.OrderType.UPGRADE.value)
            _self.assertEqual(_r.data['orders'][0]['status'], Order.Status.UNPAID.value)

        # list vo order, filter query "resource_type, order_type, status"
        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.PAID.value
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.UNPAID.value
        })
        check_vo_order_response(self, f'{base_url}?{query}')

        # list vo order, filter query "resource_type, order_type, status, time_start"
        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.UNPAID.value, 'time_start': timezone.now()
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.UNPAID.value, 'time_start': timezone.now() - timedelta(hours=1)
        })
        check_vo_order_response(self, f'{base_url}?{query}')

        # list vo order, filter query "resource_type, order_type, status, time_end"
        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.UNPAID.value, 'time_end': timezone.now()
        })
        check_vo_order_response(self, f'{base_url}?{query}')

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.UNPAID.value, 'time_end': timezone.now() - timedelta(hours=1)
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        # list vo order, filter query "resource_type, order_type, status, time_start, time_end"
        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.UNPAID.value,
            'time_start': timezone.now() - timedelta(hours=1), 'time_end': timezone.now()
        })
        check_vo_order_response(self, f'{base_url}?{query}')

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'resource_type': ResourceType.DISK.value, 'order_type': Order.OrderType.UPGRADE.value,
            'status': Order.Status.UNPAID.value,
            'time_start': timezone.now(), 'time_end': timezone.now()
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['orders']), 0)

        # user2 no vo permission test
        user2 = get_or_create_user(username='user2')
        self.client.logout()
        self.client.force_login(user=user2)
        query = parse.urlencode(query={
            'vo_id': self.vo.id
        })
        response = self.client.get(f'{base_url}?{query}')
        self.assertEqual(response.status_code, 403)

    def test_detail_order(self):
        omgr = OrderManager()

        # invalid order id
        url = reverse('api:order-detail', kwargs={'id': 'test'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        url = reverse('api:order-detail', kwargs={'id': '123456789123456789'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)

        # not found order
        url = reverse('api:order-detail', kwargs={'id': '1234567891234567891234'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        # create order
        order_instance_config = ServerConfig(
            vm_cpu=2, vm_ram=2048, systemdisk_size=100, public_ip=True,
            image_id='image_id', network_id='network_id', azone_id='azone_id', azone_name='azone_name'
        )
        order, resource = omgr.create_order(
            order_type=Order.OrderType.NEW.value,
            service_id='test',
            service_name='test',
            resource_type=ResourceType.VM.value,
            instance_config=order_instance_config,
            period=2,
            pay_type=PayType.PREPAID.value,
            user_id=self.user.id,
            username=self.user.username,
            vo_id='', vo_name='',
            owner_type=OwnerType.USER.value
        )

        # user order detail
        url = reverse('api:order-detail', kwargs={'id': order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertKeysIn([
            "id", "order_type", "status", "total_amount", "pay_amount", "service_id", "service_name",
            "resource_type", "instance_config", "period", "payment_time", "pay_type", "creation_time",
            "user_id", "username", "vo_id", "vo_name", "owner_type", "resources"
        ], response.data)
        self.assert_is_subdict_of(sub={
            "id": order.id,
            "order_type": Order.OrderType.NEW.value,
            "status": Order.Status.UNPAID.value,
            "resource_type": ResourceType.VM.value,
            "instance_config": order.instance_config,
            "period": 2,
            "pay_type": PayType.PREPAID.value,
            "user_id": self.user.id,
            "username": self.user.username,
            "owner_type": OwnerType.USER.value,
        }, d=response.data)
        self.assert_is_subdict_of({
            "id": resource.id,
            "order_id": order.id,
            "resource_type": ResourceType.VM.value,
            "instance_id": resource.instance_id,
            "instance_status": resource.instance_status
        }, response.data["resources"][0])
        self.assert_is_subdict_of(order.instance_config, response.data["instance_config"])
        self.assertEqual(order_instance_config, ServerConfig.from_dict(response.data['instance_config']))

        order2_instance_config = DiskConfig(disk_size=166, azone_id='azone_id', azone_name='azone_name')
        order2, resource2 = omgr.create_order(
            order_type=Order.OrderType.UPGRADE.value,
            service_id='test',
            service_name='test',
            resource_type=ResourceType.DISK.value,
            instance_config=order2_instance_config,
            period=3,
            pay_type=PayType.POSTPAID.value,
            user_id='',
            username='',
            vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value
        )

        # vo order detail
        url = reverse('api:order-detail', kwargs={'id': order2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertKeysIn([
            "id", "order_type", "status", "total_amount", "pay_amount", "service_id", "service_name",
            "resource_type", "instance_config", "period", "payment_time", "pay_type", "creation_time",
            "user_id", "username", "vo_id", "vo_name", "owner_type", "resources"
        ], response.data)
        self.assert_is_subdict_of(sub={
            "id": order2.id,
            "order_type": Order.OrderType.UPGRADE.value,
            "status": Order.Status.UNPAID.value,
            "resource_type": ResourceType.DISK.value,
            "instance_config": order2.instance_config,
            "period": 3,
            "pay_type": PayType.POSTPAID.value,
            "vo_id": self.vo.id,
            "vo_name": self.vo.name,
            "owner_type": OwnerType.VO.value,
        }, d=response.data)
        self.assert_is_subdict_of({
            "id": resource2.id,
            "order_id": order2.id,
            "resource_type": ResourceType.DISK.value,
            "instance_id": resource2.instance_id,
            "instance_status": resource2.instance_status
        }, response.data["resources"][0])
        self.assert_is_subdict_of(order2.instance_config, response.data["instance_config"])
        self.assertEqual(order2_instance_config, DiskConfig.from_dict(response.data['instance_config']))

        # user2 no vo permission test
        user2 = get_or_create_user(username='user2')
        self.client.logout()
        self.client.force_login(user=user2)
        url = reverse('api:order-detail', kwargs={'id': order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        url = reverse('api:order-detail', kwargs={'id': order2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_pay_claim_order(self):
        self.client.logout()
        self.client.force_login(self.user2)

        # prepaid mode order
        instance_config = ServerConfig(
            vm_cpu=1, vm_ram=1024, systemdisk_size=50, public_ip=True,
            image_id='test', network_id='network_id', azone_id='', azone_name=''
        )
        # 创建订单
        order, resource = OrderManager().create_order(
            order_type=Order.OrderType.NEW.value,
            service_id=self.service.id,
            service_name=self.service.name,
            resource_type=ResourceType.VM.value,
            instance_config=instance_config,
            period=8,
            pay_type=PayType.PREPAID.value,
            user_id=self.user.id,
            username=self.user.username,
            vo_id=self.vo.id,
            vo_name=self.vo.name,
            owner_type=OwnerType.VO.value,
            remark='testcase创建，可删除'
        )

        # invalid order id
        url = reverse('api:order-pay-order', kwargs={'id': 'test'})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=400, code='InvalidOrderId', response=response)

        # param "payment_method"
        url = reverse('api:order-pay-order', kwargs={'id': '2022041810175512345678'})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=400, code='MissingPaymentMethod', response=response)

        # not found order
        url = reverse('api:order-pay-order', kwargs={'id': '2022041810175512345678'})
        query = parse.urlencode(query={'payment_method': Order.PaymentMethod.BALANCE.value})
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=404, code='NotFound', response=response)

        # no permission vo order
        url = reverse('api:order-pay-order', kwargs={'id': order.id})
        query = parse.urlencode(query={'payment_method': Order.PaymentMethod.BALANCE.value})
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        # 索要订单资源
        url = reverse('api:order-claim-order', kwargs={'id': order.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        # set vo member
        VoMember(user=self.user2, vo=self.vo, role=VoMember.Role.LEADER.value, inviter='').save(force_insert=True)

        # 索要订单资源
        url = reverse('api:order-claim-order', kwargs={'id': order.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='OrderUnpaid', response=response)

        # vo balance not enough
        url = reverse('api:order-pay-order', kwargs={'id': order.id})
        query = parse.urlencode(query={'payment_method': Order.PaymentMethod.BALANCE.value})
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='BalanceNotEnough', response=response)

        # set vo account balance
        vo_account = PaymentManager.get_vo_point_account(vo_id=self.vo.id)
        vo_account.balance = Decimal('10000')
        vo_account.save(update_fields=['balance'])

        # pay order
        url = reverse('api:order-pay-order', kwargs={'id': order.id})
        query = parse.urlencode(query={'payment_method': Order.PaymentMethod.BALANCE.value})
        response = self.client.post(f'{url}?{query}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['order_id'], order.id)

        resource.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(order.trading_status, order.TradingStatus.UNDELIVERED.value)
        self.assertEqual(resource.instance_status, resource.InstanceStatus.FAILED.value)

        # 索要订单资源
        url = reverse('api:order-claim-order', kwargs={'id': order.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='TryAgainLater', response=response)

        resource.last_deliver_time = resource.last_deliver_time - timedelta(minutes=2)
        resource.save(update_fields=['last_deliver_time'])
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='QuotaShortage', response=response)

    def test_pay_order_with_coupon(self):
        now_time = timezone.now()
        # 通用有效
        coupon1_user = CashCoupon(
            face_value=Decimal('10'),
            balance=Decimal('10'),
            effective_time=now_time - timedelta(days=1),
            expiration_time=now_time + timedelta(days=10),
            coupon_type=CouponType.UNIVERSAL.value,
            service_id=None,
            _applicable_resource=[ApplicableResourceField.UNIVERSAL_VALUE],
            status=CashCoupon.Status.AVAILABLE.value,
            owner_type=OwnerType.USER.value,
            user_id=self.user.id, vo_id=None
        )
        coupon1_user.save(force_insert=True)

        # 专用有效
        coupon2_user = CashCoupon(
            face_value=Decimal('20'),
            balance=Decimal('20'),
            effective_time=now_time - timedelta(days=2),
            expiration_time=now_time + timedelta(days=10),
            coupon_type=CouponType.SPECIAL.value,
            service_id=self.service.id,
            _applicable_resource=[],
            status=CashCoupon.Status.AVAILABLE.value,
            owner_type=OwnerType.USER.value,
            user_id=self.user.id, vo_id=None
        )
        coupon2_user.save(force_insert=True)

        # 通用有效，只适用于云硬盘
        coupon3_user = CashCoupon(
            face_value=Decimal('30'),
            balance=Decimal('30'),
            effective_time=now_time - timedelta(days=2),
            expiration_time=now_time + timedelta(days=10),
            coupon_type=CouponType.UNIVERSAL.value,
            service_id=None,
            _applicable_resource=[ResourceType.DISK.value],
            status=CashCoupon.Status.AVAILABLE.value,
            owner_type=OwnerType.USER.value,
            user_id=self.user.id, vo_id=None
        )
        coupon3_user.save(force_insert=True)

        # prepaid mode order
        instance_config = ServerConfig(
            vm_cpu=1, vm_ram=1024, systemdisk_size=50, public_ip=True,
            image_id='test', network_id='network_id', azone_id='', azone_name=''
        )
        # 创建订单
        order1, resource1 = OrderManager().create_order(
            order_type=Order.OrderType.NEW.value,
            service_id=self.service.id,
            service_name=self.service.name,
            resource_type=ResourceType.VM.value,
            instance_config=instance_config,
            period=8,
            pay_type=PayType.PREPAID.value,
            user_id=self.user.id,
            username=self.user.username,
            vo_id='',
            vo_name='',
            owner_type=OwnerType.USER.value,
            remark='testcase创建，可删除'
        )
        order1.total_amount = Decimal('25')
        order1.save(update_fields=['total_amount'])

        order2, resource2 = OrderManager().create_order(
            order_type=Order.OrderType.NEW.value,
            service_id=self.service.id,
            service_name=self.service.name,
            resource_type=ResourceType.VM.value,
            instance_config=instance_config,
            period=18,
            pay_type=PayType.PREPAID.value,
            user_id=self.user.id,
            username=self.user.username,
            vo_id='',
            vo_name='',
            owner_type=OwnerType.USER.value,
            remark='testcase创建，可删除'
        )
        order2.total_amount = Decimal('100')
        order2.save(update_fields=['total_amount'])

        # test param "payment_method"
        url = reverse('api:order-pay-order', kwargs={'id': order1.id})
        query = parse.urlencode(query={'payment_method': 'test'}, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidPaymentMethod', response=response)

        # only pay by balance, param "coupon_ids"
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.BALANCE.value,
            'coupon_ids': ['test']
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='CouponIDsShouldNotExist', response=response)

        # only pay by cash cooupon, missing param "coupon_ids"
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': []
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='MissingCouponIDs', response=response)

        # invalid param "coupon_ids"
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': ['', coupon1_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidCouponIDs', response=response)

        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': [coupon1_user.id, coupon2_user.id, coupon3_user.id, '4', '5', '6']
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='TooManyCouponIDs', response=response)

        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': [coupon1_user.id, coupon1_user.id, coupon2_user.id, coupon3_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='DuplicateCouponIDExist', response=response)

        # pay order1 by balance, balance not enough
        url = reverse('api:order-pay-order', kwargs={'id': order1.id})
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.BALANCE.value
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='BalanceNotEnough', response=response)

        # pay order1 by cash coupon, coupon not enough
        url = reverse('api:order-pay-order', kwargs={'id': order1.id})
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': [coupon1_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='CouponBalanceNotEnough', response=response)

        # pay order1 by cash coupon, invalid coupon
        url = reverse('api:order-pay-order', kwargs={'id': order1.id})
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': [coupon1_user.id, coupon3_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='CouponNotApplicable', response=response)

        # pay order1(25) by cash coupon, coupon1(10 - 10), coupon2(20 - 15)
        url = reverse('api:order-pay-order', kwargs={'id': order1.id})
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': [coupon1_user.id, coupon2_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertEqual(response.status_code, 200)
        coupon1_user.refresh_from_db()
        self.assertEqual(coupon1_user.balance, Decimal('0'))
        coupon2_user.refresh_from_db()
        self.assertEqual(coupon2_user.balance, Decimal('5'))
        order1.refresh_from_db()
        self.assertEqual(order1.status, Order.Status.PAID.value)
        self.assertEqual(order1.payment_method, Order.PaymentMethod.CASH_COUPON.value)
        self.assertEqual(order1.pay_amount, Decimal('25'))
        # 支付记录确认
        pay_history1 = PaymentHistory.objects.filter(order_id=order1.id).first()
        self.assertEqual(pay_history1.type, PaymentHistory.Type.PAYMENT)
        self.assertEqual(pay_history1.amounts, Decimal('0'))
        self.assertEqual(pay_history1.coupon_amount, Decimal('-25'))
        self.assertEqual(pay_history1.before_payment, Decimal('0'))
        self.assertEqual(pay_history1.after_payment, Decimal('0'))
        self.assertEqual(pay_history1.payer_type, OwnerType.USER.value)
        self.assertEqual(pay_history1.payer_id, self.user.id)
        self.assertEqual(pay_history1.payer_name, self.user.username)
        self.assertEqual(pay_history1.executor, self.user.username)
        self.assertEqual(pay_history1.payment_method, PaymentHistory.PaymentMethod.CASH_COUPON.value)
        self.assertEqual(pay_history1.payment_account, '')
        self.assertEqual(pay_history1.resource_type, ResourceType.VM.value)
        self.assertEqual(pay_history1.service_id, self.service.id)
        self.assertEqual(pay_history1.instance_id, '')
        # 券支付记录
        cc_historys = pay_history1.cashcouponpaymenthistory_set.all().order_by('creation_time')
        self.assertEqual(cc_historys[0].payment_history_id, pay_history1.id)
        self.assertEqual(cc_historys[0].cash_coupon_id, coupon1_user.id)
        self.assertEqual(cc_historys[0].before_payment, Decimal('10'))
        self.assertEqual(cc_historys[0].amounts, Decimal('-10'))
        self.assertEqual(cc_historys[0].after_payment, Decimal('0'))
        self.assertEqual(cc_historys[1].payment_history_id, pay_history1.id)
        self.assertEqual(cc_historys[1].cash_coupon_id, coupon2_user.id)
        self.assertEqual(cc_historys[1].before_payment, Decimal('20'))
        self.assertEqual(cc_historys[1].amounts, Decimal('-15'))
        self.assertEqual(cc_historys[1].after_payment, Decimal('5'))

        # pay order2(100) by cash coupon, coupon1(0), coupon2(5)
        url = reverse('api:order-pay-order', kwargs={'id': order2.id})
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': [coupon1_user.id, coupon2_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='CouponNoBalance', response=response)

        url = reverse('api:order-pay-order', kwargs={'id': order2.id})
        query = parse.urlencode(query={
            'payment_method': Order.PaymentMethod.CASH_COUPON.value,
            'coupon_ids': [coupon2_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='CouponBalanceNotEnough', response=response)

        # pay order2(100) by balance + coupon, coupon2(5), BalanceNotEnough
        url = reverse('api:order-pay-order', kwargs={'id': order2.id})
        query = parse.urlencode(query={
            'payment_method': CASH_COUPON_BALANCE,
            'coupon_ids': [coupon2_user.id]
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='BalanceNotEnough', response=response)

        url = reverse('api:order-pay-order', kwargs={'id': order2.id})
        query = parse.urlencode(query={
            'payment_method': CASH_COUPON_BALANCE
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertErrorResponse(status_code=409, code='BalanceNotEnough', response=response)

        # pay order2(100) by balance + coupon, coupon2(5)
        user_account = self.user.userpointaccount
        user_account.balance = Decimal('100')
        user_account.save(update_fields=['balance'])

        url = reverse('api:order-pay-order', kwargs={'id': order2.id})
        query = parse.urlencode(query={
            'payment_method': CASH_COUPON_BALANCE
        }, doseq=True)
        response = self.client.post(f'{url}?{query}')
        self.assertEqual(response.status_code, 200)
        coupon2_user.refresh_from_db()
        self.assertEqual(coupon2_user.balance, Decimal('0'))
        order2.refresh_from_db()
        self.assertEqual(order2.status, Order.Status.PAID.value)
        self.assertEqual(order2.payment_method, Order.PaymentMethod.BALANCE.value)
        self.assertEqual(order2.pay_amount, Decimal('100'))
        # 支付记录确认
        pay_history2 = PaymentHistory.objects.filter(order_id=order2.id).first()
        self.assertEqual(pay_history2.type, PaymentHistory.Type.PAYMENT)
        self.assertEqual(pay_history2.amounts, Decimal('-95'))
        self.assertEqual(pay_history2.coupon_amount, Decimal('-5'))
        self.assertEqual(pay_history2.before_payment, Decimal('100'))
        self.assertEqual(pay_history2.after_payment, Decimal('5'))
        self.assertEqual(pay_history2.payer_type, OwnerType.USER.value)
        self.assertEqual(pay_history2.payer_id, self.user.id)
        self.assertEqual(pay_history2.payer_name, self.user.username)
        self.assertEqual(pay_history2.executor, self.user.username)
        self.assertEqual(pay_history2.payment_method, PaymentHistory.PaymentMethod.BALANCE_COUPON.value)
        self.assertEqual(pay_history2.payment_account, self.user.userpointaccount.id)
        self.assertEqual(pay_history2.resource_type, ResourceType.VM.value)
        self.assertEqual(pay_history2.service_id, self.service.id)
        self.assertEqual(pay_history2.instance_id, '')
        # 券支付记录
        cc_historys = pay_history2.cashcouponpaymenthistory_set.all().order_by('creation_time')
        self.assertEqual(cc_historys[0].payment_history_id, pay_history2.id)
        self.assertEqual(cc_historys[0].cash_coupon_id, coupon2_user.id)
        self.assertEqual(cc_historys[0].before_payment, Decimal('5'))
        self.assertEqual(cc_historys[0].amounts, Decimal('-5'))
        self.assertEqual(cc_historys[0].after_payment, Decimal('0'))

    def test_cancel_order(self):
        # prepaid mode order
        instance_config = ServerConfig(
            vm_cpu=1, vm_ram=1024, systemdisk_size=50, public_ip=True,
            image_id='test', network_id='network_id', azone_id='', azone_name=''
        )
        # create vo order
        order, resource = OrderManager().create_order(
            order_type=Order.OrderType.NEW.value,
            service_id=self.service.id,
            service_name=self.service.name,
            resource_type=ResourceType.VM.value,
            instance_config=instance_config,
            period=8,
            pay_type=PayType.PREPAID.value,
            user_id=self.user.id,
            username=self.user.username,
            vo_id=self.vo.id,
            vo_name=self.vo.name,
            owner_type=OwnerType.VO.value,
            remark='testcase创建，可删除'
        )
        self.client.logout()
        self.client.force_login(self.user2)

        # cancel order , no permission
        url = reverse('api:order-cancel-order', kwargs={'id': order.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)

        # set vo member
        VoMember(user=self.user2, vo=self.vo, role=VoMember.Role.LEADER.value, inviter='').save(force_insert=True)

        # cancel order
        url = reverse('api:order-cancel-order', kwargs={'id': order.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['order_id'], order.id)

        # create user2 order
        order2, resource2 = OrderManager().create_order(
            order_type=Order.OrderType.NEW.value,
            service_id=self.service.id,
            service_name=self.service.name,
            resource_type=ResourceType.VM.value,
            instance_config=instance_config,
            period=8,
            pay_type=PayType.PREPAID.value,
            user_id=self.user2.id,
            username=self.user2.username,
            vo_id='',
            vo_name='',
            owner_type=OwnerType.USER.value,
            remark='testcase创建，可删除'
        )
        resource2.last_deliver_time = timezone.now()
        resource2.save(update_fields=['last_deliver_time'])

        # cancel order
        url = reverse('api:order-cancel-order', kwargs={'id': order2.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='TryAgainLater', response=response)

        # cancel closed order
        order2.trading_status = order2.TradingStatus.CLOSED.value
        order2.save(update_fields=['trading_status'])
        url = reverse('api:order-cancel-order', kwargs={'id': order2.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='OrderTradingClosed', response=response)

        # cancel completed order
        order2.trading_status = order2.TradingStatus.COMPLETED.value
        order2.save(update_fields=['trading_status'])
        url = reverse('api:order-cancel-order', kwargs={'id': order2.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='OrderTradingCompleted', response=response)

        # cancel paid order
        order2.trading_status = order2.TradingStatus.UNDELIVERED.value
        order2.status = order2.Status.PAID.value
        order2.save(update_fields=['trading_status', 'status'])
        url = reverse('api:order-cancel-order', kwargs={'id': order2.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='OrderPaid', response=response)

        # cancel refund order
        order2.trading_status = order2.TradingStatus.UNDELIVERED.value
        order2.status = order2.Status.REFUND.value
        order2.save(update_fields=['trading_status', 'status'])
        url = reverse('api:order-cancel-order', kwargs={'id': order2.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='OrderRefund', response=response)

        # cancel cancelled order
        order2.trading_status = order2.TradingStatus.UNDELIVERED.value
        order2.status = order2.Status.CANCELLED.value
        order2.save(update_fields=['trading_status', 'status'])
        url = reverse('api:order-cancel-order', kwargs={'id': order2.id})
        response = self.client.post(url)
        self.assertErrorResponse(status_code=409, code='OrderCancelled', response=response)

        # cancel order ok
        order2.trading_status = order2.TradingStatus.OPENING.value
        order2.status = order2.Status.UNPAID.value
        order2.save(update_fields=['trading_status', 'status'])
        resource2.last_deliver_time = timezone.now() - timedelta(minutes=2)
        resource2.save(update_fields=['last_deliver_time'])

        url = reverse('api:order-cancel-order', kwargs={'id': order2.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['order_id'], order2.id)

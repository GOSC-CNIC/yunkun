from decimal import Decimal
from urllib import parse
from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone as dj_timezone

from utils.model import OwnerType
from utils.time import utc
from utils.test import get_or_create_org_data_center, get_or_create_user, MyAPITestCase
from vo.models import VirtualOrganization
from servers.models import ServiceConfig
from storage.models import ObjectsService
from monitor.models import MonitorWebsiteVersion
from scan.models import VtScanService
from apply.models import CouponApply
from apply.managers import CouponApplyManager


class CouponApplyTests(MyAPITestCase):
    def setUp(self):
        self.user1 = get_or_create_user()
        self.user2 = get_or_create_user(username='tom@cnic.cn')
        self.vo = VirtualOrganization(
            name='test vo', owner=self.user1
        )
        self.vo.save()
        self.odc1 = get_or_create_org_data_center(name='odc1')
        self.odc2 = get_or_create_org_data_center(name='odc2')

    def test_list(self):
        apply1 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('1000.12'),
            expiration_time=datetime(year=2024, month=3, day=16, tzinfo=utc), apply_desc='申请原因2',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2022, month=6, day=16, tzinfo=utc)
        )
        apply2 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.STORAGE.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('2000.12'),
            expiration_time=datetime(year=2024, month=3, day=16, tzinfo=utc), apply_desc='申请原因2',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2022, month=12, day=16, tzinfo=utc),
            status=CouponApply.Status.REJECT.value, reject_reason='不允许', approver='approver1'
        )
        apply3 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('3000.12'),
            expiration_time=datetime(year=2024, month=2, day=15, tzinfo=utc), apply_desc='申请原因3',
            user_id=self.user1.id, username=self.user1.username, vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value, creation_time=datetime(year=2023, month=5, day=8, tzinfo=utc)
        )
        apply4 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.STORAGE.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('4000.12'),
            expiration_time=datetime(year=2023, month=11, day=15, tzinfo=utc), apply_desc='申请原因4',
            user_id=self.user1.id, username=self.user1.username, vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value, creation_time=datetime(year=2023, month=6, day=8, tzinfo=utc),
            status=CouponApply.Status.PASS.value, approver='approver1', approved_amount=Decimal('4000')
        )
        apply5 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=self.odc2,
            service_id='service_id2', service_name='service_name2', service_name_en='service_name_en2',
            pay_service_id='pay_service_id2', face_value=Decimal('5000.12'),
            expiration_time=datetime(year=2023, month=12, day=15, tzinfo=utc), apply_desc='申请原因5',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2023, month=8, day=18, tzinfo=utc),
            status=CouponApply.Status.PASS.value, approver='approver1', approved_amount=Decimal('4000')
        )
        apply6 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=self.odc2,
            service_id='service_id2', service_name='service_name2', service_name_en='service_name_en2',
            pay_service_id='pay_service_id2', face_value=Decimal('6000.12'),
            expiration_time=datetime(year=2023, month=12, day=15, tzinfo=utc), apply_desc='申请原因6',
            user_id=self.user2.id, username=self.user2.username, vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value, creation_time=datetime(year=2023, month=10, day=9, tzinfo=utc),
            status=CouponApply.Status.PENDING.value
        )
        apply7 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SCAN.value, odc=None,
            service_id='scan1', service_name='scan_name1', service_name_en='scan_name_en1',
            pay_service_id='pay_service_id6', face_value=Decimal('7000.12'),
            expiration_time=datetime(year=2024, month=3, day=15, tzinfo=utc), apply_desc='申请原因7',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2024, month=3, day=9, tzinfo=utc),
            status=CouponApply.Status.WAIT.value
        )
        apply8 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.MONITOR_SITE.value, odc=None,
            service_id='site1', service_name='site_name1', service_name_en='site_name_en1',
            pay_service_id='pay_service_id8', face_value=Decimal('8000.12'),
            expiration_time=datetime(year=2024, month=12, day=15, tzinfo=utc), apply_desc='申请原因8',
            user_id=self.user2.id, username=self.user2.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2024, month=3, day=11, tzinfo=utc),
            status=CouponApply.Status.PENDING.value
        )

        # user1 list
        base_url = reverse('apply-api:coupon-list')
        r = self.client.get(base_url)
        self.assertErrorResponse(status_code=401, code='NotAuthenticated', response=r)

        self.client.force_login(self.user2)
        r = self.client.get(base_url)
        self.assertEqual(r.status_code, 200)
        self.assertKeysIn(["count", "page_num", "page_size", "results"], r.data)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(len(r.data['results']), 1)
        self.assertKeysIn([
            'id', 'service_type', 'odc', 'service_id', 'service_name', 'service_name_en',
            'face_value', 'expiration_time', 'apply_desc', 'creation_time', 'update_time',
            'user_id', 'username', 'vo_id', 'vo_name', 'owner_type',
            'status', 'approver', 'approved_amount', 'reject_reason', 'coupon_id'], r.data['results'][0])
        self.assertEqual(r.data['results'][0]['id'], apply8.id)

        # vo
        query = parse.urlencode(query={'vo_id': self.vo.id})
        r = self.client.get(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        # --- user1 test vo ---
        self.client.logout()
        self.client.force_login(self.user1)

        query = parse.urlencode(query={'vo_id': self.vo.id})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 3)
        self.assertEqual(len(r.data['results']), 3)
        self.assertEqual(r.data['results'][0]['id'], apply6.id)
        self.assertEqual(r.data['results'][1]['id'], apply4.id)
        self.assertEqual(r.data['results'][2]['id'], apply3.id)

        query = parse.urlencode(query={'vo_id': self.vo.id, 'service_type': CouponApply.ServiceType.SERVER.value})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 2)
        self.assertEqual(len(r.data['results']), 2)
        self.assertEqual(r.data['results'][0]['id'], apply6.id)
        self.assertEqual(r.data['results'][1]['id'], apply3.id)

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'service_type': CouponApply.ServiceType.SERVER.value,
            'status': CouponApply.Status.PENDING.value
        })
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(len(r.data['results']), 1)
        self.assertEqual(r.data['results'][0]['id'], apply6.id)

        query = parse.urlencode(query={
            'vo_id': self.vo.id, 'time_start': '2023-06-01T00:00:00Z', 'time_end': '2023-07-06T00:00:00Z'})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(len(r.data['results']), 1)
        self.assertEqual(r.data['results'][0]['id'], apply4.id)

        # --- user1 test own ---
        r = self.client.get(base_url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 4)
        self.assertEqual(len(r.data['results']), 4)
        self.assertEqual(r.data['results'][0]['id'], apply7.id)
        self.assertEqual(r.data['results'][1]['id'], apply5.id)
        self.assertEqual(r.data['results'][2]['id'], apply2.id)
        self.assertEqual(r.data['results'][3]['id'], apply1.id)

        query = parse.urlencode(query={
            'time_start': '2023-01-01T00:00:00Z', 'time_end': '2023-12-06T00:00:00Z'})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(len(r.data['results']), 1)
        self.assertEqual(r.data['results'][0]['id'], apply5.id)

        query = parse.urlencode(query={'page_size': 2, 'page': 1})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 4)
        self.assertEqual(len(r.data['results']), 2)
        self.assertEqual(r.data['results'][0]['id'], apply7.id)
        self.assertEqual(r.data['results'][1]['id'], apply5.id)

        query = parse.urlencode(query={'page_size': 3, 'page': 2})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 4)
        self.assertEqual(len(r.data['results']), 1)
        self.assertEqual(r.data['results'][0]['id'], apply1.id)

        query = parse.urlencode(query={'status': CouponApply.Status.REJECT.value})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(len(r.data['results']), 1)
        self.assertEqual(r.data['results'][0]['id'], apply2.id)

        # ---- test odc admin ---
        query = parse.urlencode(query={'as-admin': ''})
        r = self.client.get(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        # odc1 admin
        self.odc1.users.add(self.user1)
        query = parse.urlencode(query={'as-admin': ''})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 4)
        self.assertEqual(len(r.data['results']), 4)
        self.assertEqual(r.data['results'][0]['id'], apply4.id)
        self.assertEqual(r.data['results'][1]['id'], apply3.id)
        self.assertEqual(r.data['results'][2]['id'], apply2.id)
        self.assertEqual(r.data['results'][3]['id'], apply1.id)

        # odc1 odc2 admin
        self.odc2.users.add(self.user1)
        query = parse.urlencode(query={'as-admin': ''})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 6)
        self.assertEqual(len(r.data['results']), 6)
        self.assertEqual(r.data['results'][0]['id'], apply6.id)
        self.assertEqual(r.data['results'][1]['id'], apply5.id)
        self.assertEqual(r.data['results'][2]['id'], apply4.id)
        self.assertEqual(r.data['results'][3]['id'], apply3.id)
        self.assertEqual(r.data['results'][4]['id'], apply2.id)
        self.assertEqual(r.data['results'][5]['id'], apply1.id)

        query = parse.urlencode(query={
            'as-admin': '', 'time_start': '2023-01-01T00:00:00Z', 'time_end': '2023-10-01T00:00:00Z'})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 3)
        self.assertEqual(len(r.data['results']), 3)
        self.assertEqual(r.data['results'][0]['id'], apply5.id)
        self.assertEqual(r.data['results'][1]['id'], apply4.id)
        self.assertEqual(r.data['results'][2]['id'], apply3.id)

        self.odc1.users.remove(self.user1)
        self.odc2.users.remove(self.user1)

        # -- test fed admin ----
        query = parse.urlencode(query={'as-admin': ''})
        r = self.client.get(f'{base_url}?{query}')
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        self.user1.set_federal_admin()
        query = parse.urlencode(query={'as-admin': ''})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 8)
        self.assertEqual(len(r.data['results']), 8)
        self.assertEqual(r.data['results'][0]['id'], apply8.id)
        self.assertEqual(r.data['results'][1]['id'], apply7.id)

        query = parse.urlencode(query={'as-admin': '', 'vo_id': self.vo.id})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 3)
        self.assertEqual(len(r.data['results']), 3)
        self.assertEqual(r.data['results'][0]['id'], apply6.id)
        self.assertEqual(r.data['results'][1]['id'], apply4.id)
        self.assertEqual(r.data['results'][2]['id'], apply3.id)

        query = parse.urlencode(query={
            'as-admin': '', 'time_start': '2023-01-01T00:00:00Z', 'time_end': '2024-3-09T00:00:00Z'})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 5)
        self.assertEqual(len(r.data['results']), 5)
        self.assertEqual(r.data['results'][0]['id'], apply7.id)
        self.assertEqual(r.data['results'][1]['id'], apply6.id)
        self.assertEqual(r.data['results'][2]['id'], apply5.id)
        self.assertEqual(r.data['results'][3]['id'], apply4.id)
        self.assertEqual(r.data['results'][4]['id'], apply3.id)

        query = parse.urlencode(query={
            'as-admin': '', 'time_start': '2023-01-01T00:00:00Z', 'time_end': '2024-3-09T00:00:00Z',
            'status': CouponApply.Status.WAIT.value})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 2)
        self.assertEqual(len(r.data['results']), 2)
        self.assertEqual(r.data['results'][0]['id'], apply7.id)
        self.assertEqual(r.data['results'][1]['id'], apply3.id)

        query = parse.urlencode(query={
            'as-admin': '', 'time_start': '2023-01-01T00:00:00Z', 'time_end': '2024-3-09T00:00:00Z',
            'status': CouponApply.Status.WAIT.value, 'service_type': CouponApply.ServiceType.SCAN.value})
        r = self.client.get(f'{base_url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(len(r.data['results']), 1)
        self.assertEqual(r.data['results'][0]['id'], apply7.id)

    def test_create(self):
        nt_utc = dj_timezone.now()
        base_url = reverse('apply-api:coupon-list')
        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=401, code='NotAuthenticated', response=r)
        self.client.force_login(self.user2)

        # 过期时间
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": nt_utc.isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": "string",
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)

        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": "string",
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": "string",
            "vo_id": 'xxx'
        })
        self.assertErrorResponse(status_code=404, code='VoNotExist', response=r)

        # pass vo权限，服务单元不存在
        self.client.logout()
        self.client.force_login(self.user1)
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": "string",
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        # ---- 云主机 ----
        server_service1 = ServiceConfig(
            name='server1', name_en='server1 en', status=ServiceConfig.Status.DISABLE.value,
            pay_app_service_id='s2324536464', org_data_center=self.odc1
        )
        server_service1.save(force_insert=True)
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id,
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # vo
        server_service1.status = ServiceConfig.Status.ENABLE.value
        server_service1.save(update_fields=['status'])
        expiration_time = (nt_utc + timedelta(hours=2)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明1",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id,
            "vo_id": self.vo.id
        })
        self.assertEqual(r.status_code, 201)
        self.assertKeysIn([
            'id', 'service_type', 'odc', 'service_id', 'service_name', 'service_name_en',
            'face_value', 'expiration_time', 'apply_desc', 'creation_time', 'update_time',
            'user_id', 'username', 'vo_id', 'vo_name', 'owner_type',
            'status', 'approver', 'approved_amount', 'reject_reason', 'coupon_id'], r.data)
        qs = CouponApply.objects.all()
        self.assertEqual(len(qs), 1)
        apply1: CouponApply = qs[0]
        self.assertEqual(apply1.service_type, CouponApply.ServiceType.SERVER.value)
        self.assertEqual(apply1.odc_id, self.odc1.id)
        self.assertEqual(apply1.service_id, server_service1.id)
        self.assertEqual(apply1.service_name, server_service1.name)
        self.assertEqual(apply1.service_name_en, server_service1.name_en)
        self.assertEqual(apply1.face_value, Decimal('1000.12'))
        self.assertEqual(apply1.expiration_time, expiration_time)
        self.assertEqual(apply1.apply_desc, '申请说明1')
        self.assertEqual(apply1.user_id, self.user1.id)
        self.assertEqual(apply1.username, self.user1.username)
        self.assertEqual(apply1.vo_id, self.vo.id)
        self.assertEqual(apply1.vo_name, self.vo.name)
        self.assertEqual(apply1.owner_type, OwnerType.VO.value)
        self.assertEqual(apply1.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply1.pay_service_id, server_service1.pay_app_service_id)

        # user
        expiration_time = (nt_utc + timedelta(hours=100)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "2000.12",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明user",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id
        })
        self.assertEqual(r.status_code, 201)
        qs = CouponApply.objects.all().order_by('-creation_time')
        self.assertEqual(len(qs), 2)
        apply2: CouponApply = qs[0]
        self.assertEqual(apply2.face_value, Decimal('2000.12'))
        self.assertEqual(apply2.expiration_time, expiration_time)
        self.assertEqual(apply2.apply_desc, '申请说明user')
        self.assertEqual(apply2.user_id, self.user1.id)
        self.assertEqual(apply2.username, self.user1.username)
        self.assertEqual(apply2.vo_id, '')
        self.assertEqual(apply2.vo_name, '')
        self.assertEqual(apply2.owner_type, OwnerType.USER.value)
        self.assertEqual(apply2.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply2.pay_service_id, server_service1.pay_app_service_id)

        server_service1.pay_app_service_id = ''
        server_service1.save(update_fields=['pay_app_service_id'])
        expiration_time = (nt_utc + timedelta(hours=2)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明1",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id,
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # ---- 对象存储 ----
        obj_service1 = ObjectsService(
            name='obj1', name_en='obj1 en', status=ObjectsService.Status.DISABLE.value,
            pay_app_service_id='s666666', org_data_center=self.odc1
        )
        obj_service1.save(force_insert=True)
        r = self.client.post(base_url, data={
            "face_value": "1234.56",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": obj_service1.id
        })
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)
        r = self.client.post(base_url, data={
            "face_value": "1234.56",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.STORAGE.value,
            "service_id": obj_service1.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # user
        obj_service1.status = ServiceConfig.Status.ENABLE.value
        obj_service1.save(update_fields=['status'])
        expiration_time = (nt_utc + timedelta(hours=2)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "1234.56",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "obj申请说明",
            "service_type": CouponApply.ServiceType.STORAGE.value,
            "service_id": obj_service1.id
        })
        self.assertEqual(r.status_code, 201)
        self.assertKeysIn([
            'id', 'service_type', 'odc', 'service_id', 'service_name', 'service_name_en',
            'face_value', 'expiration_time', 'apply_desc', 'creation_time', 'update_time',
            'user_id', 'username', 'vo_id', 'vo_name', 'owner_type',
            'status', 'approver', 'approved_amount', 'reject_reason', 'coupon_id'], r.data)
        qs = CouponApply.objects.all()
        self.assertEqual(len(qs), 3)
        apply3: CouponApply = qs[0]
        self.assertEqual(apply3.service_type, CouponApply.ServiceType.STORAGE.value)
        self.assertEqual(apply3.odc_id, self.odc1.id)
        self.assertEqual(apply3.service_id, obj_service1.id)
        self.assertEqual(apply3.service_name, obj_service1.name)
        self.assertEqual(apply3.service_name_en, obj_service1.name_en)
        self.assertEqual(apply3.face_value, Decimal('1234.56'))
        self.assertEqual(apply3.expiration_time, expiration_time)
        self.assertEqual(apply3.apply_desc, 'obj申请说明')
        self.assertEqual(apply3.user_id, self.user1.id)
        self.assertEqual(apply3.username, self.user1.username)
        self.assertEqual(apply3.vo_id, '')
        self.assertEqual(apply3.vo_name, '')
        self.assertEqual(apply3.owner_type, OwnerType.USER.value)
        self.assertEqual(apply3.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply3.pay_service_id, 's666666')

        # vo
        expiration_time = (nt_utc + timedelta(hours=2)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "1234.56",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "obj申请说明",
            "service_type": CouponApply.ServiceType.STORAGE.value,
            "service_id": obj_service1.id,
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)

        server_service1.pay_app_service_id = ''
        server_service1.save(update_fields=['pay_app_service_id'])
        expiration_time = (nt_utc + timedelta(hours=2)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # ---- 站点监控 ----
        site_service = MonitorWebsiteVersion.get_instance()
        r = self.client.post(base_url, data={
            "face_value": "1234.56",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "websit 申请说明",
            "service_type": CouponApply.ServiceType.MONITOR_SITE.value
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # user
        site_service.pay_app_service_id = '99767343'
        site_service.save(update_fields=['pay_app_service_id'])
        expiration_time = (nt_utc + timedelta(hours=20)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "6234.56",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "website申请说明",
            "service_type": CouponApply.ServiceType.MONITOR_SITE.value
        })
        self.assertEqual(r.status_code, 201)
        self.assertKeysIn([
            'id', 'service_type', 'odc', 'service_id', 'service_name', 'service_name_en',
            'face_value', 'expiration_time', 'apply_desc', 'creation_time', 'update_time',
            'user_id', 'username', 'vo_id', 'vo_name', 'owner_type',
            'status', 'approver', 'approved_amount', 'reject_reason', 'coupon_id'], r.data)
        qs = CouponApply.objects.all()
        self.assertEqual(len(qs), 4)
        apply4: CouponApply = qs[0]
        self.assertEqual(apply4.service_type, CouponApply.ServiceType.MONITOR_SITE.value)
        self.assertEqual(apply4.odc_id, None)
        self.assertEqual(apply4.service_id, str(site_service.id))
        self.assertEqual(apply4.face_value, Decimal('6234.56'))
        self.assertEqual(apply4.expiration_time, expiration_time)
        self.assertEqual(apply4.apply_desc, 'website申请说明')
        self.assertEqual(apply4.user_id, self.user1.id)
        self.assertEqual(apply4.username, self.user1.username)
        self.assertEqual(apply4.vo_id, '')
        self.assertEqual(apply4.vo_name, '')
        self.assertEqual(apply4.owner_type, OwnerType.USER.value)
        self.assertEqual(apply4.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply4.pay_service_id, '99767343')

        # vo
        r = self.client.post(base_url, data={
            "face_value": "6234.56",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "website申请说明",
            "service_type": CouponApply.ServiceType.MONITOR_SITE.value,
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)

        site_service.pay_app_service_id = ''
        site_service.save(update_fields=['pay_app_service_id'])
        expiration_time = (nt_utc + timedelta(hours=2)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "site申请说明",
            "service_type": CouponApply.ServiceType.MONITOR_SITE.value
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # ---- SCAN ----
        r = self.client.post(base_url, data={
            "face_value": "1234.56",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "scan 申请说明",
            "service_type": CouponApply.ServiceType.SCAN.value
        })
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        scan_service = VtScanService(
            name='scan', name_en='scan en', status=VtScanService.Status.DISABLE.value,
            pay_app_service_id='88888676'
        )
        scan_service.save(force_insert=True)

        r = self.client.post(base_url, data={
            "face_value": "1234.56",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "scan 申请说明",
            "service_type": CouponApply.ServiceType.SCAN.value,
            "service_id": scan_service.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # user
        scan_service.status = VtScanService.Status.ENABLE.value
        scan_service.save(update_fields=['status'])

        expiration_time = (nt_utc + timedelta(days=200)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "6234.56",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "scan申请说明",
            "service_type": CouponApply.ServiceType.SCAN.value
        })
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data['service_type'], CouponApply.ServiceType.SCAN.value)
        self.assertIsNone(r.data['odc'])
        self.assertEqual(r.data['service_id'], scan_service.id)
        self.assertEqual(r.data['service_name'], scan_service.name)
        self.assertEqual(r.data['service_name_en'], scan_service.name_en)
        self.assertEqual(r.data['face_value'], '6234.56')
        self.assertEqual(r.data['expiration_time'], expiration_time.isoformat().split('+')[0] + 'Z')
        self.assertEqual(r.data['apply_desc'], 'scan申请说明')
        self.assertEqual(r.data['user_id'], self.user1.id)
        self.assertEqual(r.data['username'], self.user1.username)
        self.assertEqual(r.data['vo_id'], '')
        self.assertEqual(r.data['vo_name'], '')
        self.assertEqual(r.data['owner_type'], OwnerType.USER.value)
        self.assertEqual(r.data['status'], CouponApply.Status.WAIT.value)

        qs = CouponApply.objects.all()
        self.assertEqual(len(qs), 5)
        apply5: CouponApply = qs[0]
        self.assertEqual(apply5.service_type, CouponApply.ServiceType.SCAN.value)
        self.assertEqual(apply5.odc_id, None)
        self.assertEqual(apply5.service_id, scan_service.id)
        self.assertEqual(apply5.service_name, scan_service.name)
        self.assertEqual(apply5.service_name_en, scan_service.name_en)
        self.assertEqual(apply5.face_value, Decimal('6234.56'))
        self.assertEqual(apply5.expiration_time, expiration_time)
        self.assertEqual(apply5.apply_desc, 'scan申请说明')
        self.assertEqual(apply5.user_id, self.user1.id)
        self.assertEqual(apply5.username, self.user1.username)
        self.assertEqual(apply5.vo_id, '')
        self.assertEqual(apply5.vo_name, '')
        self.assertEqual(apply5.owner_type, OwnerType.USER.value)
        self.assertEqual(apply5.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply5.pay_service_id, '88888676')

        # vo
        r = self.client.post(base_url, data={
            "face_value": "6234.56",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "scan申请说明",
            "service_type": CouponApply.ServiceType.SCAN.value,
            "vo_id": self.vo.id
        })
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)

        scan_service.pay_app_service_id = ''
        scan_service.save(update_fields=['pay_app_service_id'])
        expiration_time = (nt_utc + timedelta(hours=2)).replace(microsecond=0)
        r = self.client.post(base_url, data={
            "face_value": "1000.12",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "scan申请说明",
            "service_type": CouponApply.ServiceType.SCAN.value
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

    def test_update(self):
        nt_utc = dj_timezone.now()
        server_service1 = ServiceConfig(
            name='server1', name_en='server1 en', status=ServiceConfig.Status.ENABLE.value,
            pay_app_service_id='s2324536464', org_data_center=self.odc1
        )
        server_service1.save(force_insert=True)
        server_service2 = ServiceConfig(
            name='server2', name_en='server2 en', status=ServiceConfig.Status.ENABLE.value,
            pay_app_service_id='s2222222', org_data_center=self.odc2
        )
        server_service2.save(force_insert=True)
        apply1 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=server_service1.org_data_center,
            service_id=server_service1.id, service_name=server_service1.name, service_name_en=server_service1.name_en,
            pay_service_id=server_service1.pay_app_service_id, face_value=Decimal('1000.12'),
            expiration_time=datetime(year=2024, month=3, day=16, tzinfo=utc), apply_desc='申请原因1',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value
        )
        base_url = reverse('apply-api:coupon-detail', kwargs={'id': 'xx'})
        r = self.client.put(base_url)
        self.assertErrorResponse(status_code=401, code='NotAuthenticated', response=r)
        self.client.force_login(self.user2)

        # 过期时间
        r = self.client.put(base_url, data={
            "face_value": "1000.12",
            "expiration_time": nt_utc.isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service2.id
        })
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)

        # not found
        r = self.client.put(base_url, data={
            "face_value": "1000.12",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service2.id
        })
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        # AccessDenied
        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply1.id})
        r = self.client.put(base_url, data={
            "face_value": "2000.12",
            "expiration_time": (nt_utc + timedelta(hours=2)).isoformat(),
            "apply_desc": "申请说明",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service2.id
        })
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        # to server service2
        self.client.logout()
        self.client.force_login(self.user1)

        expiration_time = nt_utc + timedelta(hours=3)
        r = self.client.put(base_url, data={
            "face_value": "2000.12",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明ss",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service2.id
        })
        self.assertEqual(r.status_code, 200)
        self.assertKeysIn([
            'id', 'service_type', 'odc', 'service_id', 'service_name', 'service_name_en',
            'face_value', 'expiration_time', 'apply_desc', 'creation_time', 'update_time',
            'user_id', 'username', 'vo_id', 'vo_name', 'owner_type',
            'status', 'approver', 'approved_amount', 'reject_reason', 'coupon_id'], r.data)

        apply1.refresh_from_db()
        self.assertEqual(apply1.service_type, CouponApply.ServiceType.SERVER.value)
        self.assertEqual(apply1.odc_id, server_service2.org_data_center_id)
        self.assertEqual(apply1.service_id, server_service2.id)
        self.assertEqual(apply1.service_name, server_service2.name)
        self.assertEqual(apply1.service_name_en, server_service2.name_en)
        self.assertEqual(apply1.pay_service_id, 's2222222')
        self.assertEqual(apply1.expiration_time, expiration_time)
        self.assertEqual(apply1.face_value, Decimal('2000.12'))
        self.assertEqual(apply1.apply_desc, '申请说明ss')
        self.assertEqual(apply1.user_id, self.user1.id)
        self.assertEqual(apply1.vo_id, '')
        self.assertEqual(apply1.owner_type, OwnerType.USER.value)
        self.assertEqual(apply1.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply1.reject_reason, '')
        self.assertEqual(apply1.approver, '')

        # ----- to object service1  -----
        obj_service1 = ObjectsService(
            name='obj1', name_en='obj1 en', status=ObjectsService.Status.ENABLE.value,
            pay_app_service_id='s666666', org_data_center=self.odc1
        )
        obj_service1.save(force_insert=True)

        expiration_time = nt_utc + timedelta(hours=23)
        # status test
        apply1.status = CouponApply.Status.PENDING.value
        apply1.save(update_fields=['status'])
        r = self.client.put(base_url, data={
            "face_value": "3000.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明ss22",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        apply1.status = CouponApply.Status.CANCEL.value
        apply1.save(update_fields=['status'])
        r = self.client.put(base_url, data={
            "face_value": "3000.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明ss22",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        apply1.status = CouponApply.Status.PASS.value
        apply1.save(update_fields=['status'])
        r = self.client.put(base_url, data={
            "face_value": "3000.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明ss22",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        apply1.status = CouponApply.Status.REJECT.value
        apply1.save(update_fields=['status'])
        r = self.client.put(base_url, data={
            "face_value": "3234.56",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "obj申请说明",
            "service_type": CouponApply.ServiceType.STORAGE.value,
            "service_id": obj_service1.id
        })
        self.assertEqual(r.status_code, 200)
        apply1.refresh_from_db()
        self.assertEqual(apply1.service_type, CouponApply.ServiceType.STORAGE.value)
        self.assertEqual(apply1.odc_id, obj_service1.org_data_center_id)
        self.assertEqual(apply1.service_id, obj_service1.id)
        self.assertEqual(apply1.service_name, obj_service1.name)
        self.assertEqual(apply1.service_name_en, obj_service1.name_en)
        self.assertEqual(apply1.pay_service_id, 's666666')
        self.assertEqual(apply1.expiration_time, expiration_time)
        self.assertEqual(apply1.face_value, Decimal('3234.56'))
        self.assertEqual(apply1.apply_desc, 'obj申请说明')
        self.assertEqual(apply1.user_id, self.user1.id)
        self.assertEqual(apply1.vo_id, '')
        self.assertEqual(apply1.owner_type, OwnerType.USER.value)
        self.assertEqual(apply1.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply1.reject_reason, '')
        self.assertEqual(apply1.approver, '')

        # ----- vo ------
        self.client.logout()
        self.client.force_login(self.user2)
        apply2 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=server_service1.org_data_center,
            service_id=server_service1.id, service_name=server_service1.name, service_name_en=server_service1.name_en,
            pay_service_id=server_service1.pay_app_service_id, face_value=Decimal('1000.12'),
            expiration_time=datetime(year=2024, month=3, day=16, tzinfo=utc), apply_desc='申请原因1',
            user_id=self.user2.id, username=self.user2.username, vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value
        )
        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply2.id})
        expiration_time = nt_utc + timedelta(hours=200)
        r = self.client.put(base_url, data={
            "face_value": "333.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明ss22qwdqw",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id
        })
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        self.client.logout()
        self.client.force_login(self.user1)
        expiration_time = nt_utc + timedelta(hours=200)
        r = self.client.put(base_url, data={
            "face_value": "333.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明ss22qwdqw",
            "service_type": CouponApply.ServiceType.SERVER.value,
            "service_id": server_service1.id
        })
        apply2.refresh_from_db()
        self.assertEqual(apply2.service_type, CouponApply.ServiceType.SERVER.value)
        self.assertEqual(apply2.odc_id, server_service1.org_data_center_id)
        self.assertEqual(apply2.service_id, server_service1.id)
        self.assertEqual(apply2.service_name, server_service1.name)
        self.assertEqual(apply2.service_name_en, server_service1.name_en)
        self.assertEqual(apply2.pay_service_id, server_service1.pay_app_service_id)
        self.assertEqual(apply2.expiration_time, expiration_time)
        self.assertEqual(apply2.face_value, Decimal('333.33'))
        self.assertEqual(apply2.apply_desc, '申请说明ss22qwdqw')
        self.assertEqual(apply2.user_id, self.user1.id)
        self.assertEqual(apply2.username, self.user1.username)
        self.assertEqual(apply2.vo_id, self.vo.id)
        self.assertEqual(apply2.vo_name, self.vo.name)
        self.assertEqual(apply2.owner_type, OwnerType.VO.value)
        self.assertEqual(apply2.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply2.reject_reason, '')
        self.assertEqual(apply2.approver, '')

        # can not update vo object service
        r = self.client.put(base_url, data={
            "face_value": "333.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "申请说明ss22qwdqw",
            "service_type": CouponApply.ServiceType.STORAGE.value,
            "service_id": obj_service1.id
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # ---- 站点监控 ----
        site_service = MonitorWebsiteVersion.get_instance()
        site_service.pay_app_service_id = '99767343'
        site_service.save(update_fields=['pay_app_service_id'])

        expiration_time = nt_utc + timedelta(hours=66)
        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply1.id})
        r = self.client.put(base_url, data={
            "face_value": "4333.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "site 申请说明ss22qwdqw",
            "service_type": CouponApply.ServiceType.MONITOR_SITE.value
        })
        self.assertEqual(r.status_code, 200)
        apply1.refresh_from_db()
        self.assertEqual(apply1.service_type, CouponApply.ServiceType.MONITOR_SITE.value)
        self.assertIsNone(apply1.odc_id)
        self.assertEqual(apply1.service_id, str(site_service.id))
        self.assertEqual(apply1.pay_service_id, '99767343')
        self.assertEqual(apply1.expiration_time, expiration_time)
        self.assertEqual(apply1.face_value, Decimal('4333.33'))
        self.assertEqual(apply1.apply_desc, 'site 申请说明ss22qwdqw')
        self.assertEqual(apply1.user_id, self.user1.id)
        self.assertEqual(apply1.username, self.user1.username)
        self.assertEqual(apply1.vo_id, '')
        self.assertEqual(apply1.owner_type, OwnerType.USER.value)
        self.assertEqual(apply1.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply1.reject_reason, '')
        self.assertEqual(apply1.approver, '')

        # ---- SCAN ----
        expiration_time = nt_utc + timedelta(hours=668)
        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply1.id})
        r = self.client.put(base_url, data={
            "face_value": "666.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "scan 申请说明ss22qwdqw",
            "service_type": CouponApply.ServiceType.SCAN.value
        })
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        scan_service = VtScanService(
            name='scan', name_en='scan en', status=VtScanService.Status.DISABLE.value,
            pay_app_service_id='88888676'
        )
        scan_service.save(force_insert=True)
        r = self.client.put(base_url, data={
            "face_value": "666.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "scan 申请说明ss22qwdqw",
            "service_type": CouponApply.ServiceType.SCAN.value
        })
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        scan_service.status = VtScanService.Status.ENABLE.value
        scan_service.save(update_fields=['status'])
        r = self.client.put(base_url, data={
            "face_value": "666.33",
            "expiration_time": expiration_time.isoformat(),
            "apply_desc": "scan 申请说明ss22qwdqw",
            "service_type": CouponApply.ServiceType.SCAN.value
        })
        self.assertEqual(r.status_code, 200)
        apply1.refresh_from_db()
        self.assertEqual(apply1.service_type, CouponApply.ServiceType.SCAN.value)
        self.assertIsNone(apply1.odc_id)
        self.assertEqual(apply1.service_id, scan_service.id)
        self.assertEqual(apply1.pay_service_id, '88888676')
        self.assertEqual(apply1.expiration_time, expiration_time)
        self.assertEqual(apply1.face_value, Decimal('666.33'))
        self.assertEqual(apply1.apply_desc, 'scan 申请说明ss22qwdqw')
        self.assertEqual(apply1.user_id, self.user1.id)
        self.assertEqual(apply1.username, self.user1.username)
        self.assertEqual(apply1.vo_id, '')
        self.assertEqual(apply1.owner_type, OwnerType.USER.value)
        self.assertEqual(apply1.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply1.reject_reason, '')
        self.assertEqual(apply1.approver, '')

    def test_delete(self):
        apply1 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.STORAGE.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('5000.12'),
            expiration_time=datetime(year=2024, month=3, day=16, tzinfo=utc), apply_desc='申请原因2',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2022, month=12, day=16, tzinfo=utc),
            status=CouponApply.Status.REJECT.value, reject_reason='不允许', approver='approver1'
        )
        apply2 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('6000.12'),
            expiration_time=datetime(year=2024, month=2, day=15, tzinfo=utc), apply_desc='申请原因3',
            user_id=self.user2.id, username=self.user2.username, vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value, creation_time=datetime(year=2023, month=5, day=8, tzinfo=utc)
        )

        base_url = reverse('apply-api:coupon-detail', kwargs={'id': 'xx'})
        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=401, code='NotAuthenticated', response=r)
        self.client.force_login(self.user2)

        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply1.id})
        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply2.id})
        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        self.client.logout()
        self.client.force_login(self.user1)

        self.assertFalse(apply1.deleted)
        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply1.id})
        r = self.client.delete(base_url)
        self.assertEqual(r.status_code, 204)
        apply1.refresh_from_db()
        self.assertTrue(apply1.deleted)

        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        self.assertFalse(apply2.deleted)
        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply2.id})
        r = self.client.delete(base_url)
        self.assertEqual(r.status_code, 204)
        apply2.refresh_from_db()
        self.assertTrue(apply2.deleted)

        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

    def test_cancel(self):
        apply1 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.STORAGE.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('522.12'),
            expiration_time=datetime(year=2024, month=3, day=16, tzinfo=utc), apply_desc='申请原因tw',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2022, month=12, day=16, tzinfo=utc),
            status=CouponApply.Status.REJECT.value, reject_reason='不允许', approver='approver1'
        )
        apply2 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('688.12'),
            expiration_time=datetime(year=2024, month=2, day=15, tzinfo=utc), apply_desc='申请原因rhr',
            user_id=self.user2.id, username=self.user2.username, vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value, creation_time=datetime(year=2023, month=5, day=8, tzinfo=utc)
        )

        base_url = reverse('apply-api:coupon-cancel', kwargs={'id': 'xx'})
        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=401, code='NotAuthenticated', response=r)
        self.client.force_login(self.user2)

        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply1.id})
        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        base_url = reverse('apply-api:coupon-detail', kwargs={'id': apply2.id})
        r = self.client.delete(base_url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        self.client.logout()
        self.client.force_login(self.user1)

        self.assertEqual(apply1.status, CouponApply.Status.REJECT.value)
        base_url = reverse('apply-api:coupon-cancel', kwargs={'id': apply1.id})
        r = self.client.post(base_url)
        self.assertEqual(r.status_code, 200)
        apply1.refresh_from_db()
        self.assertEqual(apply1.status, CouponApply.Status.CANCEL.value)

        r = self.client.post(base_url)
        self.assertEqual(r.status_code, 200)

        self.assertEqual(apply2.status, CouponApply.Status.WAIT.value)
        self.assertEqual(apply2.delete_user, '')
        base_url = reverse('apply-api:coupon-cancel', kwargs={'id': apply2.id})
        r = self.client.post(base_url)
        self.assertEqual(r.status_code, 200)
        apply2.refresh_from_db()
        self.assertEqual(apply1.status, CouponApply.Status.CANCEL.value)
        self.assertEqual(apply2.delete_user, self.user1.username)

        r = self.client.post(base_url)
        self.assertEqual(r.status_code, 200)

        apply2.status = CouponApply.Status.PASS.value
        apply2.save(update_fields=['status'])
        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

    def test_pending(self):
        apply1 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SERVER.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('688.12'),
            expiration_time=datetime(year=2024, month=2, day=15, tzinfo=utc), apply_desc='申请原因rhr',
            user_id=self.user2.id, username=self.user2.username, vo_id=self.vo.id, vo_name=self.vo.name,
            owner_type=OwnerType.VO.value, creation_time=datetime(year=2023, month=5, day=8, tzinfo=utc),
            status=CouponApply.Status.REJECT.value, reject_reason='不允许', approver='approver1'
        )

        apply2 = CouponApplyManager.create_apply(
            service_type=CouponApply.ServiceType.SCAN.value, odc=self.odc1,
            service_id='service_id1', service_name='service_name1', service_name_en='service_name_en1',
            pay_service_id='pay_service_id1', face_value=Decimal('522.12'),
            expiration_time=datetime(year=2024, month=3, day=16, tzinfo=utc), apply_desc='申请原因twada',
            user_id=self.user1.id, username=self.user1.username, vo_id='', vo_name='',
            owner_type=OwnerType.USER.value, creation_time=datetime(year=2022, month=12, day=16, tzinfo=utc)
        )

        base_url = reverse('apply-api:coupon-pending', kwargs={'id': 'xx'})
        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=401, code='NotAuthenticated', response=r)
        self.client.force_login(self.user2)

        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=404, code='TargetNotExist', response=r)

        base_url = reverse('apply-api:coupon-pending', kwargs={'id': apply1.id})
        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        # 只能挂起待审批
        self.odc1.users.add(self.user2)
        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        apply1.status = CouponApply.Status.WAIT.value
        apply1.save(update_fields=['status'])
        base_url = reverse('apply-api:coupon-pending', kwargs={'id': apply1.id})
        r = self.client.post(base_url)
        self.assertEqual(r.status_code, 200)
        apply1.refresh_from_db()
        self.assertEqual(apply1.status, CouponApply.Status.PENDING.value)
        self.assertEqual(apply1.approver, self.user2.username)

        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=409, code='Conflict', response=r)

        # fed admin
        base_url = reverse('apply-api:coupon-pending', kwargs={'id': apply2.id})
        r = self.client.post(base_url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=r)

        self.user2.set_federal_admin()
        r = self.client.post(base_url)
        self.assertEqual(r.status_code, 200)
        apply2.refresh_from_db()
        self.assertEqual(apply2.status, CouponApply.Status.PENDING.value)
        self.assertEqual(apply2.approver, self.user2.username)

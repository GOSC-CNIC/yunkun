from __future__ import print_function
from decimal import Decimal
from datetime import datetime, timedelta, time

import pytz
from django.test import TransactionTestCase
from django.utils import timezone

from utils.test import get_or_create_user, get_or_create_storage_service
from utils.model import OwnerType
from core import errors
from order.models import Price, ResourceType
from bill.models import CashCoupon, PaymentHistory, PayAppService, PayApp, PayOrgnazition
from .measurers import StorageMeasure
from .models import PaymentStatus, MeteringObjectStorage, DailyStatementObjectStorage
from .payment import MeteringPaymentManager
from .generate_daily_statement import GenerateDailyStatementObjectStorage
from users.models import UserProfile
from storage.models import Bucket, ObjectsService


def create_bucket_metadata(service, user, creation_time):
    bucket = Bucket(service=service,
                    user=user,
                    creation_time=creation_time,
                    )
    bucket.save()
    return bucket


def up_int(val, base=100):
    return int(val * base)


class MeteringObjectStorageTests(TransactionTestCase):
    def setUp(self):
        self.user = get_or_create_user()
        self.service = get_or_create_storage_service()
        self.price = Price(
            vm_ram=Decimal('0'),
            vm_cpu=Decimal('0'),
            vm_disk=Decimal('0'),
            vm_pub_ip=Decimal('0'),
            vm_upstream=Decimal('0'),
            vm_downstream=Decimal('0'),
            vm_disk_snap=Decimal('0'),
            disk_size=Decimal('0'),
            disk_snap=Decimal('0'),
            obj_size=Decimal('1.2'),
            obj_upstream=Decimal('0'),
            obj_downstream=Decimal('0'),
            obj_replication=Decimal('0'),
            obj_get_request=Decimal('0'),
            obj_put_request=Decimal('0'),
            prepaid_discount=66
        )
        self.price.save()

    def init_data_only_bucket(self, now: datetime):
        ago_hour_time = now - timedelta(hours=1)
        meter_time = now - timedelta(days=1)
        ago_time = now - timedelta(days=2)

        meter_time.replace(hour=12, minute=0, second=0, microsecond=0)

        # 该桶是处于今天的计费范围 而当前计费的是昨天到今天的使用情况
        bucket1 = create_bucket_metadata(
            service=self.service,
            user=self.user,
            creation_time=ago_hour_time
        )

        bucket1.name = 'bucket1'
        bucket1.save()

        bucket2 = create_bucket_metadata(
            service=self.service,
            user=self.user,
            creation_time=meter_time
        )

        bucket2.name = 'bucket2'
        bucket2.save()

        bucket3 = create_bucket_metadata(
            service=self.service,
            user=self.user,
            creation_time=ago_time
        )

        bucket3.name = 'bucket3'
        bucket3.save()

        return bucket1, bucket2, bucket3

    @staticmethod
    def delta_hours(end, start):
        delta = end - start
        seconds = delta.total_seconds()
        seconds = max(seconds, 0)
        return seconds / 3600

    def do_assert_bucket(self, now: datetime, bucket2: Bucket, bucket3: Bucket, cnt: int):
        metering_date = (now - timedelta(days=1)).date()
        metering_end_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        measure = StorageMeasure(raise_exception=True)
        measure.run()

        utc_now = now.astimezone(pytz.utc)
        uin_utc_0_1 = False
        if time(hour=0, minute=0, second=0) <= utc_now.time() <= time(hour=1, minute=0, second=0):
            uin_utc_0_1 = True

        count = MeteringObjectStorage.objects.count()

        if uin_utc_0_1:
            self.assertEqual(count, cnt)
        else:
            self.assertEqual(count, cnt - 1)

        # bucket2 是不满一天的情况
        metering = measure.bucket_metering_exists(metering_date=metering_date, bucket_id=bucket2.id)
        self.assertIsNotNone(metering)
        # 这里是将 iharbor中的storage 都设置成为了50
        self.assertEqual(up_int(metering.storage), up_int(50))
        self.assertEqual(metering.user_id, self.user.id)
        self.assertEqual(metering.username, self.user.username)

        # bucket2 是 不满一天的测试情况
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        hours = self.delta_hours(end=end, start=bucket2.creation_time)
        original_amount1 = (self.price.obj_size / Decimal('24') * Decimal.from_float(50 * hours))
        original_amount1 = Decimal(original_amount1).quantize(Decimal('0.00'))
        self.assertEqual(metering.original_amount, original_amount1)
        self.assertEqual(metering.trade_amount, original_amount1)

        # bucket3 是满一天的情况
        metering = measure.bucket_metering_exists(metering_date=metering_date, bucket_id=bucket3.id)
        self.assertIsNotNone(metering)
        # 这里是将 iharbor中的storage 都设置成为了50
        self.assertEqual(up_int(metering.storage), up_int(50))
        self.assertEqual(metering.user_id, self.user.id)
        self.assertEqual(metering.username, self.user.username)

        # 数据库中的数据
        original_amount1 = (self.price.obj_size / Decimal('24') * 50 * 24)
        self.assertEqual(metering.original_amount, original_amount1)
        self.assertEqual(metering.trade_amount, original_amount1)

        # 测试是否会重复计费
        measure.run()
        count = MeteringObjectStorage.objects.count()
        if uin_utc_0_1:
            self.assertEqual(count, cnt)
        else:
            self.assertEqual(count, cnt - 1)

    def test_only_bucket(self):
        now = timezone.now()
        bucket1, bucket2, bucket3 = self.init_data_only_bucket(now)
        # bucket1不会参与计费
        self.do_assert_bucket(now=now, bucket2=bucket2, bucket3=bucket3, cnt=3)

    def test_archive_bucket(self):
        now = timezone.now()
        bucket1, bucket2, bucket3 = self.init_data_only_bucket(now)

        ok = bucket2.do_archive(archiver=self.user)
        self.assertIs(ok, True)


def create_metering_bucket_matedata(
        service, storage_bucket_id, date_,
        original_amount: Decimal, trade_amount: Decimal, daily_statement_id='',
        user_id='', username='', storage=0
):
    metering = MeteringObjectStorage(
        service=service,
        storage_bucket_id=storage_bucket_id,
        date=date_,
        user_id=user_id,
        username=username,
        original_amount=original_amount,
        trade_amount=trade_amount,
        daily_statement_id=daily_statement_id,
        storage=storage
    )
    metering.save()
    return metering


class DailyStatementTests(TransactionTestCase):
    def setUp(self):
        self.user = get_or_create_user()
        self.user2 = UserProfile(id='user2', username='username2')
        self.user2.save(force_insert=True)

        self.service = get_or_create_storage_service()
        self.service2 = ObjectsService(
            name='service2', data_center_id=self.service.data_center_id,
            endpoint_url='service2', username='', password=''
        )
        self.service2.save(force_insert=True)

        self.service3 = ObjectsService(
            name='service3', data_center_id=self.service.data_center_id,
            endpoint_url='service3', username='', password=''
        )
        self.service3.save(force_insert=True)

    def init_data(self, st_date: str = '2022-01-01'):
        n_st_date = '2022-01-02'

        # service & user
        for idx in range(1, 6):
            create_metering_bucket_matedata(
                service=self.service,
                storage_bucket_id='bucket' + str(idx),
                date_=st_date,
                user_id=self.user.id,
                username=self.user.username,
                original_amount=Decimal.from_float(idx + 0.1),
                trade_amount=Decimal.from_float(idx + 0.1)
            )

        # service2 & user
        for idx in range(6, 10):
            create_metering_bucket_matedata(
                service=self.service2,
                storage_bucket_id='bucket' + str(idx),
                date_=st_date,
                user_id=self.user.id,
                username=self.user.username,
                original_amount=Decimal.from_float(idx + 0.1),
                trade_amount=Decimal.from_float(idx + 0.1)
            )

        # service 3 & user
        for idx in range(10, 11):
            create_metering_bucket_matedata(
                service=self.service3,
                storage_bucket_id='bucket' + str(idx),
                date_=st_date,
                user_id=self.user.id,
                username=self.user.username,
                original_amount=Decimal.from_float(idx + 0.1),
                trade_amount=Decimal.from_float(idx + 0.1)
            )

        # invalid date
        for idx in range(11, 12):
            create_metering_bucket_matedata(
                service=self.service3,
                storage_bucket_id='bucket' + str(idx),
                date_=n_st_date,
                user_id=self.user.id,
                username=self.user.username,
                original_amount=Decimal.from_float(idx + 0.1),
                trade_amount=Decimal.from_float(idx + 0.1)
            )

        # service & user2
        for idx in range(13, 15):
            create_metering_bucket_matedata(
                service=self.service,
                storage_bucket_id='bucket' + str(idx),
                date_=st_date,
                user_id=self.user2.id,
                username=self.user2.username,
                original_amount=Decimal.from_float(idx + 0.1),
                trade_amount=Decimal.from_float(idx + 0.1)
            )

    def do_assert_a_user_daily_statement(self, range_a, range_b, user, service, generate_daily_statement, meterings,
                                         st_date):
        original_amount = 0
        payable_amount = 0

        for idx in range(range_a, range_b):
            original_amount += Decimal(str(int(idx) + 0.1))
            payable_amount += Decimal(str(int(idx) + 0.1))

        daily_statement = generate_daily_statement.user_daily_statement_exists(
            statement_date=st_date, service_id=service.id, user_id=user.id
        )

        self.assertIsNotNone(daily_statement)
        self.assertEqual(daily_statement.date, st_date)
        self.assertEqual(daily_statement.user_id, user.id)
        self.assertEqual(daily_statement.username, user.username)
        self.assertEqual(daily_statement.service, service)
        self.assertEqual(daily_statement.original_amount, original_amount)
        self.assertEqual(daily_statement.payable_amount, payable_amount)
        self.assertEqual(daily_statement.trade_amount, Decimal('0'))
        self.assertEqual(daily_statement.payment_status, PaymentStatus.UNPAID.value)
        self.assertEqual(daily_statement.payment_history_id, '')

        cnt = 0
        for m in meterings:
            if (
                    m.user_id == user.id and m.service == service and m.date == st_date
            ):
                cnt += 1
                self.assertEqual(m.daily_statement_id, daily_statement.id)
            else:
                self.assertNotEqual(m.daily_statement_id, daily_statement.id)

        self.assertEqual(cnt, range_b - range_a)

    def test_daily_statement(self, st_date: str = '2022-01-01'):
        self.init_data(st_date=st_date)

        st_date = datetime.strptime(st_date, '%Y-%m-%d').date()
        generate_daily_statement = GenerateDailyStatementObjectStorage(statement_date=st_date, raise_exception=True)
        generate_daily_statement.run()

        count = DailyStatementObjectStorage.objects.all().count()
        self.assertEqual(count, 4)

        meterings = MeteringObjectStorage.objects.all()

        # 2022-01-01 user & service
        self.do_assert_a_user_daily_statement(
            range_a=1, range_b=6, user=self.user, service=self.service,
            generate_daily_statement=generate_daily_statement, meterings=meterings, st_date=st_date
        )

        # 2022-01-01 user & service2
        self.do_assert_a_user_daily_statement(
            range_a=6, range_b=10, user=self.user, service=self.service2,
            generate_daily_statement=generate_daily_statement, meterings=meterings, st_date=st_date
        )

        # 2022-01-01 user & service3
        self.do_assert_a_user_daily_statement(
            range_a=10, range_b=11, user=self.user, service=self.service3,
            generate_daily_statement=generate_daily_statement, meterings=meterings, st_date=st_date
        )

        # 2022-01-01 user2& service
        self.do_assert_a_user_daily_statement(
            range_a=13, range_b=15, user=self.user2, service=self.service,
            generate_daily_statement=generate_daily_statement, meterings=meterings, st_date=st_date
        )

        # invalid date
        cnt = 0
        for m in meterings:
            if m.date != st_date:
                cnt += 1
                self.assertEqual(m.daily_statement_id, '')
        self.assertEqual(cnt, 1)

        # add another metering bill
        add_metering = create_metering_bucket_matedata(
            service=self.service,
            storage_bucket_id='bucket_user_added',
            date_=st_date,
            user_id=self.user.id,
            username=self.user.username,
            original_amount=Decimal('0.1'),
            trade_amount=Decimal('0.1'),
        )

        original_amount = add_metering.original_amount
        payable_amount = add_metering.trade_amount
        for idx in range(1, 6):
            original_amount += Decimal(str(int(idx) + 0.1))
            payable_amount += Decimal(str(int(idx) + 0.1))

        generate_daily_statement2 = GenerateDailyStatementObjectStorage(statement_date=st_date, raise_exception=True)
        generate_daily_statement2.run()

        daily_statement2 = generate_daily_statement2.user_daily_statement_exists(
            statement_date=st_date, service_id=self.service.id, user_id=self.user.id
        )
        self.assertEqual(daily_statement2.original_amount, original_amount)
        self.assertEqual(daily_statement2.payable_amount, payable_amount)


class MeteringPaymentManagerTests(TransactionTestCase):
    def setUp(self):
        self.user = get_or_create_user()
        self.service = get_or_create_storage_service()

        # balance payment
        app = PayApp(name='app')
        app.save()
        self.app = app

        po = PayOrgnazition(name='机构')
        po.save()
        self.app_service1 = PayAppService(
            name='service1', app=app, orgnazition=po
        )
        self.app_service1.save()

        self.app_service2 = PayAppService(
            name='service2', app=app, orgnazition=po
        )
        self.app_service2.save()

        self.service.pay_app_service_id = self.app_service1.id
        self.service.save(update_fields=['pay_app_service_id'])

        self.service2 = ObjectsService(
            name='service2', data_center_id=self.service.data_center_id,
            endpoint_url='service2', username='', password='', pay_app_service_id=self.app_service2.id
        )

        self.service2.save()

    def test_pay_user_daily_statement_obs(self):
        pay_mgr = MeteringPaymentManager()
        payer_name = self.user.username

        app_id = self.app.id

        # pay bill invalid user id no 'user_id'
        bill1 = DailyStatementObjectStorage(
            service_id=self.service.id,
            date=timezone.now().date(),
            user_id='user_id',
            original_amount=Decimal("199.99"),
            payable_amount=Decimal("199.99"),
            trade_amount=Decimal('0'),
            payment_status=PaymentStatus.UNPAID.value,
            payment_history_id=''
        )

        bill1.save(force_insert=True)
        with self.assertRaises(errors.Error):
            pay_mgr.pay_daily_statement_bill(
                daily_statement=bill1, app_id=app_id, subject="对象存储计费",
                executor=self.user.username, remark=''
            )

        # not enoough balance
        bill1.user_id = self.user.id
        bill1.save(update_fields=['user_id'])
        with self.assertRaises(errors.BalanceNotEnough):
            pay_mgr.pay_daily_statement_bill(
                daily_statement=bill1, app_id=app_id, subject="对象存储计费",
                executor=self.user.username, remark='', required_enough_balance=True
            )

        # pay bill
        pay_mgr.pay_daily_statement_bill(
            daily_statement=bill1, app_id=app_id, subject="对象存储计费",
            executor=self.user.username, remark='', required_enough_balance=False
        )
        self.user.userpointaccount.refresh_from_db()
        user_balance = self.user.userpointaccount.balance
        self.assertEqual(user_balance, Decimal('-199.99'))
        bill1.refresh_from_db()
        self.assertEqual(bill1.original_amount, Decimal('199.99'))
        self.assertEqual(bill1.trade_amount, Decimal('199.99'))
        self.assertEqual(bill1.payment_status, PaymentStatus.PAID.value)

        pay_history_id = bill1.payment_history_id
        pay_history = PaymentHistory.objects.get(id=pay_history_id)
        pay_history.refresh_from_db()
        self.assertEqual(pay_history.type, PaymentHistory.Type.PAYMENT)
        self.assertEqual(pay_history.amounts, Decimal('-199.99'))
        self.assertEqual(pay_history.coupon_amount, Decimal('0'))
        self.assertEqual(pay_history.before_payment, Decimal('0'))
        self.assertEqual(pay_history.after_payment, Decimal('-199.99'))
        self.assertEqual(pay_history.payer_name, payer_name)
        self.assertEqual(pay_history.app_service_id, self.service.pay_app_service_id)
        self.assertEqual(pay_history.instance_id, '')
        self.assertEqual(pay_history.payer_type, OwnerType.USER.value)
        self.assertEqual(pay_history.payer_id, self.user.id)
        self.assertEqual(pay_history.executor, self.user.username)
        self.assertEqual(pay_history.payment_method, PaymentHistory.PaymentMethod.BALANCE.value)
        self.assertEqual(pay_history.payment_account, self.user.userpointaccount.id)

        # pay bill
        bill2 = DailyStatementObjectStorage(
            service_id=self.service.id,
            date=(timezone.now() - timedelta(days=1)).date(),
            user_id=self.user.id,
            original_amount=Decimal('223.45'),
            payable_amount=Decimal('0'),
            trade_amount=Decimal('0'),
            payment_status=PaymentStatus.UNPAID.value,
            payment_history_id=''
        )

        bill2.save(force_insert=True)
        pay_mgr.pay_daily_statement_bill(
            daily_statement=bill2, app_id=app_id, subject="对象存储计费",
            executor=self.user.username, remark='', required_enough_balance=False
        )
        bill2.refresh_from_db()
        self.user.userpointaccount.refresh_from_db()
        self.assertEqual(self.user.userpointaccount.balance, user_balance)
        self.assertEqual(bill2.payment_status, PaymentStatus.PAID.value)
        self.assertEqual(bill2.original_amount, Decimal('223.45'))
        self.assertEqual(bill2.payable_amount, Decimal('0'))
        self.assertEqual(bill2.trade_amount, Decimal('0'))
        self.assertEqual(bill2.payment_history_id, '')

        # pay bill Postpaid
        bill3 = DailyStatementObjectStorage(
            service_id=self.service.id,
            date=(timezone.now() - timedelta(days=2)),
            user_id=self.user.id,
            original_amount=Decimal('66.88'),
            payable_amount=Decimal('66.88'),
            trade_amount=Decimal(0),
            payment_status=PaymentStatus.UNPAID.value,
            payment_history_id=''
        )
        bill3.save(force_insert=True)
        pay_mgr.pay_daily_statement_bill(
            daily_statement=bill3, app_id=app_id, subject='对象存储计费',
            executor=self.user.username, remark='', required_enough_balance=False
        )
        self.user.userpointaccount.refresh_from_db()
        user_balance = self.user.userpointaccount.balance
        self.assertEqual(user_balance, Decimal('-199.99') - Decimal('66.88'))
        bill3.refresh_from_db()
        self.assertEqual(bill3.payment_status, PaymentStatus.PAID.value)
        self.assertEqual(bill3.original_amount, Decimal('66.88'))
        self.assertEqual(bill3.trade_amount, Decimal('66.88'))

        pay_history_id = bill3.payment_history_id
        pay_history = PaymentHistory.objects.get(id=pay_history_id)
        pay_history.refresh_from_db()
        self.assertEqual(pay_history.amounts, Decimal('-66.88'))
        self.assertEqual(pay_history.coupon_amount, Decimal('0'))
        self.assertEqual(pay_history.before_payment, Decimal('-199.99'))
        self.assertEqual(pay_history.after_payment, Decimal('-266.87'))
        self.assertEqual(pay_history.executor, self.user.username)
        self.assertEqual(pay_history.payer_type, OwnerType.USER.value)
        self.assertEqual(pay_history.payer_id, self.user.id)
        self.assertEqual(pay_history.type, PaymentHistory.Type.PAYMENT)
        self.assertEqual(pay_history.payment_method, PaymentHistory.PaymentMethod.BALANCE.value)
        self.assertEqual(pay_history.payment_account, self.user.userpointaccount.id)
        self.assertEqual(pay_history.payer_name, payer_name)
        self.assertEqual(pay_history.resource_type, ResourceType.BUCKET.value)
        self.assertEqual(pay_history.app_service_id, self.service.pay_app_service_id)
        self.assertEqual(pay_history.instance_id, '')

        # ------- test coupon --------
        now_time = timezone.now()
        # 有效, service
        coupon1_user = CashCoupon(
            face_value=Decimal('20'),
            balance=Decimal('20'),
            effective_time=now_time - timedelta(days=1),
            expiration_time=now_time + timedelta(days=10),
            app_service_id=self.service.pay_app_service_id,
            status=CashCoupon.Status.AVAILABLE.value,
            owner_type=OwnerType.USER.value,
            user_id=self.user.id, vo_id=None
        )
        coupon1_user.save(force_insert=True)

        # 有效，只适用于service2
        coupon2_user = CashCoupon(
            face_value=Decimal('33'),
            balance=Decimal('33'),
            effective_time=now_time - timedelta(days=2),
            expiration_time=now_time + timedelta(days=10),
            app_service_id=self.service2.pay_app_service_id,
            status=CashCoupon.Status.AVAILABLE.value,
            owner_type=OwnerType.USER.value,
            user_id=self.user.id, vo_id=None
        )
        coupon2_user.save(force_insert=True)

        # pay bill, pay_type POSTPAID
        bill4 = DailyStatementObjectStorage(
            service_id=self.service.id,
            date=(timezone.now() - timedelta(days=2)),
            user_id=self.user.id,
            original_amount=Decimal('88.8'),
            payable_amount=Decimal('88.8'),
            trade_amount=Decimal(0),
            payment_status=PaymentStatus.UNPAID.value,
            payment_history_id=''
        )
        bill4.save(force_insert=True)

        self.user.userpointaccount.refresh_from_db()
        user_balance = self.user.userpointaccount.balance
        self.assertEqual(user_balance, Decimal('-266.87'))
        pay_mgr.pay_daily_statement_bill(
            daily_statement=bill4, app_id=app_id, subject='对象存储计费',
            executor=self.user.username, remark='', required_enough_balance=False
        )
        self.user.userpointaccount.refresh_from_db()
        user_balance = self.user.userpointaccount.balance
        self.assertEqual(user_balance, Decimal('-266.87') - Decimal('88.8') + Decimal('20'))  # coupon 20
        bill4.refresh_from_db()
        self.assertEqual(bill4.payment_status, PaymentStatus.PAID.value)
        self.assertEqual(bill4.original_amount, Decimal('88.8'))
        self.assertEqual(bill4.trade_amount, Decimal('88.8'))

        pay_history_id = bill4.payment_history_id
        pay_history = PaymentHistory.objects.get(id=pay_history_id)
        pay_history.refresh_from_db()
        self.assertEqual(pay_history.amounts, Decimal('-68.8'))
        self.assertEqual(pay_history.coupon_amount, Decimal('-20'))
        self.assertEqual(pay_history.before_payment, Decimal('-266.87'))
        self.assertEqual(pay_history.after_payment, Decimal('-335.67'))
        self.assertEqual(pay_history.executor, self.user.username)
        self.assertEqual(pay_history.payer_type, OwnerType.USER.value)
        self.assertEqual(pay_history.payer_id, self.user.id)
        self.assertEqual(pay_history.type, PaymentHistory.Type.PAYMENT)
        self.assertEqual(pay_history.payment_method, PaymentHistory.PaymentMethod.BALANCE_COUPON.value)
        self.assertEqual(pay_history.payment_account, self.user.userpointaccount.id)
        self.assertEqual(pay_history.payer_name, payer_name)
        self.assertEqual(pay_history.resource_type, ResourceType.BUCKET.value)
        self.assertEqual(pay_history.app_service_id, self.service.pay_app_service_id)
        self.assertEqual(pay_history.instance_id, '')

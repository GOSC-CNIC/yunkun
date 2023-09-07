from django.utils.translation import gettext as _
from django.db.models import TextChoices

from core import errors
from .models import BucketStatsMonthly


class BktStatsMonthQueryOrderBy(TextChoices):
    DATE_ASC = 'date', _('按日期升序')
    DATE_DESC = '-date', _('按日期降序')
    INCR_SIZE_ASC = 'increment_byte', _('按容量增量升序')
    INCR_SIZE_DESC = '-increment_byte', _('按容量增量降序')
    AMOUNT_ASC = 'original_amount', _('按计量金额升序')
    AMOUNT_DESC = '-original_amount', _('按计量金额降序')
    CREATION_TIME_DESC = '-creation_time', _('按创建时间降序')


class BucketStatsMonthlyManager:
    @staticmethod
    def get_queryset():
        return BucketStatsMonthly.objects.all()

    @staticmethod
    def filter_queryset(
            queryset, user_id: str = None, service_ids: list = None, bucket_id: str = None,
            date_start=None, date_end=None, order_by: str = None
    ):
        """
        date_start: 大于等于此日期
        date_end: 小于等于此日期
        """
        lookups = {}
        if service_ids:
            if len(service_ids) == 1:
                lookups['service_id'] = service_ids[0]
            else:
                lookups['service_id__in'] = service_ids

        if bucket_id:
            lookups['bucket_id'] = bucket_id

        if date_start:
            lookups['date__gte'] = date_start

        if date_end:
            lookups['date__lte'] = date_end

        if user_id:
            lookups['user_id'] = user_id

        if lookups:
            queryset = queryset.filter(**lookups)

        return queryset.order_by(order_by)

    def get_user_bkt_stats_queryset(
            self, user_id: str, service_ids: list = None, bucket_id: str = None,
            date_start=None, date_end=None, order_by: str = None
    ):
        """
        查询用户自己存储桶的月度统计数据
        """
        if not user_id:
            raise errors.NotAuthenticated()

        queryset = self.get_queryset()
        return self.filter_queryset(
            queryset=queryset, user_id=user_id, service_ids=service_ids, bucket_id=bucket_id,
            date_start=date_start, date_end=date_end, order_by=order_by
        )

    def admin_bkt_stats_queryset(
            self, user_id: str = None, service_ids: list = None, bucket_id: str = None,
            date_start=None, date_end=None, order_by: str = None
    ):
        """
        管理员查询存储桶的月度统计数据
        """
        queryset = self.get_queryset()
        return self.filter_queryset(
            queryset=queryset, user_id=user_id, service_ids=service_ids, bucket_id=bucket_id,
            date_start=date_start, date_end=date_end, order_by=order_by
        )

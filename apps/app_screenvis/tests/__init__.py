from django.conf import settings
from django.utils import timezone as dj_timezone
from rest_framework.test import APITestCase, APITransactionTestCase

from apps.app_screenvis.models import MetricMonitorUnit
from apps.app_screenvis.configs_manager import screen_configs


def get_test_case_settings():
    test_settings = getattr(settings, 'TEST_CASE', None)
    if test_settings is None:
        raise Exception('No test settings(TEST_CASE) in file "test_settings.py", '
                        'Check whether it is in debug mode(Debug=True)')

    return test_settings


class MyAPITestCase(APITestCase):
    def assertKeysIn(self, keys: list, container):
        for k in keys:
            self.assertIn(k, container)

    def assertErrorResponse(self, status_code: int, code: str, response):
        self.assertEqual(response.status_code, status_code)
        self.assertKeysIn(['code', 'message'], response.data)
        self.assertEqual(response.data['code'], code)

    def assert_is_subdict_of(self, sub: dict, d: dict):
        for k, v in sub.items():
            if k in d and v == d[k]:
                continue
            else:
                self.fail(f'{sub} is not sub dict of {d}, Not Equal key is {k}, {v} != {d.get(k)}')

        return True


class MyAPITransactionTestCase(APITransactionTestCase):
    def assertKeysIn(self, keys: list, container):
        for k in keys:
            self.assertIn(k, container)

    def assertErrorResponse(self, status_code: int, code: str, response):
        self.assertEqual(response.status_code, status_code)
        self.assertKeysIn(['code', 'message'], response.data)
        self.assertEqual(response.data['code'], code)

    def assert_is_subdict_of(self, sub: dict, d: dict):
        for k, v in sub.items():
            if k in d and v == d[k]:
                continue
            else:
                self.fail(f'{sub} is not sub dict of {d}, Not Equal key is {k}, {v} != {d.get(k)}')

        return True


def get_or_create_metric_ceph(job_tag: str = None, name: str = 'test ceph', name_en: str = 'test ceph en'):
    if job_tag is None:
        try:
            test_settings = get_test_case_settings()
            job_settings = test_settings['MONITOR_CEPH']['JOB_CEPH']
        except Exception as e:
            raise Exception(f'No test settings(MONITOR_CEPH.JOB_CEPH) in file "test_settings.TEST_CASE"， {str(e)}')

        job_tag = job_settings['job_tag']

    if not job_tag:
        raise Exception('invalid "job_tag"')

    job_ceph = MetricMonitorUnit.objects.filter(job_tag=job_tag).first()
    if job_ceph is not None:
        return job_ceph

    try:
        test_settings = get_test_case_settings()
        provider_settings = test_settings['MONITOR_CEPH']['PROVIDER']
        metric_endpoint_url = provider_settings.get('endpoint_url')
    except Exception as e:
        raise Exception(f'No test settings(MONITOR_CEPH.PROVIDER) in file "test_settings.TEST_CASE"， {str(e)}')

    screen_configs.add_or_update(
        name=screen_configs.ConfigName.METRIC_QUERY_ENDPOINT_URL.value, value=metric_endpoint_url)

    nt = dj_timezone.now()
    job_ceph = MetricMonitorUnit(
        name=name, name_en=name_en, job_tag=job_tag, unit_type=MetricMonitorUnit.UnitType.CEPH.value,
        creation_time=nt, update_time=nt
    )
    job_ceph.save(force_insert=True)
    return job_ceph


def get_or_create_metric_host(job_tag: str = None, name: str = 'test host', name_en: str = 'test host en'):
    try:
        test_settings = get_test_case_settings()
        provider_settings = test_settings['MONITOR_SERVER']['PROVIDER']
        metric_endpoint_url = provider_settings.get('endpoint_url')
    except Exception as e:
        raise Exception(f'No test settings(MONITOR_SERVER.PROVIDER) in file "test_settings.TEST_CASE"， {str(e)}')

    screen_configs.add_or_update(
        name=screen_configs.ConfigName.METRIC_QUERY_ENDPOINT_URL.value, value=metric_endpoint_url)

    if job_tag is None:
        try:
            test_settings = get_test_case_settings()
            job_settings = test_settings['MONITOR_SERVER']['JOB_SERVER']
        except Exception as e:
            raise Exception(f'No test settings(MONITOR_SERVER.JOB_SERVER) in file "test_settings.TEST_CASE"， {str(e)}')

        job_tag = job_settings['job_tag']

    if not job_tag:
        raise Exception('invalid "job_tag"')

    unit = MetricMonitorUnit.objects.filter(job_tag=job_tag).first()
    if unit is not None:
        return unit

    nt = dj_timezone.now()
    unit = MetricMonitorUnit(
        name=name, name_en=name_en, job_tag=job_tag, unit_type=MetricMonitorUnit.UnitType.HOST.value,
        creation_time=nt, update_time=nt
    )
    unit.save(force_insert=True)
    return unit


def get_or_create_metric_tidb(job_tag: str = None, name: str = 'test tidb', name_en: str = 'test tidb en'):
    if job_tag is None:
        try:
            test_settings = get_test_case_settings()
            job_settings = test_settings['MONITOR_TIDB']['JOB_TIDB']
        except Exception as e:
            raise Exception(f'No test settings(MONITOR_TIDB.JOB_TIDB) in file "test_settings.TEST_CASE"， {str(e)}')

        job_tag = job_settings['job_tag']

    if not job_tag:
        raise Exception('invalid "job_tag"')

    unit = MetricMonitorUnit.objects.filter(job_tag=job_tag).first()
    if unit is not None:
        return unit

    try:
        test_settings = get_test_case_settings()
        provider_settings = test_settings['MONITOR_TIDB']['PROVIDER']
        metric_endpoint_url = provider_settings.get('endpoint_url')
    except Exception as e:
        raise Exception(f'No test settings(MONITOR_TIDB.PROVIDER) in file "test_settings.TEST_CASE"， {str(e)}')

    screen_configs.add_or_update(
        name=screen_configs.ConfigName.METRIC_QUERY_ENDPOINT_URL.value, value=metric_endpoint_url)

    nt = dj_timezone.now()
    unit = MetricMonitorUnit(
        name=name, name_en=name_en, job_tag=job_tag, unit_type=MetricMonitorUnit.UnitType.TIDB.value,
        creation_time=nt, update_time=nt
    )
    unit.save(force_insert=True)
    return unit


def config_website_query_endpoint_url():
    try:
        test_settings = get_test_case_settings()
        provider_settings = test_settings['MONITOR_WEBSITE']['PROVIDER']
        query_endpoint_url = provider_settings.get('endpoint_url')
    except Exception as e:
        raise Exception(f'No test settings(MONITOR_TIDB.PROVIDER) in file "test_settings.TEST_CASE"， {str(e)}')

    screen_configs.add_or_update(
        name=screen_configs.ConfigName.PROBE_QUERY_ENDPOINT_URL.value, value=query_endpoint_url)

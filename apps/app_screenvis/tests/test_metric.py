import time
from urllib import parse

from django.urls import reverse
from django.utils import timezone as dj_timezone

from apps.app_screenvis.managers import CephQueryChoices, HostQueryChoices, TiDBQueryChoices, HostQueryRangeChoices
from apps.app_screenvis.models import MetricMonitorUnit, HostNetflow
from apps.app_screenvis.permissions import ScreenAPIIPRestrictor
from . import MyAPITestCase, get_or_create_metric_ceph, get_or_create_metric_host, get_or_create_metric_tidb


class MetricCephTests(MyAPITestCase):
    def setUp(self):
        ScreenAPIIPRestrictor.clear_cache()

    def query_response(self, unit_id, query_tag: str):
        querys = {}
        if unit_id:
            querys['unit_id'] = unit_id

        if query_tag:
            querys['query'] = query_tag

        url = reverse('screenvis-api:ceph-query')
        query = parse.urlencode(query=querys)
        return self.client.get(f'{url}?{query}')

    def query_ok_test(self, unit_id: int, query_tag: str):
        response = self.query_response(unit_id=unit_id, query_tag=query_tag)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertKeysIn([query_tag, "monitor"], response.data)
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        tag_data = response.data[query_tag]
        if tag_data:
            data_item = tag_data[0]
            self.assertKeysIn(["metric", "value"], data_item)
            if data_item["value"] is not None:
                self.assertIsInstance(data_item["value"], list)
                self.assertEqual(len(data_item["value"]), 2)

        return response

    def test_query(self):
        ceph_unit = get_or_create_metric_ceph()
        ceph_unit_id = ceph_unit.id

        response = self.query_response(unit_id=666, query_tag=CephQueryChoices.MGR_STATUS.value)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        ScreenAPIIPRestrictor.add_ip_rule(ip_value='127.0.0.1')
        ScreenAPIIPRestrictor.clear_cache()

        response = self.query_response(unit_id=666, query_tag=CephQueryChoices.MGR_STATUS.value)
        self.assertEqual(response.status_code, 404)
        response = self.query_response(unit_id='666', query_tag=CephQueryChoices.MGR_STATUS.value)
        self.assertEqual(response.status_code, 404)
        response = self.query_response(unit_id='xxx', query_tag=CephQueryChoices.MGR_STATUS.value)
        self.assertEqual(response.status_code, 400)
        response = self.query_response(unit_id=ceph_unit_id, query_tag='xxx')
        self.assertEqual(response.status_code, 400)

        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.HEALTH_STATUS_DETAIL.value)
        self.assertTrue(len(r.data[CephQueryChoices.HEALTH_STATUS_DETAIL.value]) >= 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.CLUSTER_SIZE.value)
        self.assertTrue(len(r.data[CephQueryChoices.CLUSTER_SIZE.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.CLUSTER_USED_SIZE.value)
        self.assertTrue(len(r.data[CephQueryChoices.CLUSTER_USED_SIZE.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.OSD_IN_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.OSD_IN_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.OSD_OUT_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.OSD_OUT_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.OSD_UP_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.OSD_UP_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.OSD_DOWN_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.OSD_DOWN_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.MON_STATUS.value)
        self.assertTrue(len(r.data[CephQueryChoices.MON_STATUS.value]) >= 3)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.MGR_STATUS.value)
        self.assertTrue(len(r.data[CephQueryChoices.MGR_STATUS.value]) >= 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.POOL_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.POOL_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.PG_ACTIVE_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.PG_ACTIVE_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.PG_UNACTIVE_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.PG_UNACTIVE_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.PG_DEGRADED_COUNT.value)
        self.assertTrue(len(r.data[CephQueryChoices.PG_DEGRADED_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.OBJ_DEGRADED.value)
        self.assertTrue(len(r.data[CephQueryChoices.OBJ_DEGRADED.value]) == 1)
        r = self.query_ok_test(unit_id=ceph_unit_id, query_tag=CephQueryChoices.OBJ_MISPLACED.value)
        self.assertTrue(len(r.data[CephQueryChoices.OBJ_MISPLACED.value]) == 1)

        # all together
        response = self.query_response(unit_id=ceph_unit_id, query_tag=CephQueryChoices.ALL_TOGETHER.value)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)

        tags = CephQueryChoices.values
        tags.remove(CephQueryChoices.ALL_TOGETHER.value)
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        for tag in tags:
            self.assertIn(tag, response.data)
            tag_data = response.data[tag]
            self.assertIsInstance(tag_data, list)
            if tag_data:
                data_item = tag_data[0]
                self.assertKeysIn(["metric", "value"], data_item)
                if data_item["value"] is not None:
                    self.assertIsInstance(data_item["value"], list)
                    self.assertEqual(len(data_item["value"]), 2)


class MetricHostTests(MyAPITestCase):
    def setUp(self):
        ScreenAPIIPRestrictor.clear_cache()

    def query_response(self, unit_id, query_tag: str):
        querys = {}
        if unit_id:
            querys['unit_id'] = unit_id

        if query_tag:
            querys['query'] = query_tag

        url = reverse('screenvis-api:host-query')
        query = parse.urlencode(query=querys)
        return self.client.get(f'{url}?{query}')

    def query_ok_test(self, unit_id: int, query_tag: str):
        response = self.query_response(unit_id=unit_id, query_tag=query_tag)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertKeysIn([query_tag, "monitor"], response.data)
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        tag_data = response.data[query_tag]
        if tag_data:
            data_item = tag_data[0]
            self.assertKeysIn(["metric", "value"], data_item)
            if data_item["value"] is not None:
                self.assertIsInstance(data_item["value"], list)
                self.assertEqual(len(data_item["value"]), 2)

        return response

    def test_query(self):
        host_unit = get_or_create_metric_host()
        host_unit_id = host_unit.id

        response = self.query_response(unit_id=666, query_tag=HostQueryChoices.HOST_UP_COUNT.value)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        ScreenAPIIPRestrictor.add_ip_rule(ip_value='127.0.0.1')
        ScreenAPIIPRestrictor.clear_cache()

        response = self.query_response(unit_id=666, query_tag=HostQueryChoices.HOST_UP_COUNT.value)
        self.assertEqual(response.status_code, 404)
        response = self.query_response(unit_id='666', query_tag=HostQueryChoices.HOST_UP_COUNT.value)
        self.assertEqual(response.status_code, 404)
        response = self.query_response(unit_id='xxx', query_tag=HostQueryChoices.HOST_UP_COUNT.value)
        self.assertEqual(response.status_code, 400)
        response = self.query_response(unit_id=host_unit_id, query_tag='xxx')
        self.assertEqual(response.status_code, 400)

        r = self.query_ok_test(unit_id=host_unit_id, query_tag=HostQueryChoices.HOST_UP_COUNT.value)
        self.assertTrue(len(r.data[HostQueryChoices.HOST_UP_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=host_unit_id, query_tag=HostQueryChoices.HOST_DOWN.value)
        self.assertTrue(len(r.data[HostQueryChoices.HOST_DOWN.value]) >= 0)

        # all together
        response = self.query_response(unit_id=host_unit_id, query_tag=HostQueryChoices.ALL_TOGETHER.value)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)

        tags = HostQueryChoices.values
        tags.remove(HostQueryChoices.ALL_TOGETHER.value)
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        for tag in tags:
            self.assertIn(tag, response.data)
            tag_data = response.data[tag]
            self.assertIsInstance(tag_data, list)
            if tag_data:
                data_item = tag_data[0]
                self.assertKeysIn(["metric", "value"], data_item)
                if data_item["value"] is not None:
                    self.assertIsInstance(data_item["value"], list)
                    self.assertEqual(len(data_item["value"]), 2)

    def test_netflow(self):
        now_time = dj_timezone.now()
        now_ts = int(now_time.timestamp())
        host_unit1 = MetricMonitorUnit(
            name='name1', name_en='name_en1', job_tag='tag1',
            unit_type=MetricMonitorUnit.UnitType.HOST.value,
            creation_time=now_time, update_time=now_time
        )
        host_unit1.save(force_insert=True)
        host_unit2 = MetricMonitorUnit(
            name='name2', name_en='name_en2', job_tag='tag2',
            unit_type=MetricMonitorUnit.UnitType.HOST.value,
            creation_time=now_time, update_time=now_time
        )
        host_unit2.save(force_insert=True)

        hnf1 = HostNetflow(timestamp=now_ts, flow_in=1.234, flow_out=2.12, unit_id=host_unit1.id)
        hnf1.save(force_insert=True)
        hnf2 = HostNetflow(timestamp=(now_ts - 60*10), flow_in=34.254, flow_out=2.546, unit_id=host_unit1.id)
        hnf2.save(force_insert=True)
        hnf3 = HostNetflow(timestamp=(now_ts - 60*20), flow_in=4.547, flow_out=6.643222, unit_id=host_unit1.id)
        hnf3.save(force_insert=True)
        hnf4 = HostNetflow(timestamp=(now_ts - 60*22), flow_in=25.2342, flow_out=56.464, unit_id=host_unit1.id)
        hnf4.save(force_insert=True)
        hnf5 = HostNetflow(timestamp=(now_ts - 60*30), flow_in=67.6767, flow_out=9.33352, unit_id=host_unit1.id)
        hnf5.save(force_insert=True)
        u2_hnf1 = HostNetflow(timestamp=now_ts, flow_in=24.5532, flow_out=12.3532, unit_id=host_unit2.id)
        u2_hnf1.save(force_insert=True)
        u2_hnf2 = HostNetflow(timestamp=(now_ts - 60*10), flow_in=7.9433, flow_out=3.464788, unit_id=host_unit2.id)
        u2_hnf2.save(force_insert=True)
        hnf6 = HostNetflow(timestamp=(now_ts - 60 * 21), flow_in=-1, flow_out=-2, unit_id=host_unit1.id)
        hnf6.save(force_insert=True)

        url = reverse('screenvis-api:host-query-netflow')
        response = self.client.get(url)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        ScreenAPIIPRestrictor.add_ip_rule(ip_value='127.0.0.1')
        ScreenAPIIPRestrictor.clear_cache()

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 7)

        query = parse.urlencode(query={'unit_id': host_unit1.id})
        r = self.client.get(f'{url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 5)

        query = parse.urlencode(query={'unit_id': host_unit1.id, 'time': now_ts})
        r = self.client.get(f'{url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 5)
        self.assertKeysIn(['id', 'timestamp', 'unit_id', 'flow_in', 'flow_out'], r.data['results'][0])
        query = parse.urlencode(query={'unit_id': host_unit1.id, 'time': (now_ts - 60*21)})
        r = self.client.get(f'{url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 2)
        query = parse.urlencode(query={'unit_id': host_unit1.id, 'time': (now_ts - 60 * 10)})
        r = self.client.get(f'{url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 4)
        query = parse.urlencode(query={'unit_id': host_unit1.id, 'time': (now_ts - 60 * 10), 'limit': 1})
        r = self.client.get(f'{url}?{query}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 1)

        query = parse.urlencode(query={'unit_id': host_unit1.id, 'time': (now_ts - 60 * 10), 'limit': 0})
        r = self.client.get(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)
        query = parse.urlencode(query={'unit_id': host_unit1.id, 'time': (now_ts - 60 * 10), 'limit': 2001})
        r = self.client.get(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)
        query = parse.urlencode(query={'unit_id': host_unit1.id, 'time': -1})
        r = self.client.get(f'{url}?{query}')
        self.assertErrorResponse(status_code=400, code='InvalidArgument', response=r)

    def query_range_response(self, unit_id, query_tag: str, start: int, end: int, step: int):
        querys = {}
        if unit_id:
            querys['unit_id'] = unit_id

        if query_tag:
            querys['query'] = query_tag

        if start:
            querys['start'] = start

        if end:
            querys['end'] = end

        if step:
            querys['step'] = step

        url = reverse('screenvis-api:host-query-range')
        query = parse.urlencode(query=querys)
        return self.client.get(f'{url}?{query}')

    def query_range_ok_test(self, unit_id: int, query_tag: str, start: int, end: int, step: int):
        response = self.query_range_response(unit_id=unit_id, query_tag=query_tag, start=start, end=end, step=step)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertKeysIn([query_tag, "monitor"], response.data)
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        tag_data = response.data[query_tag]
        if tag_data:
            data_item = tag_data[0]
            self.assertKeysIn(["metric", "values"], data_item)
            if data_item["values"] is not None:
                self.assertIsInstance(data_item["values"], list)
                self.assertEqual(len(data_item["values"][0]), 2)

        return response

    def test_query_range(self):
        host_unit = get_or_create_metric_host()
        host_unit_id = host_unit.id

        now_ts = int(time.time())
        one_hour_ago_ts = now_ts - 60 * 60

        response = self.query_range_response(
            unit_id=666, query_tag=HostQueryRangeChoices.HOST_CPU_USAGE.value,
            start=one_hour_ago_ts, end=now_ts, step=60
        )
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        ScreenAPIIPRestrictor.add_ip_rule(ip_value='127.0.0.1')
        ScreenAPIIPRestrictor.clear_cache()

        response = self.query_range_response(
            unit_id=666, query_tag=HostQueryRangeChoices.HOST_CPU_USAGE.value,
            start=one_hour_ago_ts, end=now_ts, step=60
        )
        self.assertEqual(response.status_code, 404)
        response = self.query_range_response(
            unit_id='666', query_tag=HostQueryRangeChoices.HOST_CPU_USAGE.value,
            start=one_hour_ago_ts, end=now_ts, step=60
        )
        self.assertEqual(response.status_code, 404)
        response = self.query_range_response(
            unit_id='xxx', query_tag=HostQueryRangeChoices.HOST_CPU_USAGE.value,
            start=one_hour_ago_ts, end=now_ts, step=60
        )
        self.assertEqual(response.status_code, 400)
        response = self.query_range_response(
            unit_id=host_unit_id, query_tag='xxx', start=one_hour_ago_ts, end=now_ts, step=60)
        self.assertEqual(response.status_code, 400)

        response = self.query_range_ok_test(
            unit_id=host_unit_id, query_tag=HostQueryRangeChoices.HOST_CPU_USAGE.value,
            start=one_hour_ago_ts, end=now_ts, step=60
        )
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        data_list = response.data[HostQueryRangeChoices.HOST_CPU_USAGE.value]
        self.assertIsInstance(data_list, list)
        self.assertKeysIn(["metric", "values"], data_list[0])
        if data_list[0]["values"] is not None:
            self.assertTrue(len(data_list[0]["values"]) >= 60)

        response = self.query_range_ok_test(
            unit_id=host_unit_id, query_tag=HostQueryRangeChoices.HOST_CPU_USAGE.value,
            start=one_hour_ago_ts, end=now_ts, step=600
        )
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        data_list = response.data[HostQueryRangeChoices.HOST_CPU_USAGE.value]
        self.assertIsInstance(data_list, list)
        self.assertKeysIn(["metric", "values"], data_list[0])
        if data_list[0]["values"] is not None:
            self.assertTrue(len(data_list[0]["values"]) >= 6)

        self.query_range_ok_test(
            unit_id=host_unit_id, query_tag=HostQueryRangeChoices.HOST_CPU_USAGE_AVG.value,
            start=one_hour_ago_ts, end=now_ts, step=600
        )
        self.query_range_ok_test(
            unit_id=host_unit_id, query_tag=HostQueryRangeChoices.HOST_CPU_COUNT.value,
            start=one_hour_ago_ts, end=now_ts, step=600
        )
        self.query_range_ok_test(
            unit_id=host_unit_id, query_tag=HostQueryRangeChoices.HOST_SUM_LOAD5.value,
            start=one_hour_ago_ts, end=now_ts, step=600
        )


class MetricTiDBTests(MyAPITestCase):
    def setUp(self):
        ScreenAPIIPRestrictor.clear_cache()

    def query_response(self, unit_id, query_tag: str):
        querys = {}
        if unit_id:
            querys['unit_id'] = unit_id

        if query_tag:
            querys['query'] = query_tag

        url = reverse('screenvis-api:tidb-query')
        query = parse.urlencode(query=querys)
        return self.client.get(f'{url}?{query}')

    def query_ok_test(self, unit_id: int, query_tag: str):
        response = self.query_response(unit_id=unit_id, query_tag=query_tag)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertKeysIn([query_tag, "monitor"], response.data)
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        tag_data = response.data[query_tag]
        if tag_data:
            data_item = tag_data[0]
            self.assertKeysIn(["metric", "value"], data_item)
            if data_item["value"] is not None:
                self.assertIsInstance(data_item["value"], list)
                self.assertEqual(len(data_item["value"]), 2)

        return response

    def test_query(self):
        tidb_unit = get_or_create_metric_tidb()
        tidb_unit_id = tidb_unit.id

        response = self.query_response(unit_id=666, query_tag=TiDBQueryChoices.CONNECTIONS_COUNT.value)
        self.assertErrorResponse(status_code=403, code='AccessDenied', response=response)
        ScreenAPIIPRestrictor.add_ip_rule(ip_value='127.0.0.1')
        ScreenAPIIPRestrictor.clear_cache()

        response = self.query_response(unit_id=666, query_tag=TiDBQueryChoices.CONNECTIONS_COUNT.value)
        self.assertEqual(response.status_code, 404)
        response = self.query_response(unit_id='666', query_tag=TiDBQueryChoices.CONNECTIONS_COUNT.value)
        self.assertEqual(response.status_code, 404)
        response = self.query_response(unit_id='xxx', query_tag=TiDBQueryChoices.CONNECTIONS_COUNT.value)
        self.assertEqual(response.status_code, 400)
        response = self.query_response(unit_id=tidb_unit_id, query_tag='xxx')
        self.assertEqual(response.status_code, 400)

        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.TIDB_NODES.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.TIDB_NODES.value]) >= 3)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.TIKV_NODES.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.TIKV_NODES.value]) >= 3)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.PD_NODES.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.PD_NODES.value]) >= 3)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.CONNECTIONS_COUNT.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.CONNECTIONS_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.QPS_COUNT.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.QPS_COUNT.value]) == 1)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.STORAGE.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.STORAGE.value]) == 2)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.SERVER_CPU_USAGE.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.SERVER_CPU_USAGE.value]) == 1)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.SERVER_MEM_SIZE.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.SERVER_MEM_SIZE.value]) == 1)
        r = self.query_ok_test(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.SERVER_MEM_AVAIL.value)
        self.assertTrue(len(r.data[TiDBQueryChoices.SERVER_MEM_AVAIL.value]) == 1)

        # all together
        response = self.query_response(unit_id=tidb_unit_id, query_tag=TiDBQueryChoices.ALL_TOGETHER.value)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)

        tags = TiDBQueryChoices.values
        tags.remove(TiDBQueryChoices.ALL_TOGETHER.value)
        self.assertKeysIn(["name", "name_en", "job_tag", "id", "unit_type", 'creation_time'], response.data["monitor"])
        for tag in tags:
            self.assertIn(tag, response.data)
            tag_data = response.data[tag]
            self.assertIsInstance(tag_data, list)
            if tag_data:
                data_item = tag_data[0]
                self.assertKeysIn(["metric", "value"], data_item)
                if data_item["value"] is not None:
                    self.assertIsInstance(data_item["value"], list)
                    self.assertEqual(len(data_item["value"]), 2)

# Generated by Django 4.2.5 on 2023-11-01 06:10

from django.db import migrations, connection
from service.models import OrgDataCenter, DataCenter
from servers.models import ServiceConfig


def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def service_org_data_center(apps, schema_editor):
    # service_model = apps.get_model("service", "ServiceConfig")
    # 将来会从ServiceConfig模型移除data_center字段，无法通过model获取data_center信息。只能使用原始sql
    cursor = connection.cursor()
    cursor.execute('SELECT id, data_center_id FROM `service_serviceconfig`')
    services = dictfetchall(cursor)

    ok_count = 0
    skip_count = 0
    for sv_dict in services:
        org = DataCenter.objects.filter(id=sv_dict['data_center_id']).first()
        if org is None:
            skip_count += 1
            continue

        # 机构下没有数据中心就创建一个默认数据中心
        odc = OrgDataCenter.objects.filter(organization_id=org.id).first()
        if odc is None:
            odc = OrgDataCenter(name=f'数据中心-{org.name}', name_en='', organization_id=org.id)
            odc.save(force_insert=True)

        sv = ServiceConfig(id=sv_dict['id'])
        sv.org_data_center_id = odc.id
        sv.save(update_fields=['org_data_center_id'])
        ok_count += 1

    print(f'Changed server service ForeignKey to OrgDataCenter OK，ok={ok_count}, skip={skip_count}')


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0004_orgdatacenter_serviceconfig_org_data_center'),
    ]

    operations = [
        # migrations.RunPython(service_org_data_center, reverse_code=None),
    ]
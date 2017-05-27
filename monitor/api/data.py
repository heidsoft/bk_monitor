# -*- coding: utf-8 -*-
"""
@desc:
"""
import json

from monitor.errors import CCAPIError
from utils import decorators
from utils.common_utils import ignored
from utils.query_cc import CCBiz
from utils.trt import list_result_table_detail as trt_list_result_table_detail
from utils.trt import (filter_aggregate_table, list_datasets_by_biz_id,
                       list_fields, monitor_api_post, msg_api_get)


def access_performance(cc_biz_id, ip_list=None):
    """
    biref  : 基础性能接入
    method : POST
    """
    if ip_list is None:
        res = CCBiz.hosts(cc_biz_id)
        hosts = res.get("data", [])
        if hosts is None:
            raise CCAPIError(res["message"])

        ip_list = [{
            "plat_id": host["Source"],
            "ip": host["InnerIP"]
        } for host in hosts]
    ip_arr = [ip_info["ip"] for ip_info in ip_list]
    params = {
        "biz_id": cc_biz_id,
        "ips_info": ip_list,
        "ips": ','.join(ip_arr)
    }
    return monitor_api_post("monitor/source_performance_couplein/", params)


def get_bp_data_id(cc_biz_id):
    """
    biref  : 获取业务基础性能data id
    method : GET
    """
    data = []
    with ignored(Exception):
        data = msg_api_get(
            "list_datasets"
            , {"biz_id": cc_biz_id, "type": "sys_res"}
        ).get("data")
    return data or []


@decorators.check_param_perm
@decorators.api
def list_result_table_detail(request):
    result_tables = []
    biz_id = request.GET.get("biz_id", "")
    result_table_list = request.GET.get('result_table_list', '[]')
    result_table_list = json.loads(result_table_list)
    table_list = trt_list_result_table_detail(
        biz_id=biz_id)['data']
    if not table_list:
        table_list = []
    for table in table_list:
        if 'result_table_id' in table:
            table['id'] = table['result_table_id']
        filter_aggregate_table(result_tables, result_table_list, table)
    return result_tables


@decorators.check_param_perm
@decorators.api
def list_datasets(request):
    biz_id = request.GET.get("biz_id", "")
    datasets = list_datasets_by_biz_id(biz_id=biz_id)['data']
    if not datasets:
        datasets = []
    return datasets


@decorators.check_param_perm
@decorators.api
def list_dataset_fields(request):
    data_id = request.GET.get("data_id", "")
    return list_fields(data_id=data_id)["data"]

# -*- coding: utf-8 -*-
import json
import requests

from django.conf import settings

from utils.cache import web_cache
from utils.request_middlewares import get_request
from monitor import constants
from monitor.models import CallMethodRecord
from common.log import logger
from utils.requests_utils import INTERFACE_COMMON_PARAMS, get_bk_token


def add_storage(**kwargs):
    """
    result table 添加存储接口
    """
    return data_api_post('project/resultTable/addStorage/', kwargs)


def get_result_table(**kwargs):
    response = trt_api_get('get_result_table', kwargs)
    if response and response.get('result', False):
        response['data']['id'] = response['data'].get("result_table_id", '')
    return response


def list_result_table_detail(**kwargs):
    response = trt_api_get('list_result_table_detail_by_biz', kwargs)
    if response and response.get('result', False):
        for item in response['data']:
            item['id'] = item.get("result_table_id", '')
    return response


def get_data_id(**kwargs):
    return msg_api_get('get_data_id', kwargs)


def list_datasets_by_biz_id(**kwargs):
    return msg_api_get('list_datasets', kwargs)


def list_fields(**kwargs):
    return msg_api_get('list_fields', kwargs)


def data_api_post(action, kwargs):
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    result = requests.post(
        constants.DATA_API+action, data=json.dumps(kwargs))
    CallMethodRecord.objects.create(
        action=action, url=constants.DATA_API+action,
        param=json.dumps(kwargs), result=result.text)
    return parse_requests_result(result, action, kwargs)


def data_api_get(action, kwargs):
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    result = requests.get(
        constants.DATA_API+action, params=kwargs)
    CallMethodRecord.objects.create(
        action=action, url=constants.DATA_API+action,
        param=json.dumps(kwargs), result=result.text)
    return parse_requests_result(result, action, kwargs)


def trt_api_get(action, kwargs):
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    result = requests.get(
        constants.TRT_API+action, params=kwargs)
    result.raise_for_status()
    return result.json()


def msg_api_get(action, kwargs):
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    result = requests.get(
        constants.MSG_API+action, params=kwargs)
    result.raise_for_status()
    return result.json()


def monitor_api_post(action, kwargs):
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    result = requests.post(
        constants.JA_API+action, json=kwargs)
    result.raise_for_status()
    return result.json()


def parse_requests_result(result, action, kwargs):
    result.raise_for_status()
    if not result.json()["result"]:
        logger.error('action: %s; kwargs: %s' % (action, kwargs))
        logger.error("message: %s" % result.json()["message"])
        raise Exception(result.json()["message"])
    return result.json().get("data", "")


def filter_aggregate_table(result_tables, result_table_list, table):
    storages = table.get('storages', [])
    if len(storages) > 0:
        if table['id'] in result_table_list:
            result_tables.insert(0, table)
        else:
            result_tables.append(table)


@web_cache(60 * 60)
def get_key_alias(result_table_id):
    """获取字段的别名"""
    try:
        result = get_result_table(
            id=result_table_id,
            includes_children=False
        )
        return {field["field"]: field["description"]
                for field in result["fields"]}
    except Exception, e:
        logger.exception(e)
        return {}


def trans_bkcloud_bizid(kwargs):
    return kwargs


def trans_bkcloud_rt_bizid(result_table_id):
    return result_table_id
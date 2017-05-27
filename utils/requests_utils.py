# -*- coding: utf-8 -*-

import json
from urllib import urlencode
import requests

from django.conf import settings

from common.log import logger
from utils.request_middlewares import get_request


# 接口调用的公共参数
INTERFACE_COMMON_PARAMS = {
    'app_code': settings.APP_ID,
    'app_secret': settings.APP_TOKEN,
}

# 超时
TIMEOUT_SETTING = {
    'timeout': 60,
}


def get_bk_token():
    request = get_request()
    return request.COOKIES.get('bk_token', '')


class RequestsResultException(Exception):
    """
    对应返回状态非200，或者返回结果为False的异常
    """
    pass


def custom_requests(method, url, data=None, headers=None, **kwargs):
    """
    对request的封装
        1、添加公共参数到请求头
        2、请求失败统一处理
    @param data: dict
    :return:
    """
    # 公共参数处理
    if headers is None:
        headers = {}
    headers['content-type'] = 'application/json'
    if data is None:
        data = {}
    data.update(INTERFACE_COMMON_PARAMS)
    data['bk_token'] = get_bk_token()
    kwargs.update(TIMEOUT_SETTING)
    try:
        res = requests.request(
            method, url, data=json.dumps(data), headers=headers, **kwargs
        )
    except requests.exceptions.Timeout as e:
        logger.exception(u"接口请求超时: %s" % e)
        raise requests.exceptions.Timeout(u"接口请求网络超时")
    except Exception as e:
        logger.exception(u"接口请求异常: %s" % e)
        raise RequestsResultException(u"接口请求异常")
    # 请求失败，打log
    if res.status_code != 200:
        logger.warning('Request exception. {method} {url}: {content}'.format(
            method=method, url=url, content=res.content[:500])
        )
        raise RequestsResultException(
            u"调用接口异常，返回：%s" % res.status_code
        )
    res = json.loads(res.content)
    if not res['result']:
        logger.warning(u'Request exception. {method} {url}: {content}'.format(
            method=method, url=url, content=res['message']))
        raise RequestsResultException(u"调用接口异常：%s" % res['message'])
    return res


def requests_get(url, **kwargs):
    """
    requests get方法封装
    :return:
    """
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    url = '%s?%s' % (url, urlencode(kwargs))
    try:
        # logger.info('requests get start: %s' % url)
        res = requests.get(url, **TIMEOUT_SETTING)
        # logger.info('requests get finish: %s' % url)
    except Exception as e:
        logger.exception(u"接口请求网络异常: %s" % e)
        if settings.DEBUG:
            raise e
        return {
            "message": u"接口请求网络异常",
            "result": False,
            "data": None
        }
    res = res.json()
    if not res['result']:
        logger.warning(u'Request exception. {method} {url}: {content}'.format(
        method='get', url=url, content=res['message']))
    return res


def requests_post(url, **kwargs):
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    try:
        res = requests.post(url,
                            json=kwargs,
                            headers={'Content-Type': 'application/json'},
                            **TIMEOUT_SETTING)
        # res = requests.post(url, data=kwargs, **TIMEOUT_SETTING)
    except Exception as e:
        logger.exception(u"接口请求网络异常: %s" % e)
        if settings.DEBUG:
            raise e
        return {
            "message": u"接口请求网络异常",
            "result": False,
            "data": None
        }
    res = res.json()
    return res


def requests_delete(url, **kwargs):
    kwargs.update(INTERFACE_COMMON_PARAMS)
    kwargs['bk_token'] = get_bk_token()
    try:
        res = requests.delete(url, params=kwargs, **TIMEOUT_SETTING)
    except Exception as e:
        logger.exception(u"接口请求网络异常: %s" % e)
        if settings.DEBUG:
            raise e
        return {
            "message": u"接口请求网络异常",
            "result": False,
            "data": None
        }
    res = res.json()
    res['result'] = res.get("result", res.get("code") == '00')
    return res

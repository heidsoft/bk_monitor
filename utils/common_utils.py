# -*- coding: utf-8 -*-
import json
import arrow
import traceback
import datetime
from dateutil import tz
from collections import OrderedDict
from contextlib import contextmanager

from django.conf import settings

from common.log import logger


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions as e:
        logger.exception(traceback.format_exc())
        pass


def _host_key(host_info):
    """
    机器唯一标识
    :param host_info: 至少包含的key：InnerIP Source
    :return:
    """
    assert "InnerIP" in host_info and "Source" in host_info, \
        '"InnerIP" in host_info and "Source" in host_info return false'
    if host_info["Source"] == "0":
        host_info["Source"] = "1"
    return "%s|%s" % (host_info["InnerIP"], host_info["Source"])


def host_key(host_info=None, ip="", plat_id=""):
    if host_info is None:
        assert ip and plat_id, "ip and plat_id return false"
        host_info = {
            "InnerIP": str(ip),
            "Source": str(plat_id)
        }
    return _host_key(host_info)


def parse_host_id(host_id):
    ip, plat_id = host_id.split("|")
    return ip, plat_id


def ok(message="", **options):
    result = {'result': True, 'message': message, 'msg': message}
    result.update(**options)
    return result


def failed(message="", **options):
    if not isinstance(message, str):
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        message = str(message)
    result = {'result': False, 'message': message, 'data': {}, 'msg': message}
    result.update(**options)
    return result


def failed_data(message, data, **options):
    if not isinstance(message, str):
        if isinstance(message, unicode):
            message = message.encode('utf-8')
        message = str(message)
    result = {'result': False, 'message': message, 'data': data, 'msg': message}
    result.update(**options)
    return result


def ok_data(data=None, **options):
    if data is None:
        data = {}
    result = {'result': True, 'message': "", 'data': data, 'msg': ""}
    result.update(**options)
    return result


def href_link(text, href):
    return u"""<a href="%s">%s</a>""" % (href, text)


def strip(obj):
    if isinstance(obj, dict):
        return {key: strip(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [strip(item) for item in obj]
    elif isinstance(obj, basestring):
        return obj.strip()
    else:
        return obj


def convert_textarea_to_list(ips):
    return ips.replace('\r\n', '\n').split('\n')


def base_hostindex_id_to_page_id(_id):
    return int(_id) + 10 ** 4


def page_id_to_base_hostindex_id(_id):
    return int(_id) - 10 ** 4


def is_base_hostindex(_id):
    return int(_id) > 10 ** 4


def plat_id_gse_to_cc(plat_id):
    """
    将gse的plat_id转换成cc的plat_id
    """
    plat_id = str(plat_id)
    return plat_id if plat_id != "0" else "1"


def plat_id_cc_to_gse(plat_id):
    """
    将cc的plat_id转换成gse的plat_id
    """
    plat_id = str(plat_id)
    return plat_id if plat_id != "1" else "0"


def check_permission(obj, request_cc_biz_id):
    cc_biz_id = getattr(obj, "cc_biz_id", "")
    if not cc_biz_id:
        cc_biz_id = getattr(obj, "biz_id")
    if cc_biz_id and int(cc_biz_id) != int(request_cc_biz_id):
        return False
    return True


def safe_int(int_str, dft=0):
    try:
        int_val = int(int_str)
    except Exception, e:
        try:
            int_val = int(float(dft))
        except Exception, float_ex:
            int_val = dft
    return int_val


def filter_alarms(alarms, params):
    filter_alarm_list = []
    for alarm in alarms:
        hit = True
        for k, v in params.items():
            if k in alarm.dimensions:
                if v and v != str(alarm.dimensions[k]):
                    hit = False
            else:
                if v:
                    hit = False
        if hit:
            filter_alarm_list.append(alarm)
    return filter_alarm_list


def get_group_of_alarm(alarm_list):

    def detail(alarm):
        alarm_info = dict()
        try:
            alarm_info["alarm_dimension"] = json.loads(alarm.alarm_dimension)
        except:
            alarm_info["alarm_dimension"] = alarm.alarm_dimension
        dimensions_display_list = []
        for k, v in alarm_info["alarm_dimension"].iteritems():
            dimensions_display_list.append("%s: %s" % (k, v))
        alarm_info["dimensions_display"] = (
            ",".join(dimensions_display_list)
            if dimensions_display_list else u"全部"
        )
        alarm_info["source_timestamp"] = arrow.get(
            arrow.get(alarm.source_time).naive, tz.gettz(settings.TIME_ZONE)
        ).timestamp * 1000
        alarm_info["alarm_type"] = alarm.alarm_type
        alarm_info["alert_count"] = getattr(alarm, "alert_count")
        alarm_info["alert_ids"] = getattr(alarm, "alert_ids", [])
        alarm_info["level_display"] = u"【%s】" % alarm.get_level_display()
        alarm_info["level"] = alarm.level
        alarm_info["extend_message"] = alarm.extend_message
        alarm_info["raw"] = alarm.raw
        alarm_info["id"] = alarm.id
        return alarm_info

    result = {
        "1": [],
        "2": [],
        "3": [],
    }
    for alarm in alarm_list:
        # 按告警级别分类
        result[str(alarm.level)].append(detail(alarm))
    for k in result:
        result[k] = sorted(result[k], key=lambda x: x["source_timestamp"])
    return result


def get_unique_list(_list):
    """
    list去重，并保持原有数据顺序
    :param _list:
    :return:
    """
    return list(OrderedDict.fromkeys(_list))


def today_start_timestamp(the_day=None):
    if the_day is None:
        the_day = datetime.date.today()
    if isinstance(the_day, datetime.datetime):
        the_day = the_day.date()
    days = (the_day - datetime.date(1970, 1, 1)).days
    return days * 3600 * 24 * 1000
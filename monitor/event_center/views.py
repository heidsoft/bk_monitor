# -*- coding: utf-8 -*-
"""
@desc:事件中心
"""
import json
import traceback
import arrow
from dateutil import tz
from django.http import HttpResponseForbidden
from django.conf import settings
import time

from common.log import logger
from common.mymako import render_json, render_mako_context
from monitor.constants import ALARM_COUNTS_URL, ALARM_RECENT_URL, \
    JUNGLE_SUBJECT_TYPE
from monitor.models import MonitorLocation
from monitor.performance.models import AlarmInstance, HostIndex, Monitor
from utils import decorators
from utils.common_utils import check_permission, get_group_of_alarm, safe_int
from utils.dataview_tools import get_time_step, SeriesHandleManage, get_data
from utils.requests_utils import requests_get
from utils.trt import get_key_alias


@decorators.check_perm
def home(request, cc_biz_id):
    """首页

    :param request:
    :param cc_biz_id:
    :return:
    """
    return render_mako_context(
        request,
        '/monitor/event_center/calendar.html',
        {'cc_biz_id': cc_biz_id}
    )


@decorators.check_perm
def get_alarm_data(request, cc_biz_id):
    """获取告警列表

    :param request:
    :param cc_biz_id:
    :return:
    """
    def build_alarm_recent_data(data_list):
        """组装最近告警列表数据

        :param data_list:
        :return:
        """
        result_data_list = []
        for data in data_list:
            result_data_list.append({
                'id': data['id'],
                'alarm_attr_id': data['alarm_attr_id'],
                'source_time': data['source_time'],
                'level': data['level'],
                'status': data['user_status'],
                'alarm_content': json.loads(data['alarm_content'])
            })
        return result_data_list
    try:
        # 近期告警事件
        res = requests_get(
            ALARM_RECENT_URL,
            cc_biz_id=cc_biz_id,
            **json.loads(request.GET['params'])
        )
        if res['result']:
            res['data'] = build_alarm_recent_data(res['data']['results'])
    except Exception as e:
        logger.error(traceback.format_exc())
        res = {
            'result': False,
            'message': str(e),
            'data': []
        }
    return render_json(res)


@decorators.check_perm
def get_alarm_num_data(request, cc_biz_id, period, group_field, begin_time,
                       end_time):
    """获取告警数量统计

    :param request:
    :param cc_biz_id:
    :param period: 统计周期 [day 按天统计|hour 按小时统计]
    :param group_field: 聚合字段 按此字段group by, 例如按告警级别[level]
    :param begin_time: YYYY-MM-DD HH:mm:SS
    :param end_time: YYYY-MM-DD HH:mm:SS
    :return:
    """
    try:
        res = requests_get(ALARM_COUNTS_URL, cc_biz_id=cc_biz_id,
                           period=period, group_field=group_field,
                           time_key__gte=begin_time, time_key__lte=end_time)
    except Exception as e:
        logger.error(traceback.format_exc())
        res = {
            'result': False,
            'message': u"查询接口失败：%s" % e,
            'data': []
        }
    return render_json(res)


@decorators.check_perm
def alarm_detail(request, cc_biz_id, alarm_id):
    """
    单页的告警流程页面
    2015.10.28

    graph = [
        ({1: ['~success']}, u'155'),
        ({2: ['~success'], 3: ['failure']}, u'1134'),
        ({5: ['success']}, u'1961'),
        ({4: ['success']}, u'1958'),
        ({5: ['success']}, u'1962'),
        ({6: ['~success']}, u'807'),
        ({7: ['~success']}, u'433'),
        ({8: ['success']}, u'367'),
        ({9: ['success']}, u'1958'),
        ({10: ['~success']}, u'1968'),
        ({11: ['success']}, u'480'),
        ({12: ['success']}, u'361'),
        ({13: ['success']}, u'1965'),
        ({}, u'360')
    ]
    """
    try:
        alarm = AlarmInstance.objects.get(id=alarm_id)
    except:
        return HttpResponseForbidden(u"告警不存在")
    if not check_permission(alarm, cc_biz_id):
        return HttpResponseForbidden(u"无权限查看")

    related_alarms = [alarm]
    return render_mako_context(
        request,
        '/monitor/event_center/alarm_detail_new.html', locals())


@decorators.check_param_perm
def get_alarm_detail_chart_list(request):
    """新监控系统告警详情页-获取关联视图以及每个视图内有哪些图表"""
    result = {'result': True,
              'message': u'',
              'err_code': 0,
              'data': {"views": [], 'main_chart': {}}}
    base_info = get_alarm_detail_base_info(request)
    if not base_info.get('result', False):
        result['result'] = False
        result['message'] = base_info.get('message', '')
        return render_json(result)
    # 告警详情与监控配置
    alarm = base_info['alarm']
    monitor = base_info['monitor']
    cc_biz_id = request.GET.get("biz_id")
    if not (check_permission(alarm, cc_biz_id) or
            check_permission(monitor, cc_biz_id)):
        result['result'] = False
        result['message'] = u"无权限查看"
        return render_json(result)
    if monitor.scenario in ["performance", "custom"]:
        result['data']['main_chart'] = {
            "chart_title": monitor.monitor_name,
            "alarm_id": alarm.id,
            "monitor_id": monitor.backend_id
        }
        # 关联场景
        if monitor.scenario == "performance":
            monitor_views = MonitorLocation.objects.\
                get_scenario_menu_list_by_monitor_id(monitor.id)
            for view_info in monitor_views:
                menu_info = view_info
                menu_charts = MonitorLocation.objects.\
                    get_monitor_list_by_scenario_menu(menu_info.id)
                charts = []
                # 每个关联场景的图表
                for chart in menu_charts:
                    if chart.id == monitor.id:
                        # 当前monitor_id是大图, 不加入列表
                        continue
                    chart_config = {
                        "chart_title": chart.monitor_name,
                        "alarm_id": alarm.id,
                        "monitor_id": chart.backend_id
                    }
                    charts.append(chart_config)
                view_config = {
                    'title': menu_info.name,
                    'id': menu_info.id,
                    'charts': charts
                }
                result['data']['views'].append(view_config)
    return render_json(result)


@decorators.check_param_perm
def get_alarm_detail_main_chart_data(request):
    """新监控系统告警详情页-获取关联视图内的大图数据"""
    result = {'result': True, 'message': u'', 'err_code': 0, 'data': {}}
    base_info = get_alarm_detail_base_info(request)
    if not base_info.get('result', False):
        result['result'] = False
        result['message'] = base_info.get('message', '')
        return render_json(result)
    # 告警详情与监控配置
    alarm = base_info['alarm']
    monitor = base_info['monitor']
    cc_biz_id = request.GET.get("biz_id")
    if not (check_permission(alarm, cc_biz_id) or
            check_permission(monitor, cc_biz_id)):
        result['result'] = False
        result['message'] = u"无权限查看"
        return render_json(result)
    try:
        result_table_id = monitor.monitor_result_table_id
        monitor_field = monitor.monitor_field
        dimensions = alarm.dimensions
        alarm_source_time_date = arrow.get(
            alarm.source_time
        ).format("YYYYMMDD")
        if monitor.scenario == "custom":
            series_name = alarm.get_dimensions_display()
            step = get_time_step(
                result_table_id, monitor.generate_config_id
            ) * 1000
            result['data'] = gen_highchart_data_config(
                get_data(
                    result_table_id,
                    monitor_field,
                    dimensions,
                    method=monitor.count_method,
                    date=alarm_source_time_date
                ), series_name, step
            )
        else:
            # 基础性能监控
            key_alias = get_key_alias(result_table_id)
            hostindex = HostIndex.objects.get(id=monitor.monitor_target)
            host_dimensions = {
                "ip": alarm.ip
            }
            if hostindex.dimension_field and hostindex.dimension_field in dimensions:
                host_dimensions[hostindex.dimension_field] = dimensions[hostindex.dimension_field]
            series_name = " | ".join(
                ["%s:%s" % (JUNGLE_SUBJECT_TYPE.get(k, key_alias.get(k, k)), v)
                 for k, v in host_dimensions.items()]
            )
            result['data'] = gen_highchart_data_config(
                get_data(
                    result_table_id, hostindex.item, host_dimensions,
                    method="avg", date=alarm_source_time_date,
                    conversion=hostindex.conversion)
                , series_name, 60 * 1000)
            result['data']["unit"] = hostindex.conversion_unit.replace(
                u"个", u""
            )
        # 设置 告警信息
        try:
            setattr(alarm, "alert_count", 1)
            setattr(alarm, "alert_ids", [alarm.id])
            result['alarm_info'] = get_group_of_alarm([alarm])
        except Exception, e:
            result['alarm_info'] = {}
            logger.exception(u'告警详情-告警分组异常 %s' % e)
    except Exception, e:
        logger.exception(u'查询监控数据失败:%s' % e)
        result['result'] = False
        result['message'] = u'查询监控数据失败'
    return render_json(result)


@decorators.check_param_perm
def get_alarm_detail_sub_chart_data(request):
    """新监控系统告警详情页-获取关联视图内的其他图型数据"""
    result = {'result': True, 'message': u'', 'err_code': 0, 'data': {}}
    base_info = get_alarm_detail_base_info(request)
    if not base_info.get('result', False):
        result['result'] = False
        result['message'] = base_info.get('message', '')
        return render_json(result)
    # 告警详情与监控配置
    alarm = base_info['alarm']
    monitor = base_info['monitor']
    cc_biz_id = request.GET.get("biz_id")
    if not (check_permission(alarm, cc_biz_id) or
            check_permission(monitor, cc_biz_id)):
        result['result'] = False
        result['message'] = u"无权限查看"
        return render_json(result)
    try:
        monitor_dimensions = [d.field for d in monitor.dimensions]
        alarm_dimensions = alarm.dimensions
        common_dimensions = {}
        for dimension_key in monitor_dimensions:
            if dimension_key in alarm_dimensions.keys():
                common_dimensions[dimension_key] = alarm_dimensions[dimension_key]
        result_table_id = monitor.monitor_result_table_id
        monitor_field = monitor.monitor_field
        alarm_source_time_date = arrow.get(
            alarm.source_time
        ).format("YYYYMMDD")
        series_name = get_dimensions_display(
            common_dimensions, alarm, result_table_id
        )
        step = get_time_step(result_table_id, monitor.generate_config_id) * 1000
        result['data'] = gen_highchart_data_config(
            get_data(
                result_table_id,
                monitor_field,
                common_dimensions,
                date=alarm_source_time_date
            ), series_name, step)
    except Exception, e:
        logger.exception(u'查询监控数据失败:%s' % e)
        result['result'] = False
        result['message'] = u'查询监控数据失败'
    return render_json(result)


def get_dimensions_display(dimensions, alarm, result_table_id, sp=" | ",
                           ass=":"):

    key_alias = get_key_alias(result_table_id)

    def _render_value(key, value):
        if key == "ip":
            return u"%s[大区(%s)|模块(%s)]" % (
                value,
                alarm.cc_topo_set,
                alarm.cc_app_module)
        return value

    return sp.join([
        u"%s%s%s" % (
            JUNGLE_SUBJECT_TYPE.get(key, key_alias.get(key, key)),
            ass,
            _render_value(key, value)
        )
        for key, value in dimensions.items()
    ]) or u"全业务"


def gen_highchart_data_config(data, series_name=None, step=0):
    if not series_name:
        series_name = u'今日'
    config = {'series_name_list': [series_name], 'chart_type': 'spline',
              "x_axis": {"minRange": 3600000, "type": "datetime"},
              "yaxis_range": 0, "pointInterval": step,
              "show_percent": False}
    series_config = {'name': series_name, 'type': 'spline', 'data': data}
    x_axis = []
    y_axis = []
    for info in data:
        record_time = safe_int(info[0])/1000
        record_time_str = time.strftime(
            "%Y-%m-%d %H:%M", time.localtime(record_time)
        )
        cnt = safe_int(info[1])
        x_axis.append(record_time_str)
        y_axis.append(cnt)
    series_config['x_axis_list'] = x_axis
    config["series"] = [series_config]
    if data and step > 0:
        config["series"] = SeriesHandleManage.make_full_datetime_series(
            config["series"],
            arrow.get(safe_int(data[0][0])/1000 + 3600*8).naive,
            arrow.get(safe_int(data[0][0])/1000 + 3600*8 + (24 * 3600)).naive,
            step,
            _format="%Y-%m-%d %H:%M",
            real_time=False,
            off_set=False
        )
    return config


def get_alarm_detail_base_info(request):
    """新监控系统告警详情页-获取告警详情与监控配置"""
    result = {
        'result': True,
        'message': u'',
        'err_code': 0,
        'alarm': False,
        'monitor': False
    }
    alarm_id = safe_int(request.GET.get('alarm_id', 0))
    try:
        result['alarm'] = AlarmInstance.objects.get(id=alarm_id)
    except Exception, e:
        result['result'] = False
        result['message'] = u'查询不到id为%s的告警详情' % alarm_id
        return result

    # 监控策略
    monitor_id = safe_int(request.GET.get('monitor_id', 0))
    if monitor_id == 0:
        monitor_id = safe_int(
            result['alarm'].origin_alarm__snapshot.get('monitor_id', 0)
        )
    if monitor_id == 0:
        result['result'] = False
        result['message'] = u'查询不到此告警的监控配置'
        return result
    try:
        result['monitor'] = Monitor.objects.get(id=monitor_id)
    except Exception, e:
        result['result'] = False
        result['message'] = u'查询不到id为%s的监控配置' % monitor_id
        return result
    return result
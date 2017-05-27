# -*- coding: utf-8 -*-
"""
@desc:
"""
import json
import traceback
from urllib import urlencode
from django.http import HttpResponseForbidden, HttpResponseRedirect

import settings
from common.log import logger
from common.mymako import render_json, render_mako_context
from monitor.constants import ( ALARM_COUNTS_URL,ALARM_FREQ_URL,
                                ALARM_RECENT_URL, ALARM_EVENT_TYPE,
                                AGENT_STATUS, AGENT_SETUP_URL)
from monitor.models import MonitorLocation, OperateRecord, ScenarioMenu
from monitor.performance.models import HostIndex, Monitor
from utils import decorators
from utils.common_utils import host_key, parse_host_id, ignored
from utils.query_cc import get_user_biz, CCBiz
from utils.requests_utils import requests_get


def home(request):
    """主首页"""
    biz_list = get_user_biz(request.user)
    if not biz_list:
        return HttpResponseForbidden(u"对不起，您没有业务权限")
    cc_biz_id = request.COOKIES.get("cc_biz_id")
    if cc_biz_id not in biz_list:
        cc_biz_id = sorted(biz_list)[0]

    return HttpResponseRedirect(
        settings.SITE_URL+"%s/overview/" % cc_biz_id)


@decorators.check_perm
def overview(request, cc_biz_id):
    # 这里开始触发缓存数据，确保后续页面访问流畅。

    return render_mako_context(
        request, '/monitor/overview/overview.html', {
            'cc_biz_id': cc_biz_id,
            'AGENT_SETUP_URL': AGENT_SETUP_URL,
        }
    )


@decorators.check_perm
def render_star_panel(request, cc_biz_id):
    """
    渲染关注面板
    :param request:
    :param cc_biz_id:
    :return:
    """
    # 每页9张图
    num_per_page = 9
    try:
        current_page = int(request.GET.get("page", "1"))
    except:
        current_page = 1
    star_menu = ScenarioMenu.objects.filter(
        system_menu=u"favorite", biz_id=cc_biz_id
    )
    if not star_menu.exists():
        menus = ScenarioMenu.objects.init_biz_scenario_menu(cc_biz_id)
        locations = []
        for menu in menus:
            if menu.system_menu == u"favorite":
                star_menu = menu
    else:
        star_menu = star_menu[0]
        locations = MonitorLocation.objects.filter(
            menu_id=star_menu.id, biz_id=cc_biz_id
        ).order_by("graph_index")
    filter_loctaions = []
    for l in locations:
        if not l.monitor or l.monitor.is_deleted:
            l.is_deleted = True
            l.save()
        else:
            filter_loctaions.append(l)
    obs_count = len(filter_loctaions) + 1
    total_pages = obs_count/num_per_page + (1 if obs_count%num_per_page > 0
                                            else 0)
    filter_loctaions = filter_loctaions[num_per_page * (
        current_page - 1):num_per_page * current_page]
    monitor_count = 0
    with ignored(Exception):
        monitor_count = len(Monitor.objects.filter(
            is_deleted=False, is_enabled=True, biz_id=cc_biz_id))
    return render_mako_context(
        request, '/monitor/overview/star_chart_panel.html', locals()
    )


@decorators.check_perm
def get_event_data(request, cc_biz_id, event_type, begin_time, end_time, page):
    """获取事件列表数据

    :param request:
    :param cc_biz_id:
    :param event_type:
        最近频繁告警事件：alwaysAlert
        近期告警事件：recentAlert
        最近操作事件：recentOperate
    :param begin_time: %Y-%m-%d %H:%M:%S
    :param end_time: %Y-%m-%d %H:%M:%S
    :param page:
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
                'source_time': data['source_time'],
                'level': data['level'],
                'alarm_content': json.loads(data['alarm_content'])
            })
        return result_data_list

    try:
        if event_type == ALARM_EVENT_TYPE.alwaysAlert:
            # 最近频繁告警事件
            res = requests_get(ALARM_FREQ_URL, cc_biz_id=cc_biz_id,
                               time_key__gte=begin_time,
                               time_key__lte=end_time,
                               page=page, page_size=10)
        elif event_type == ALARM_EVENT_TYPE.recentAlert:
            # 近期告警事件
            res = requests_get(ALARM_RECENT_URL, cc_biz_id=cc_biz_id,
                               source_time__gte=begin_time,
                               source_time__lte=end_time,
                               page=page, page_size=10,
                               ordering='-source_time')
            if res['result']:
                res['data'] = build_alarm_recent_data(res['data']['results'])
        elif event_type == ALARM_EVENT_TYPE.recentOperate:
            # 操作事件
            config_types = (
                'Monitor',
                'MonitorCondition',
                'MonitorConditionConfig',
                'AlarmDef'
            )
            data_list = OperateRecord.objects.filter(
                biz_id=cc_biz_id,
                config_type__in=config_types,
                operate_time__gte=begin_time,
                operate_time__lte=end_time,
                ).exclude(operate_desc='')\
                .order_by('-operate_time')\
                .values('config_type', 'operator', 'operate', 'operate_desc',
                        'operate_time', 'operator_name', 'config_title')
            data_list = OperateRecord.build_operate_record_data(
                data_list, int(page)
            )
            OperateRecord.update_chname(data_list)
            res = {
                'result': True,
                'message': 'ok',
                'data': data_list
            }
        else:
            raise Exception(u"非法请求。event_type: %s" % event_type)
    except Exception as e:
        logger.error(traceback.format_exc())
        res = {
            'result': False,
            'message': str(e),
            'data': []
        }
    return render_json(res)


@decorators.check_perm
def get_alarm_num_data(request, cc_biz_id, period, group_field,
                       recent_intervals):
    """获取告警数量统计

    :param request:
    :param cc_biz_id:
    :param period: 统计周期 [day 按天统计|hour 按小时统计]
    :param group_field: 聚合字段 按此字段group by, 例如按告警级别[level]
    :param recent_intervals: 返回从当前时间向前recent_intervals个周期的数据
    :return:
    """
    try:
        res = requests_get(ALARM_COUNTS_URL, cc_biz_id=cc_biz_id,
                           period=period, group_field=group_field,
                           recent_intervals=int(recent_intervals)-1)
    except Exception as e:
        logger.error(traceback.format_exc())
        res = {
            'result': False,
            'message': u"查询接口失败：%s" % e,
            'data': []
        }
    return render_json(res)


@decorators.check_perm
def get_custom_monitor_num(request, cc_biz_id):
    """获取自定义监控数量

    :param request:
    :param cc_biz_id:
    :return:
    """
    try:
        # 获取自定义监控数量
        monitor_num = len(Monitor.objects.filter(biz_id=cc_biz_id,
                                                 monitor_type='custom',
                                                 is_enabled=True))
        res = {
            'result': True,
            'message': '',
            'data': monitor_num
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        res = {
            'result': False,
            'message': u"查询接口失败：%s" % e,
            'data': []
        }
    return render_json(res)


@decorators.check_perm
def get_agent_status(request, cc_biz_id):
    """获取agent安装状态

    :param request:
    :param cc_biz_id:
    :return:
    """
    hosts_list = CCBiz.hosts(cc_biz_id).get('data') or []
    hostid_list = [host_key(h) for h in hosts_list]
    agent_status_info = CCBiz.agent_status(
        cc_biz_id, hostid_list
    )
    if hosts_list and not len(agent_status_info):
        return render_json({
            'result': False,
            'message': u"查询agent状态接口失败",
            'data': []
        })
    agent_fail_cnt = agent_ok_cnt = 0
    ok_ip_list = list()
    fail_ip_list = list()
    for hostid, status in agent_status_info.iteritems():
        ip, plat_id = parse_host_id(hostid)
        if status == AGENT_STATUS.ON:
            agent_ok_cnt += 1
            ok_ip_list.append({'ip': ip, 'cc_plat_id': plat_id})
        else:
            agent_fail_cnt += 1
            fail_ip_list.append({'ip': ip, 'cc_plat_id': plat_id})
    details = {
        'agent_ok_cnt': agent_ok_cnt,
        'agent_fail_cnt': agent_fail_cnt,
        'ok_ip_list': ok_ip_list,
        'fail_ip_list': fail_ip_list,
    }
    res = {
        'result': True,
        'message': "",
        'data': agent_ok_cnt,
        'details': details
    }

    return render_json(res)


@decorators.check_perm
def get_agent_data_report_status(request, cc_biz_id):
    """获取agent上报数据状态

    :param request:
    :param cc_biz_id:
    :return:
    """
    try:
        res = HostIndex.data_report_info(cc_biz_id)
        res = {
            'result': True,
            'message': '',
            'data': res
        }
    except Exception as e:
        logger.error(traceback.format_exc())
        res = {
            'result': False,
            'message': u"获取主机上报状态失败: %s" % e,
            'data': []
        }
    return render_json(res)

# -*- coding: utf-8 -*-
"""
@desc:
"""
import hashlib
import json
import uuid

import arrow
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden

from common.log import logger
from common.mymako import render_json, render_mako_context
from monitor.config.access import DataAccess, DataSetAccess
from monitor.constants import NOTIRY_MAN_STR_DICT, JOB_URL
from monitor.errors import JAItemDoseNotExists, JAAPIError
from monitor.models import AlarmStrategy, Shield
from monitor.performance.models import (AlarmDef, AlarmInstance, BaseHostIndex,
                                        HostIndex, Monitor, MonitorCondition)
from monitor.performance.solutions import SolutionConf
from utils import decorators, query_cc
from utils.common_utils import (check_permission, failed, failed_data, ignored,
                                is_base_hostindex, ok_data,
                                page_id_to_base_hostindex_id, safe_int,
                                base_hostindex_id_to_page_id)
from utils.query_cc import get_nick_by_uin, get_owner_info, get_plat
from utils.time_status import TimeStats
from utils.trt import trans_bkcloud_rt_bizid

ACCESS_CLASS = {
    "trt": DataAccess,
    "dataset": DataSetAccess,
}


@decorators.check_perm
def bp_config_monitor(request, cc_biz_id, alarm_strategy_id):
    """
    基础性能监控页面，快速新增/编辑监控
    """
    # 获取基础性能指标列表
    ts = TimeStats(u"open_bp_config_page: %s" % cc_biz_id)
    s_id = uuid.uuid4()
    hostindex = monitor = None
    monitor_id = 0
    args_hostindex_id = safe_int(request.GET.get("hostindex_id"))
    ts.split(u"判断操作是新增还是编辑，拉取监控项id")
    monitors = Monitor.objects.filter(scenario__in='performance,base_alarm')
    try:
        alarm_strategy_id = int(alarm_strategy_id)
        if alarm_strategy_id:
            monitor_id = AlarmStrategy.objects.get(
                id=alarm_strategy_id
            ).monitor_id
            monitor = filter(lambda m: m.id == monitor_id, monitors)[0]
        else:
            monitor_id = safe_int(request.GET.get("monitor_id"))
            if monitor_id:
                monitor = filter(lambda m: m.id == monitor_id, monitors)[0]
    except ValueError:
        alarm_strategy_id = 0
    ts.split(u"获取hostindex指标")
    # 获取hostindex指标
    if monitor is not None:
        if not check_permission(monitor, cc_biz_id):
            return HttpResponseForbidden(u"无权限")
        if monitor.scenario == "performance":
            hostindex = HostIndex.objects.get(
                item=monitor.monitor_field,
                result_table_id=monitor.monitor_result_table_id.split("_", 1)[1]
            )
        else:
            hostindex = BaseHostIndex.objects.get(title=monitor.monitor_field)
    else:
        if args_hostindex_id:
            if is_base_hostindex(args_hostindex_id):
                hostindex = BaseHostIndex.objects.get(
                    alarm_type=page_id_to_base_hostindex_id(args_hostindex_id)
                )
            else:
                hostindex = HostIndex.objects.get(id=args_hostindex_id)
    ts.split(u"获取hostindex指标列表")
    # 性能指标信息
    host_list = AlarmStrategy.get_host_info(cc_biz_id, s_id, monitors=monitors)
    # 基础告警指标
    ts.split(u"获取base_hostindex指标列表")
    host_list.append(AlarmStrategy.get_base_hostindex(cc_biz_id, s_id, monitors=monitors))
    if hostindex is None:
        ts.split(u"获取默认hostindex指标")
        # 设置默认值
        hostindex = HostIndex.objects.filter(graph_show=True)[0]
        if alarm_strategy_id == 0 and request.GET.get("monitor_id"):
            monitor = Monitor.objects.get(id=request.GET.get("monitor_id"))
            hostindex = HostIndex.objects.get(
                item=monitor.monitor_field,
                result_table_id=monitor.monitor_result_table_id.split("_", 1)[1]
            )
    # 用户信息
    # 目前只有运维一种角色
    ts.split(u"获取用户信息")
    # maintainers = query_cc.CCBiz.maintainers(cc_biz_id)
    user_info_list = get_owner_info()
    # 其他通知人(包含运维角色，这里实际是全部人员)
    other_users = {item['username']: item['chname'] for item in user_info_list}
    ctx = {
        'multiple': request.GET.get("multiple", "0"),
        'alarm_strategy_id': alarm_strategy_id,
        'monitor_id': monitor_id,
        'host_list': host_list,
        'hostindex': hostindex,
        # 'plat_list': get_plat(cc_biz_id),
        # 'maintainers': maintainers,
        'other_users': other_users,
        'JOB_URL': "%s/?newTask&appId=%s" % (JOB_URL, cc_biz_id),
        'args_hostindex_id': safe_int(args_hostindex_id),
    }
    ts.stop()
    logger.warning(ts.display())
    return render_mako_context(
        request, '/monitor/configV2/base_performance.html', ctx
    )


@decorators.check_perm
def get_bp_strategy(request, cc_biz_id):
    """
    告警配置页面的告警策略
    """
    alarm_strategy_id = request.GET.get('alarm_strategy_id', '0')
    alarm_strategy = None
    try:
        alarm_strategy_id = int(alarm_strategy_id)
        if alarm_strategy_id and alarm_strategy_id > 0:
            alarm_strategy = AlarmStrategy.objects.get(id=alarm_strategy_id)
            if not check_permission(alarm_strategy, cc_biz_id):
                return render_json(failed(u"无权限"))
    except:
        logger.exception(u"无效的告警策略id：%s" % alarm_strategy_id)

    # 编辑告警策略，获取已有告警策略信息
    return render_json(ok_data(alarm_strategy_obj_to_dict(alarm_strategy)))


@decorators.check_perm
def get_strategy_id_by_condition(request, cc_biz_id):
    """
    根据告警条件获取监控项下策略id，如果没有返回0
    """
    monitor_id = request.POST.get("monitor_id")
    condition_params = request.POST.get("condition")
    condition = dict()
    with ignored(Exception):
        condition = json.loads(condition_params)

    s_id, strategys = AlarmStrategy.get_by_monitor_id(monitor_id)
    for strategy in strategys:
        if not check_permission(strategy, cc_biz_id):
            return render_json(failed(u"无权限"))
        match = True
        condition_dict = {}
        condition_list = json.loads(strategy.condition)
        if condition_list and isinstance(condition_list[0], dict):
            condition_list = [condition_list]
        if len(condition_list) != 1:
            match = False
        else:
            condition_list = condition_list[0]
            for c in condition_list:
                if (c.get("method") != "eq" or
                        not c.get("field") or
                        not c.get("value")):
                    match = False
                    break
                else:
                    condition_dict[c.get("field")] = c.get("value")
        if not match:
            continue
        if condition_dict == condition:
            return render_json(ok_data({"id": strategy.id, "s_id": str(s_id)}))
    return render_json(ok_data({"id": 0, "s_id": str(s_id)}))


def alarm_strategy_obj_to_dict(alarm_strategy):
    """
    告警策略缓存表解析为字典
    """
    # solution_id = ''
    # 告警级别默认为 2 (普通)
    monitor_level = 2
    # 算法默认为 1000 (静态阈值)
    monitor_name = ""
    display_name = ""
    strategy_id = 1000
    responsible = []
    strategy_option = {}
    notify_way = {}
    role_list = []
    rules = {'converge_id': "0"}
    prform_cate = 'ip'
    ip = ''
    cc_module = ''
    cc_set = ''
    phone_receiver = ''
    notice_start_hh, notice_start_mm, notice_end_hh, notice_end_mm = ("00", "00", "23", "59")
    condition = {}
    solution_is_enable = False
    solution_type = "job"
    solution_task_id = ""
    solution_notice = []
    solution_params_replace = ""
    solution_display = u"不处理，仅通知"
    if alarm_strategy is not None:
        display_name = alarm_strategy.display_name
        monitor_name = alarm_strategy.monitor_name
        prform_cate = alarm_strategy.prform_cate
        ip = alarm_strategy.ip
        cc_module = alarm_strategy.cc_module
        cc_set = alarm_strategy.cc_set
        monitor_level = alarm_strategy.monitor_level
        strategy_id = alarm_strategy.strategy_id
        # solution_id = alarm_strategy.solution_id
        phone_receiver = alarm_strategy.notify_dict.get("phone_receiver", "")
        phone_receiver = phone_receiver.split(",") if phone_receiver else []
        notice_start_hh, notice_start_mm = alarm_strategy.notify_dict.get(
            "alarm_start_time", "00:00"
        ).split(":")
        notice_end_hh, notice_end_mm = alarm_strategy.notify_dict.get(
            "alarm_end_time", "00:00"
        ).split(":")

        if alarm_strategy.responsible:
            responsible = alarm_strategy.responsible.split(",")

        try:
            strategy_option = json.loads(alarm_strategy.strategy_option)
        except:
            logger.error(
                u"告警策略[id:%s]中算法参数格式错误" % alarm_strategy.id
            )

        try:
            notify_way = json.loads(alarm_strategy.notify_way)
        except:
            logger.error(
                u"告警策略[id:%s]中通知方式格式错误" % alarm_strategy.id
            )

        try:
            alarm_solution_config = json.loads(alarm_strategy.alarm_solution_config)
            if alarm_solution_config:
                solution_is_enable = alarm_solution_config["is_enabled"]
                solution_type = alarm_solution_config["solution_type"]
                solution_config = json.loads(alarm_solution_config["config"])
                solution_task_id = solution_config["job_task_id"]
                for params_key in solution_config:
                    if params_key.startswith("param") and params_key != "params":
                        solution_params_replace = "replace"
                solution_notice = []
                notify = json.loads(alarm_strategy.notify)
                for key in notify.keys():
                    for word in ["begin", "end"]:
                        if key.startswith("%s_notify_" % word) and notify[key]:
                            solution_notice += [word]
                if solution_is_enable and solution_task_id:
                    solution_display = (
                        u"【%s】%s" % (
                            SolutionConf.solution_type_display_name(
                                solution_type
                            ),
                            solution_config['job_task_name'])
                    )
        except Exception, e:
            logger.error(
                u"告警策略[id:%s]中自动处理参数格式错误" % alarm_strategy.id
            )

        try:
            role_list = json.loads(alarm_strategy.role_list)
        except:
            logger.error(u"告警策略[id:%s]中通知人格式错误" % alarm_strategy.id)

        try:
            condition = json.loads(alarm_strategy.condition)
        except:
            logger.error(
                u"告警策略[id:%s]中告警范围格式错误" % alarm_strategy.id
            )

        if responsible:
            role_list.append("other")

        try:
            rules = json.loads(alarm_strategy.rules)
        except:
            logger.error(
                u"告警策略[id:%s]中收敛规则格式错误" % alarm_strategy.id
            )
    return {
        'condition_str': (
            alarm_strategy.condition_str if alarm_strategy else ""
        ),
        'nodata_alarm': alarm_strategy.nodata_alarm if alarm_strategy else 0,
        'notify_way_str': (
            alarm_strategy.notify_way_str_v2 if alarm_strategy else u""
        ),
        'notify_man_html': (
            gen_notify_man_html(alarm_strategy) if alarm_strategy else ""
        ),
        'converge_str': (
            alarm_strategy.converge_str if alarm_strategy else u"系统默认"
        ),
        'strategy_desc': (
            alarm_strategy.strategy_desc if alarm_strategy else ""
        ),
        'strategy_name': (
            alarm_strategy.strategy_name if alarm_strategy else ""
        ),
        'alarm_strategy_id': alarm_strategy.id if alarm_strategy else "",
        'monitor_name': monitor_name,
        'display_name': display_name,
        'monitor_level': monitor_level,
        'strategy_id': strategy_id,
        # 'solution_id': solution_id,
        'responsible': responsible,
        'strategy_option': strategy_option,
        'notify_way': notify_way,
        'role_list': role_list,
        'rules': rules,
        'prform_cate': prform_cate,
        'ip': ip,
        'cc_module': cc_module,
        'cc_set': cc_set,
        'condition': condition,
        # 'solutions_list': solutions_list,
        'phone_receiver': phone_receiver,
        'notice_start_hh': notice_start_hh,
        'notice_start_mm': notice_start_mm,
        'notice_end_hh': notice_end_hh,
        'notice_end_mm': notice_end_mm,
        'solution_is_enable': solution_is_enable,
        'solution_type': solution_type,
        'solution_notice': solution_notice,
        'solution_task_id': solution_task_id,
        'solution_params_replace': solution_params_replace,
        'solution_display': solution_display,
    }


def gen_notify_man_html(alarm_strategy):
    if alarm_strategy is None:
        return ""
    notify_man_html = AlarmStrategy.get_notify_html_by_role(
        alarm_strategy.cc_biz_id, alarm_strategy.role_list
    )
    # 额外通知人
    if alarm_strategy.responsible:
        responsible_str_format = NOTIRY_MAN_STR_DICT.get('responsible')
        responsible_str = responsible_str_format % "; ".join(
            get_nick_by_uin(
                alarm_strategy.responsible, show_detail=True
            ).values()
        )
        notify_man_html += responsible_str
    # 电话通知人
    notify_dict = alarm_strategy.notify_dict
    if notify_dict.get("phone_receiver"):
        phone_receiver_nick_list = get_nick_by_uin(
            notify_dict.get("phone_receiver"), show_detail=True
        ).values()
        notify_man_html += (
            NOTIRY_MAN_STR_DICT.get('phone_receiver') %
            "; ".join(phone_receiver_nick_list)
        )
    return notify_man_html


@decorators.check_perm
def get_strategy_alarm_list(request, cc_biz_id):
    """
    获取告警策略关联的告警事件
    """
    args = request.GET
    alarm_date = args.get("alarm_date")
    strategy_id = args.get("strategy_id")
    if not strategy_id:
        return render_json(failed(u"无效的请求"))
    try:
        alarm_strategy = AlarmStrategy.objects.get(id=strategy_id)
    except AlarmStrategy.DoesNotExist:
        return render_json(ok_data({"alarm_info_list": []}))
    if not alarm_strategy.alarm_def_id:
        return render_json(ok_data({"alarm_info_list": []}))
    alarm_list = AlarmInstance.get_alarm_list_by_strategy_id(
        alarm_strategy, alarm_date, cc_biz_id
    )
    alarm_info_list = filter(
        lambda alarm: alarm,
        map(lambda a: a.detail, alarm_list)
    )
    return render_json(ok_data({"alarm_info_list": alarm_info_list}))


@decorators.check_perm
def save_bp_strategy(request, cc_biz_id):
    """
    保存基础性能监控
    """
    if request.method != 'POST':
        return render_json(failed(u"请使用 POST 请求"))
    args = request.POST

    try:
        hostindex_id = safe_int(args.get("hostindex_id"))
        scenario = 'performance'
        if is_base_hostindex(hostindex_id):
            host_index = BaseHostIndex.objects.get(
                alarm_type=page_id_to_base_hostindex_id(hostindex_id)
            )
            hostindex_id = host_index.real_id
            scenario = host_index.category
        else:
            host_index = HostIndex.objects.get(id=hostindex_id)
            hostindex_id = host_index.id
    except JAItemDoseNotExists:
        return render_json(failed(u"无效的监控项"))
    # 监控源
    result_table_id = host_index.result_table_id
    monitor_result_table_id = '%s_%s' % (cc_biz_id, result_table_id)
    monitor_result_table_id = trans_bkcloud_rt_bizid(monitor_result_table_id)
    monitors = Monitor.objects.filter(
        is_deleted=False, scenario=scenario,
        biz_id=cc_biz_id, monitor_target=hostindex_id
    )
    if monitors:
        # 已有监控项，创建/更新告警策略
        monitor = monitors[0]
    else:
        # 把monitor_field, dimensions, count_freq和aggregator加入access_params中
        dimensions = host_index.table_dimensions
        if (not dimensions) or (type(dimensions) is not list):
            dimensions = []
        access_params = {
            "biz_id": cc_biz_id,
            "title": host_index.desc,
            "monitor_target": host_index.item,
            "target_result_table_id": monitor_result_table_id,
            "source_type": 'result_table',
            "source_id": monitor_result_table_id,
            "agg_method": 'max',
            "count_freq": 60,
            "dimensions": '|'.join(dimensions)
        }
        # 无监控项，将告警策略配置带上一起创建
        try:
            monitor = Monitor.create(
                cc_biz_id,
                scenario,
                host_index.category,
                host_index.desc,
                host_index.desc,
                hostindex_id,
                monitor_result_table_id,
                host_index.item,
                access_params=access_params
            )
        except JAAPIError, e:
            logger.error(u"创建监控项接口调用失败: %s" % e)
            return failed(u"创建监控项失败")
    # 监控项
    user_name = request.user.username
    alarm_strategy_id = safe_int(args.get("alarm_strategy_id"))
    s_id = args.get('s_id', '')
    if not s_id:
        return render_json(failed(u"告警策略id错误!"))
    prform_cate = args.get('prform_cate', '')
    ip = args.get('ip', '')
    cc_module = args.get('cc_module', '')
    if cc_module in ["", "0"]:
        cc_module = ""
    cc_set = args.get('cc_set', '')
    if cc_set in ["", "0"]:
        cc_set = ""
    monitor_level = args.get('monitor_level', '')
    if not monitor_level:
        return render_json(failed(u"请填写告警级别"))
    # 算法
    strategy_id = args.get('strategy_id', '')
    if not strategy_id:
        return render_json(failed(u"请选择算法"))
    # 算法参数
    strategy_option = args.get('strategy_option', '{}')
    # 通知处理
    alarm_start_time = args.get('alarm_start_time', "00:00")
    alarm_end_time = args.get('alarm_end_time', "00:00")
    phone_receiver = args.get('phone_receiver', '')
    responsible = args.get('responsible', '')
    notify_way = args.getlist('notify_way[]', [])
    role_list = args.getlist('role_list[]', [])
    if not notify_way:
        return render_json(failed(u"请勾选至少一种通知方式"))
    if "phone" in notify_way and not phone_receiver:
        return render_json(failed(u"请选择至少一个电话联系人"))
    if not role_list:
        return render_json(failed(u"请选择至少一个通知角色"))
    if "other" in role_list and not responsible:
        return render_json(failed(u"请选择至少一个其他通知人"))
    if responsible:
        role_list.remove("other")
    notify = {
        'alarm_start_time': alarm_start_time,
        'alarm_end_time': alarm_end_time,
        'responsible': responsible,
        'phone_receiver': phone_receiver,
        'role_list': role_list,
    }
    solution_notice = args.getlist('solution_notice[]', []) + [""]
    for way in notify_way:
        for sep in solution_notice:
            if sep:
                sep += "_"
            notify["%snotify_%s" % (sep, way)] = True
    # 收敛规则
    rules = args.get('rules', '{}')
    if not rules:
        return render_json(failed(u"请选填写收敛规则"))
    # 保存数据
    data = {
        'display_name': host_index.desc,
        'cc_biz_id': cc_biz_id,
        's_id': s_id,
        'monitor_level': monitor_level,
        'strategy_id': strategy_id,
        'condition': '{}',
        'strategy_option': strategy_option,
        'rules': rules,
        'updator': user_name,
        'prform_cate': prform_cate,
        'ip': ip,
        'cc_module': cc_module,
        'cc_set': cc_set,
        'nodata_alarm': safe_int(args.get("nodata_alarm", 0)),
        'responsible': responsible,
        'notify_way': json.dumps(notify_way),
        'role_list': json.dumps(role_list),
        'notify': json.dumps(notify),
        'scenario': "performance",
    }

    # 自动处理
    solution_type = args.get("solution_type")
    solution_task_id = args.get("solution_task_id") or ""
    solution_is_enable = args.get("solution_is_enable") == "true"
    solution_params_replace = args.get("solution_params_replace", "")
    if solution_task_id:
        solution = SolutionConf.get_solution_obj(
            solution_type,
            cc_biz_id,
            solution_task_id,
            is_enabled=solution_is_enable,
            solution_params_replace=solution_params_replace,
        )
        alarm_solution_config = solution.gen_solution_config()
        data["alarm_solution_config"] = json.dumps(alarm_solution_config)

    return render_json(
        AlarmStrategy.objects.update_config_by_strategy_data(
            alarm_strategy_id, data, monitor
        )
    )


@decorators.check_perm
def save_custom_strategy(request, cc_biz_id):
    """
    保存自定义监控
    """
    if request.method != 'POST':
        return render_json(failed(u"请使用 POST 请求"))
    args = request.POST
    monitor_id = int(args.get("monitor_id", "0"))
    if monitor_id != 0:
        try:
            monitor = Monitor.objects.get(id=monitor_id)
        except Monitor.DoesNotExist:
            return render_json(failed(u"无效的监控"))
    else:
        monitor = None
    s_id = args.get('s_id', '')
    if not s_id:
        return render_json(failed(u"告警策略id错误!"))
    # 监控项
    alarm_strategy_id = args.get("alarm_strategy_id", 0)
    try:
        alarm_strategy_id = int(alarm_strategy_id)
    except:
        return render_json(failed(u"告警策略id[%s]错误!" % alarm_strategy_id))

    monitor_level = args.get('monitor_level', '')
    if not monitor_level:
        return render_json(failed(u"请填写告警级别"))

    # 算法
    strategy_id = args.get('strategy_id', '')
    if not strategy_id:
        return render_json(failed(u"请选择算法"))

    # 算法参数
    strategy_option = args.get('strategy_option', '{}')

    # 通知处理
    alarm_start_time = args.get('alarm_start_time', "00:00")
    alarm_end_time = args.get('alarm_end_time', "00:00")
    phone_receiver = args.get('phone_receiver', '')
    responsible = args.get('responsible', '')
    notify_way = args.getlist('notify_way[]', [])
    role_list = args.getlist('role_list[]', [])
    if not notify_way:
        return render_json(failed(u"请勾选至少一种通知方式"))
    if "phone" in notify_way and not phone_receiver:
        return render_json(failed(u"请选择至少一个电话联系人"))
    if not role_list:
        return render_json(failed(u"请选择至少一个通知角色"))
    if "other" in role_list and not responsible:
        return render_json(failed(u"请选择至少一个其他通知人"))
    if responsible:
        role_list.remove("other")
    notify = {
        'alarm_start_time': alarm_start_time,
        'alarm_end_time': alarm_end_time,
        'responsible': responsible,
        'phone_receiver': phone_receiver,
        'role_list': role_list,
    }
    solution_notice = args.getlist('solution_notice[]', []) + [""]
    for way in notify_way:
        for sep in solution_notice:
            if sep:
                sep += "_"
            notify["%snotify_%s" % (sep, way)] = True
    # 收敛规则
    rules = args.get('rules', '{}')
    if not rules:
        return render_json(failed(u"请选填写收敛规则"))

    # 保存数据
    data = {
        'display_name': args.get("display_name", ""),
        'cc_biz_id': cc_biz_id,
        's_id': s_id,
        'monitor_level': monitor_level,
        'strategy_id': strategy_id,
        'strategy_option': strategy_option,
        'rules': rules,
        'updator': request.user.username,
        # add
        'responsible': responsible,
        'notify_way': json.dumps(notify_way),
        'role_list': json.dumps(role_list),
        'notify': json.dumps(notify),
        'condition': args.get("condition", '{}'),
        'scenario': "custom",
        'nodata_alarm': safe_int(args.get("nodata_alarm", 0))
    }
    # 自动处理
    solution_type = args.get("solution_type")
    solution_task_id = args.get("solution_task_id") or ""
    solution_is_enable = args.get("solution_is_enable") == "true"
    if solution_task_id:
        solution = SolutionConf.get_solution_obj(
            solution_type,
            cc_biz_id,
            solution_task_id,
            is_enabled=solution_is_enable,
        )
        alarm_solution_config = solution.gen_solution_config()
        data["alarm_solution_config"] = json.dumps(alarm_solution_config)
    return render_json(
        AlarmStrategy.objects.update_config_by_strategy_data(
            alarm_strategy_id, data, monitor
        )
    )


@decorators.check_perm
def duplication_strategy(request, cc_biz_id):
    # set 模式只判断是否相等
    # ip 模式判断是否包含。
    args = request.POST
    hostindex_id = args.get("hostindex_id", "")
    # 监控源
    if is_base_hostindex(hostindex_id):
        base_hostindex = BaseHostIndex.objects.get(id=hostindex_id)
        monitors = Monitor.objects.filter(
            scenario='base_alarm', biz_id=cc_biz_id,
            monitor_field=base_hostindex.title)
    else:
        try:
            host_index = HostIndex.objects.get(id=hostindex_id)
        except HostIndex.DoesNotExist:
            return render_json(failed(u"无效的监控项"))
        result_table_id = host_index.result_table_id
        monitor_result_table_id = '%s_%s' % (cc_biz_id, result_table_id)
        monitor_result_table_id = trans_bkcloud_rt_bizid(monitor_result_table_id)
        monitors = Monitor.objects.filter(
            scenario='performance', biz_id=cc_biz_id,
            monitor_field=host_index.item,
            monitor_result_table_id=monitor_result_table_id
        )
    if not len(monitors) > 0:
        return render_json(ok_data())
    else:
        monitor = monitors[0]
    prform_cate = args.get("prform_cate", "")
    alarm_strategy_id = args.get("alarm_strategy_id", "")
    try:
        alarm_strategy_id = int(alarm_strategy_id)
    except ValueError:
        render_json(failed(u"检测监控策略失败，无效的监控策略。"))
    ip = args.get("ip", "")
    cc_module = args.get('cc_module', '')
    if cc_module in ["", "0"]:
        cc_module = ""
    cc_set = args.get('cc_set', '')
    if cc_set in ["", "0"]:
        cc_set = ""
    _, strategys = AlarmStrategy.get_by_monitor_id(monitor)

    for strategy in strategys:
        if alarm_strategy_id != 0 and AlarmStrategy.objects.get(
                id=alarm_strategy_id).alarm_def_id == strategy.alarm_def_id:
            continue
        if strategy.prform_cate != prform_cate:
            continue
        if (prform_cate == "set" and
            cc_set == strategy.cc_set and
            cc_module == strategy.cc_module):
            return render_json(
                failed_data(
                    u"已存在相同监控范围的策略,点击确定继续提交", strategy.id
                )
            )
        if prform_cate == "ip":
            s_ip_set = set(strategy.ip.split(","))
            ip_set = set(ip.split(","))
            if ip_set.issubset(s_ip_set):
                return render_json(
                    failed_data(
                        u"已存在包含此次配置的ip的策略,点击确定继续提交",
                        strategy.id
                    )
                )
    return render_json(ok_data())


@decorators.check_perm
def shield_info(request, cc_biz_id):
    """
    屏蔽配置信息
    """
    shield_id = request.GET.get("shield_id")
    try:
        shield = Shield.objects.get(id=shield_id)
    except Shield.DoesNotExist:
        return render_json(failed(u"无效的屏蔽id"))
    if not check_permission(shield, cc_biz_id):
        return render_json(failed(u"无权限"))
    dimension = shield.dimension
    dimension = json.loads(dimension)
    end_time = shield.end_time.strftime("%Y-%m-%d %H:%M:%S")
    category = dimension.get("category", [""])[0]
    key_list = [
        "alarm_source_id",
        "hours_delay",
        "category",
        "alarm_attr_id",
        "source_type",
        "cc_topo_set",
        "cc_biz_id",
        "cc_app_module",
        "monitor_target"
    ]
    monitor_field_list = []
    set = mod = ip = monitor_target = perform_cate = ""
    alarm_source_id = "0"
    if category == "custom":
        alarm_source_id = dimension.get("alarm_source_id", ["0"])[0]
        if alarm_source_id and alarm_source_id != "0":
            alarm_source_id = AlarmDef.objects.get(id=alarm_source_id).id
        monitor_target = dimension["alarm_attr_id"][0]
        monitor_target = Monitor.objects.get(id=monitor_target).id
        # monitor_field_list 暂时禁用，页面隐藏入口
        for k in dimension:
            if k in key_list:
                continue
            monitor_field_list.append([k, ",".join(dimension[k])])

    if category in ["performance", "base_alarm"]:
        monitor_target = dimension["monitor_target"][0]
        if category == "base_alarm":
            monitor_target = base_hostindex_id_to_page_id(monitor_target)
        perform_cate = "ip"
        ip = ",".join(dimension.get("ip", []))
        if ("ip" not in dimension and
                ("cc_topo_set" in dimension or "cc_app_module" in dimension)):
            perform_cate = "set"
            set = ",".join(dimension["cc_topo_set"])
            mod = ",".join(dimension["cc_app_module"])

    shield_info = {
        'alarm_source_id': alarm_source_id,
        'hours_delay': shield.hours_delay,
        'end_time': end_time,
        'category': category,
        'monitor_target': monitor_target,
        'perform_cate': perform_cate,
        'set': set,
        'mod': mod,
        "ip": ip,
        'shield_desc': shield.description,
        'monitor_field_list': monitor_field_list
    }
    return render_json(ok_data(shield_info))


@decorators.check_perm
def get_alarmdef_by_monitor_id(request, cc_biz_id):
    """
    根据监控项id获取告警定义信息
    """
    monitor_id = request.GET.get("monitor_id", "0")
    monitor = None
    with ignored(ValueError, JAItemDoseNotExists):
        monitor_id = int(monitor_id)
        monitor = Monitor.objects.get(id=monitor_id)
    if not monitor:
        return render_json(failed(u"无效的监控项id"))
    if not check_permission(monitor, cc_biz_id):
        return render_json(failed(u"无权限"))
    result = AlarmDef.get_alarmdef_info_by_monitor(monitor)
    result.insert(0, {'id': '0', 'text': u'全部策略'})
    return render_json(ok_data(result))


@decorators.check_perm
def operate_alram(request, cc_biz_id, alram_strategy_id):
    """
    启用/停用 告警策略
    """
    try:
        is_enabled = request.POST.get('is_enabled', '1')
        is_enabled = int(is_enabled)
    except:
        logger.exception(u"启用/停用 告警策略，参数错误")
        return render_json(
            {'result': False, 'message': u"启用/停用 告警策略，参数错误"}
        )
    # 更新操作信息
    tip = u"启用" if is_enabled else u"停用"
    if safe_int(alram_strategy_id) == 0:
        return render_json(
            {
                'result': False,
                'message': u"告警策略id[%s]错误!" % alram_strategy_id
            }
        )
    try:
        alarm = AlarmStrategy.objects.get(id=alram_strategy_id)
    except AlarmStrategy.DoesNotExist:
        return render_json({'result': False, 'message': u"无效的请求"})
    if not check_permission(alarm, cc_biz_id):
        return render_json(failed(u"无权限"))
    try:
        alarm.toggle(is_enabled)
    except Exception as e:
        logger.exception(u"%s告警策略[id:%s]出错: %s" % (tip, alarm.id, e))
        return render_json(
            {'result': False, 'message': u"%s出错，参数错误" % tip}
        )

    return render_json({'result': True, 'message': u"%s成功" % tip})


@decorators.check_perm
def del_strategy(request, cc_biz_id, alram_strategy_id):
    """
    删除告警策略
    """
    if request.method != 'POST':
        return render_json({'result': False, 'message': u"请使用 POST 请求"})
    if safe_int(alram_strategy_id) == 0:
        return render_json(
            {
                'result': False,
                'message': u"告警策略id[%s]错误!" % alram_strategy_id
            }
        )
    try:
        alarm = AlarmStrategy.objects.get(id=alram_strategy_id)
    except AlarmStrategy.DoesNotExist:
        return render_json({'result': False, 'message': u"无效的请求"})
    if alarm and not check_permission(alarm, cc_biz_id):
        return render_json(failed(u"无权限"))
    try:
        alarm.delete()
    except Exception as e:
        logger.exception(
            u"告警策略[id:%s]删除失败: %s" % (alram_strategy_id, e)
        )
        return render_json(
            {'result': False, 'message': u"告警策略删除失败"}
        )

    return render_json({'result': True, 'message': u"删除成功"})


@decorators.check_perm
def config_custom(request, cc_biz_id, monitor_id, scenario='custom'):
    """
    自定义告警配置/基础性能页面
    """
    def _check_performance_monitor_exit(_cc_biz_id, _hostindex_id):
        """
        基础性能监控判断 业务下的监控指标是否已经存在
        """
        _monitor_id = 0
        try:
            host_info = HostIndex.objects.get(id=_hostindex_id)
            _result_table_id = host_info.result_table_id
            monitor_result_table_id = '%s_%s' % (_cc_biz_id, _result_table_id)
            monitor_result_table_id = trans_bkcloud_rt_bizid(monitor_result_table_id)
            monitors = Monitor.objects.filter(
                scenario='performance', biz_id=_cc_biz_id,
                monitor_field=host_info.item,
                monitor_result_table_id=monitor_result_table_id,)
            if monitors:
                _monitor_id = monitors[0].id
        except JAAPIError:
            logger.exception(u"_check_performance_monitor_exit异常")
        return _monitor_id
    # monitor 设置初始值，新增页面上有些值需要用  monitor 参数做判断
    monitor = None
    s_id = uuid.uuid4()
    dimension_field_value = count_freq = ''
    config_data = {}
    host_list = []
    try:
        monitor_id = int(monitor_id)
    except:
        monitor_id = 0

    hostindex_id = request.GET.get('hostindex_id', '')
    # 基础性能新建时，需要判断监控指标是否已经存在
    if scenario == 'performance' and not monitor_id and hostindex_id:
        monitor_id = _check_performance_monitor_exit(cc_biz_id, hostindex_id)
    if monitor_id:
        try:
            monitor = Monitor.objects.get(id=monitor_id)
        except JAItemDoseNotExists:
            logger.exception(
                u"自定义告警配置页面,告警配置(id:%s)不存在" % monitor_id
            )
        else:
            if not check_permission(monitor, cc_biz_id):
                raise PermissionDenied(u"无权限")

            # 将监控策略数据保存到 临时表 alramstrategy中
            s_id, alarm_strategys = AlarmStrategy.get_by_monitor_id(monitor)
            scenario = monitor.scenario
            dimensions = monitor.dimensions
            dimension_field_value = [d.field for d in dimensions]
            dimension_field_value = ','.join(dimension_field_value)
            # 监控周期
            count_freq = (monitor.result_table.count_freq
                          if monitor.result_table else '')
            count_freq = str(count_freq)
            config_data = monitor.get_config_data
            if scenario == 'performance':
                try:
                    result_table_id = monitor.monitor_result_table_id
                    hostindex_id = HostIndex.objects.get(
                        item=monitor.monitor_field,
                        result_table_id=result_table_id.split("_", 1)[1]).id
                except JAItemDoseNotExists:
                    logger.exception(
                        u"基础告警配置(id:%s)监控指标异常" % monitor_id
                    )
    # 监控指标
    monitor_field = monitor.monitor_field if monitor else ''
    if scenario == 'performance':
        try:
            monitor_field = hostindex_id
            host_list = AlarmStrategy.get_host_info(cc_biz_id, s_id)
        except JAItemDoseNotExists:
            logger.exception(
                u"基础性能告警配置页面,指标(id:%s)不存在" % hostindex_id
            )
    return render_mako_context(
        request, '/monitor/config/custom.html', locals()
    )


@decorators.check_perm
def get_strategy_list(request, cc_biz_id):
    """
    告警配置页面的告警策略
    """
    s_id = request.GET.get('s_id', '')
    is_scene_new = request.GET.get('is_scene_new', '')
    alrm_strategys = AlarmStrategy.objects.filter(s_id=s_id)
    strategy_list = AlarmStrategy.objects.handle_strategy_list(
        cc_biz_id, s_id, alrm_strategys
    )
    return render_mako_context(
        request, '/monitor/config/strategy_tr.part',
        {
            'strategy_list': strategy_list,
            'is_scene_new': is_scene_new,
            'cc_biz_id': cc_biz_id
        }
    )


def check_monitor_name(request, cc_biz_id):
    """
    检查app名称
    """
    def _validate_app_name(name, old_name):
        """
        校验监控名称
        @note: 只检查自定义\基础性能监控的名称
        """
        if len(name) > 20:
            return False, u"监控名称长度不能超过20个字符"

        monitors = Monitor.objects.filter(
            scenario__in='custom,performance',
            biz_id=cc_biz_id,
            is_deleted=False
        )
        if old_name:
            filter_func = lambda m: (m.monitor_name == name and
                                     m.monitor_name != old_name)
        else:
            filter_func = lambda m: m.monitor_name == name
        is_exists = bool(len(filter(filter_func, monitors)))
        if is_exists:
            return False, u"监控名称[%s]已存在" % name
        return True, u"校验通过"
    monitor_name = request.GET.get('name', '')
    old_name = request.GET.get('old_name', '')
    is_valid, message = _validate_app_name(monitor_name, old_name)
    return render_json({'result': is_valid, 'message': message})


@decorators.check_param_perm
@decorators.api
def update_monitor_config(request):
    """
    编辑监控配置
    """
    param = json.loads(request.POST['param'])
    monitor = Monitor.objects.get(id=param['monitor_id'])
    cc_biz_id = request.POST.get("biz_id")
    if not check_permission(monitor, cc_biz_id):
        raise Exception(u"无权限")
    monitor.update(
        title=param['monitor_name'],
        description=param.get('monitor_desc', monitor.monitor_desc)
    )
    return param['monitor_id']


@decorators.check_param_perm
@decorators.api
def access_custom(request):
    param = json.loads(request.POST['param'])
    s_id = param.get("s_id") or ""
    deploy_instance = ACCESS_CLASS[param["access_type"]](param)
    # check_monitor_exist = deploy_instance.check_monitor_exist()
    # if check_monitor_exist["result"]:
    #     return dict(type="update", id=check_monitor_exist["id"])
    monitor = deploy_instance.access()
    alarm_strategys = AlarmStrategy.objects.filter(s_id=s_id)
    for alarm_strategy in alarm_strategys:
        AlarmStrategy.objects.create_config_by_strategy(
            alarm_strategy, monitor
        )
    return dict(type="create", id=monitor.id)


@decorators.check_perm
def config_list(request, cc_biz_id):
    """
    配置列表页面
    """
    def generate_monitor_desc(dimension):
        try:
            if dimension.get("alarm_attr_id", ""):
                monitor = Monitor.objects.get(
                    id=int(dimension["alarm_attr_id"][0])
                )
                return monitor.monitor_name
            if dimension.get("monitor_target"):
                if dimension.get("category")[0] == "performance":
                    return HostIndex.objects.get(
                        id=dimension["monitor_target"][0]
                    ).desc
                else:
                    return BaseHostIndex.objects.get(
                        id=dimension["monitor_target"][0]
                    ).desc
        except:
            return u"监控已删除"
        return u"所有监控"

    def generate_shield_state(begin_time, end_time):
        now_timestamp = arrow.now().timestamp
        datetime_to_timestamp = lambda d: arrow.get(d).replace(
            tzinfo="local"
        ).timestamp
        begin_timestamp = datetime_to_timestamp(begin_time)
        end_timestamp = datetime_to_timestamp(end_time)
        if now_timestamp < begin_timestamp:
            return u"待屏蔽"
        if now_timestamp > end_timestamp:
            return u"已结束"
        else:
            return u"屏蔽中"

    def generate_dimension_desc(shield_obj):
        con_str_list = []
        dimension = shield_obj.dimension_config
        ip = dimension.get("ip", "")
        cc_set = dimension.get("cc_topo_set") or [""]
        cc_set = cc_set[0]
        cc_module = dimension.get("cc_app_module") or [""]
        cc_module = cc_module[0]
        cc_biz_id = dimension["cc_biz_id"][0]

        # 基础性能监控 显示 ip,set,module
        if shield_obj.alarm_type == "performance":
            if ip:
                con_str_list.append('IP: %s' % ", ".join(ip))
            else:
                if cc_set and cc_set != '0':
                    cc_set_list = cc_set.split(",")
                    cc_set_info = query_cc.CCBiz.set_name(
                        cc_biz_id, cc_set_list
                    )
                    cc_set_display = ",".join(
                        [cc_set_info[c] for c in cc_set_list]
                    )
                else:
                    cc_set_display = u"全部"
                con_str_list.append(u'集群: %s' % cc_set_display)
                if cc_module and cc_module != '0':
                    cc_module_list = cc_module.split(",")
                    cc_module_info = query_cc.CCBiz.module_name(
                        cc_biz_id, cc_module_list
                    )
                    cc_module_display = ",".join(
                        [cc_module_info[c] for c in cc_module_list]
                    )
                else:
                    cc_module_display = u"全部"
                con_str_list.append(u'模块: %s' % cc_module_display)
            return '; '.join(con_str_list) if con_str_list else u"全部"
        else:
            alarm_def_id = dimension.get("alarm_source_id", [""])[0]
            try:
                if alarm_def_id:
                    alarm_def = AlarmDef.objects.get(id=alarm_def_id)
                    return alarm_def.display_name
            except JAItemDoseNotExists:
                pass
            return u"全部策略"

    shield_list = Shield.objects.filter(
        Q(biz_id__contains=str(cc_biz_id)) |
        Q(biz_id="['00']") | Q(biz_id='["00"]')
    ).order_by("-update_time")
    shields = []
    for s in shield_list:
        if (s.dimension_config["source_type"] == "JUNGLE_ALERT" or
                s.dimension_config["source_type"] == "GSE" or
                s.dimension_config["source_type"] == "ALL"):
            shields.append(dict(
                id=s.id, begin_time=s.begin_time,
                end_time=s.end_time, desc=s.description,
                dimension_desc=generate_dimension_desc(s),
                monitor_desc=generate_monitor_desc(s.dimension_config),
                alarm_type_display=Monitor(
                    dict(scenario=s.alarm_type)
                ).get_scenario_display(),
                operator="".join(
                    get_nick_by_uin(s.create_user, True).values()
                ), operate_time=s.update_time,
                state=generate_shield_state(s.begin_time, s.end_time)))
    user_info_list = get_owner_info()
    # 其他通知人列出开发商下所有用户
    other_users = {item['username']: item['chname'] for item in user_info_list}
    tab = request.GET.get("tab") or ""
    alarm_strategy_id = safe_int(request.GET.get("alarm_strategy_id") or "0")
    monitor_id = 0
    if alarm_strategy_id > 0:
        alarm_def = AlarmDef.objects.get(id=alarm_strategy_id)
        strategy = AlarmStrategy.get_by_monitor_item(alarm_def.monitor_item)
        alarm_strategy_id = strategy.id
        monitor_id = strategy.monitor_id
    ctx = {"JOB_URL": "%s/?newTask&appId=%s" % (JOB_URL, cc_biz_id)}
    ctx.update(locals())
    return render_mako_context(
        request, '/monitor/config/config_list.html', ctx)


@decorators.check_perm
@decorators.api
def custom_monitor_option_list(request, cc_biz_id):
    monitors = Monitor.objects.filter(
        biz_id=cc_biz_id, scenario="custom", is_deleted=False
    )
    return [{"id": m.id, "text": m.monitor_name} for m in monitors]


@decorators.check_perm
def operate_monitor(request, cc_biz_id, monitor_id):
    """
    启用/停用 监控
    """
    try:
        is_enabled = request.POST.get('is_enabled', '1')
        is_enabled = int(is_enabled)
    except:
        logger.exception(u"启用/停用 监控，参数错误")
        return render_json(
            {'result': False, 'message': u"启用/停用 监控，参数错误"}
        )
    # 更新监控信息
    tip = u"启用" if is_enabled else u"停用"
    try:
        monitor = Monitor.objects.get(id=monitor_id)
        if not check_permission(monitor, cc_biz_id):
            return render_json(failed(u"无权限"))
        monitor.update(is_enabled=bool(is_enabled))
    except:
        logger.exception(u"启用/停用 监控 出错")
        return render_json(
            {'result': False, 'message': u"%s出错，参数错误" % tip}
        )

    return render_json({'result': True, 'message': u"%s成功" % tip})



@decorators.check_param_perm
@decorators.api
def access_shield(request, cc_biz_id):

    def save_shield(**kwargs):
        if not arrow.get(kwargs['scope_end_time']) <= \
                arrow.get(kwargs['scope_begin_time']).replace(days=7):
            raise Exception(u"开始结束时间不能超过七天")

        _event_raw_id = kwargs.get("event_raw_id")
        scope_biz = kwargs.get("scope_biz")
        scope_biz = map(lambda x: unicode(x), scope_biz)
        scope_set = kwargs.get("scope_set")

        scope_end_time = kwargs.get("scope_end_time")
        scope_begin_time = kwargs.get("scope_begin_time")
        event_title = kwargs.get("event_title")
        extra = kwargs.get("extra")

        source_type = extra.get("source_type", "")
        submit_by = extra.get("submit_by", "")
        _dimension = extra.get("dimension", {})

        _dimension["cc_biz_id"] = scope_biz
        cc_topo_set = _dimension.get("cc_topo_set") or []
        if cc_topo_set:
            if scope_set:
                _dimension["cc_topo_set"] = cc_topo_set + scope_set
        else:
            _dimension["cc_topo_set"] = scope_set if scope_set else []
        _dimension["source_type"] = source_type

        row = Shield.objects.filter(event_raw_id=_event_raw_id)
        if row:
            # 已存在, 更新
            try:
                _shield = row[0]
                _shield.biz_id = json.dumps(scope_biz)
                _shield.update_time = arrow.now().format('YYYY-MM-DD HH:mm:ss')
                _shield.update_user = submit_by
                _shield.begin_time = scope_begin_time
                _shield.end_time = scope_end_time
                _shield.dimension = json.dumps(_dimension)
                _shield.description = event_title
                _shield.save()
            except Exception, e:
                logger.exception(e)
                raise Exception(u"更新屏蔽失败")
        else:
            # 不存在, 写入
            try:
                Shield.objects.create(
                    event_raw_id=_event_raw_id,
                    biz_id=json.dumps(scope_biz),
                    create_time=arrow.now().format('YYYY-MM-DD HH:mm:ss'),
                    create_user=submit_by,
                    update_time=arrow.now().format('YYYY-MM-DD HH:mm:ss'),
                    update_user=submit_by,
                    begin_time=scope_begin_time,
                    end_time=scope_end_time,
                    dimension=json.dumps(_dimension),
                    description=event_title
                )
            except Exception, e:
                logger.exception(e)
                raise Exception(u"创建屏蔽失败")

    # start
    param = json.loads(request.POST['param'])
    shield_id = int(param["shield_id"])
    if shield_id == -1:
        md5 = hashlib.md5()
        md5.update("alert" + str(arrow.now().timestamp))
        event_raw_id = md5.hexdigest()
    else:
        shield = Shield.objects.get(id=shield_id)
        if not check_permission(shield, cc_biz_id):
            return HttpResponseForbidden(u"无权限")
        event_raw_id = shield.event_raw_id

    time_list = param['shield_time'].split("~")
    alert_type = param["alert_type"]
    if alert_type == "performance":
        monitor_target = int(param["monitor_target"])
        if is_base_hostindex(monitor_target):
            alert_type = "base_alarm"
            param["monitor_target"] = str(page_id_to_base_hostindex_id(monitor_target))
    # 屏蔽时间快捷选择，用于编辑屏蔽时应用页面展示。
    hours_delay = param["hours_delay"]
    dimension = {
        "hours_delay": hours_delay,
        "category": [alert_type],
    }
    # 新版本 将hours_delay 暂时存入dimension中，后台同步时，要将hours_delay去掉
    if alert_type == "custom":
        monitor_id = safe_int(param["monitor_id"])
        alarm_source_id = safe_int(param['alarm_source_id'])
        dimension["alarm_attr_id"] = [monitor_id]
        dimension["alarm_source_id"] = [alarm_source_id]
        for d in param["dimension_list"]:
            val_list = d["value"].split(",")
            dimension.setdefault(d["field"], []).extend(val_list)
    else:
        dimension["monitor_target"] = [param["monitor_target"]]
        if param["perform_cate"] == "ip":
            dimension["ip"] = param["ip"].split(",")
            # dimension["plat_id"] = param["perform"]["plat_id"]
        else:
            dimension["cc_topo_set"] = (param["cc_set"].split(",")
                                        if (param["cc_set"] or
                                            param["cc_set"] == "0")
                                        else [])
            dimension["cc_app_module"] = (param["cc_module"].split(",")
                                          if (param["cc_module"] or
                                              param["cc_module"] == "0")
                                          else [])
    extra = dict(submit_by=request.user.username, dimension=dimension)
    extra["source_type"] = "GSE" if alert_type == "base_alarm" else "JUNGLE_ALERT"

    try:
        save_shield(
            scope_begin_time=str(time_list[0]),
            scope_end_time=str(time_list[1]),
            scope_biz=[param['biz_id']], scope_set=[],
            level="12", event_type="fta_shield",
            extra=extra, event_time=str(time_list[0]),
            event_title=param["shield_desc"], event_raw_id=event_raw_id
        )
    except Exception, e:
        logger.exception(e)
        raise Exception(u"创建屏蔽失败")
    return True


@decorators.check_param_perm
@decorators.api
def remove_shield(request, cc_biz_id):
    shield_id = request.POST.get("shield_id", "")
    try:
        shield = Shield.objects.get(id=shield_id)
        if not check_permission(shield, cc_biz_id):
            return HttpResponseForbidden(u"无权限")
        shield.delete()
    except Exception, e:
        logger.exception(e)
        raise Exception(u"删除屏蔽失败")
    return True


@decorators.check_perm
def get_config_data(request, cc_biz_id):
    """
    配置列表数据
    """
    monitor_scenario = request.GET.get('monitor_scenario', '')
    # 根据不同tab取不同列表
    if monitor_scenario == "performance":
        monitors = Monitor.objects.filter(
            biz_id=cc_biz_id, scenario__in="performance,base_alarm")
    else:
        monitors = Monitor.objects.filter(
            scenario="custom", biz_id=cc_biz_id)

    monitor_id_list = [str(m.id) for m in monitors]
    alarm_strategy_list = MonitorCondition.objects.filter(
        monitor_id__in=",".join(monitor_id_list)
    ) if monitor_id_list else []
    strategy_cnt_info = dict()
    for s in alarm_strategy_list:
        # 去掉有效性校验，优化性能：这里有效性校验，
        # 每个策略都需要请求后台api，导致响应时间线性增加。
        # try:
        #     condition_config = s.condition_config
        #     notify_dict = s.alarm_def.notify_dict
        # except JAItemDoseNotExists as e:
        #     logger.error(u"获取告警策略失败：%s" % e)
        #     continue
        if s.monitor_id not in strategy_cnt_info:
            strategy_cnt_info[s.monitor_id] = [0, 0]
        if s.is_enabled:
            strategy_cnt_info[s.monitor_id][0] += 1
        else:
            strategy_cnt_info[s.monitor_id][1] += 1
    monitor_list = []
    for _m in monitors:
        dimensions = _m.dimensions
        try:
            dimensions = [d.field for d in dimensions]
            dimensions = ','.join(dimensions) if dimensions else '--'
        except:
            logger.exception(u"自定义告警配置页面,dimensionsj解析错误 ")
        monitor_desc = _m.monitor_desc if _m.monitor_desc else '--'
        monitor_desc_show = monitor_desc[
            :10] + '...' if len(monitor_desc) > 10 else monitor_desc
        monitor_field_display = "%s(%s)" % (
            _m.count_method, _m.monitor_field
        ) if _m.count_method else _m.monitor_field
        monitor_list.append({
            'id': _m.id,
            'monitor_name': _m.monitor_name,
            'scenario': _m.get_scenario_display(),
            'monitor_type': _m.get_monitor_type_display(),
            'monitor_result_table_id': _m.monitor_source["text"],
            'monitor_field': monitor_field_display,
            'dimensions': dimensions,
            'is_allow_delete': True,
            'is_enabled': _m.is_enabled,
            'is_enabled_str': u"<span class='text-success'>已启用</span>"
            if _m.is_enabled else u"<span class='text-danger'>未启用</span>",
            'create_time': _m.create_time,
            'create_user': _m.create_user,
            'update_user': _m.update_user,
            'update_time': _m.update_time,
            'monitor_desc': monitor_desc,
            'monitor_desc_show': monitor_desc_show,
            'result_table': _m.monitor_result_table_id,
            'monitor_item': _m.monitor_field,
            'monitor_target': _m.monitor_target,
            'enable_strategy_cnt': strategy_cnt_info.get(_m.id, [0, 0])[0],
            'disable_strategy_cnt': strategy_cnt_info.get(_m.id, [0, 0])[1],
        })
    # 基础性能告警列出所有项
    if monitor_scenario == "performance":
        existed_hostindex = ["%s_%s" % (
            m["monitor_result_table_id"], m["monitor_item"]
        ) for m in monitor_list]
        hostindex = list(HostIndex.objects.filter(
            graph_show=True, is_deleted=False
        ))
        base_hostindex = BaseHostIndex.objects.filter(is_enable=True)
        hostindex += base_hostindex
        for h in hostindex:
            if trans_bkcloud_rt_bizid("_".join([cc_biz_id, h.result_table_id, h.item])) in existed_hostindex:
                continue
            else:
                monitor_list.append({
                    'id': 0,
                    'monitor_name': h.desc,
                    'scenario': u"主机性能",
                    'monitor_type': Monitor(
                        dict(monitor_type=h.category)
                    ).get_monitor_type_display(),
                    'monitor_result_table_id': "%s_%s" % (
                        cc_biz_id, h.result_table_id
                    ),
                    'monitor_field': "",
                    'monitor_target': h.id,
                    'dimensions': "",
                    'is_allow_delete': False,
                    'is_enabled': True,
                    'is_enabled_str': u"<span class='text-success'>"
                                      u"已启用</span>",
                    'create_time': "",
                    'create_user': "",
                    'update_user': "",
                    'update_time': "",
                    'monitor_desc': "",
                    'monitor_desc_show': "",
                    'result_table': "",
                    'enable_strategy_cnt': 0,
                    'disable_strategy_cnt': 0,
                })

    return HttpResponse(json.dumps(monitor_list))


@decorators.check_perm
def get_rel_strategy_list(request, cc_biz_id):
    """
    配置列表页面获取告警策略
    @note: 先从原始表转换到缓存表中
    """
    monitor_id = request.GET.get('monitor_id', '')
    monitor_id = safe_int(monitor_id, 0)
    if not monitor_id:
        return HttpResponse(json.dumps([]))
    monitor = Monitor.objects.get(pk=monitor_id)
    if not check_permission(monitor, cc_biz_id):
        return render_json(failed(u"无权限"))
    # 将原始数据转换到 缓存表中
    if monitor_id == 0:
        s_id = AlarmStrategy.create_s_id()
        alarm_strategys = []
    else:
        s_id, alarm_strategys = AlarmStrategy.get_by_monitor_id(monitor)
    strategy_list = AlarmStrategy.objects.handle_strategy_list(
        cc_biz_id, s_id, alarm_strategys
    )
    return HttpResponse(json.dumps(strategy_list))



@decorators.check_perm
@decorators.api
def delete_monitor_config(request, cc_biz_id):
    """
    删除监控配置
    """
    logger.info("monitor_id: %s" % json.dumps(request.POST))
    monitor_id = request.POST['monitor_id']
    try:
        monitor = Monitor.objects.get(id=monitor_id)
        if not check_permission(monitor, cc_biz_id):
            return render_json(failed(u"无权限"))
        monitor.delete()
    except Exception, e:
        logger.exception(e)
        raise Exception(u"删除配置失败")

    return monitor_id

# -*- coding: utf-8 -*-
"""
@desc:
"""
import datetime
import HTMLParser
import json
import time
import unicodedata

import arrow
from django.conf import settings
from django.http.response import HttpResponse, HttpResponseForbidden

from common.log import logger
from common.mymako import render_json, render_mako_context
from monitor.constants import VALUE_METHOD_DESC, JOB_URL
from monitor.errors import (EmptyQueryException, JAItemDoseNotExists,
                            SqlQueryException, TableNotExistException)
from monitor.models import AlarmDef, MonitorLocation, ScenarioMenu
from monitor.performance.models import AlarmInstance, Monitor
from utils import decorators
from utils.common_utils import (check_permission, failed, failed_data,
                                filter_alarms, get_group_of_alarm, ok, ok_data)
from utils.dataview_tools import (DataProcessor, get_date_range,
                                  get_field_results, get_field_values_options,
                                  get_time_range, get_time_range_by_datestr)
from utils.query_cc import CCBiz, get_owner_info


@decorators.check_perm
def get_cc_set(request, cc_biz_id):
    '''
    @summary: 根据业务id 查询其在游戏云上的拓扑结构,获取大区信息（{大区id，大区名称}）
    '''
    set_list = []
    try:
        sets, total_count = CCBiz.sets(cc_biz_id)
        set_list = [{'id': _set['SetID'], 'text': _set['SetName']}
                    for _set in sets]
        set_list.insert(0, {'id': '0', 'text': u'全部 [%s]' % total_count})
    except Exception, e:
        logger.exception(u"获取大区信息失败，错误详情：%s" % e)
        set_list.insert(0, {'id': '-1', 'text': u'加载大区列表失败'})
        return render_json(
            {'result': False, 'data': set_list, 'message': u'获取大区信息失败.'}
        )
    return render_json({'result': True, 'data': set_list})


@decorators.check_perm
def get_cc_module(request, cc_biz_id):
    '''
    获取大区下面的模块
    :param request:
    :return:
    '''
    mod_list = []
    try:
        set_id = request.GET.get("set_id", None)
        mods, total_count = CCBiz.modules(cc_biz_id, set_id)
        mod_list = [{'id': mod['ModuleID'], 'text': mod['ModuleName']}
                    for mod in mods if mod]
        mod_list.insert(0, {'id': '0', 'text': u'全部 [%s]' % total_count})
    except Exception as e:
        logger.exception(u"获取模块列表失败，错误详情：%s" % e)
        mod_list.insert(0, {'id': '-1', 'text': u'加载模块列表失败'})
    finally:
        return render_json({'result': True, 'data': mod_list})


@decorators.check_perm
def operation_monitor(request, cc_biz_id):
    """运营数据监控视图"""
    # 用戶信息
    # 目前只有運維一種角色
    maintainers = CCBiz.maintainers(cc_biz_id)
    user_info_list = get_owner_info()
    other_users = {item['username']: item['chname'] for item in user_info_list}
    from_overview = bool(request.GET.get("from_overview"))
    alarm_strategy_id = request.GET.get("alarm_strategy_id", "0")
    monitor_id = -1
    if alarm_strategy_id != "0":
        try:
            alarm_def = AlarmDef.objects.get(id=alarm_strategy_id)
            monitor_id = alarm_def.alarm_attr_id
            if alarm_def.scenario == "custom":
                alarm_strategy_id = alarm_def.id
            else:
                alarm_strategy_id = -1
        except AlarmDef.DoesNotExist:
            alarm_strategy_id = -1
    ctx = {
        'JOB_URL': "%s/?newTask&appId=%s" % (JOB_URL, cc_biz_id),
    }
    ctx.update(locals())
    return render_mako_context(
        request, '/monitor/dataview/operation/home.html', ctx
    )


@decorators.check_perm
def operation_menu_list(request, cc_biz_id):
    # 获取左侧菜单栏列表
    menus = ScenarioMenu.objects.filter(
        biz_id=cc_biz_id, is_deleted=False
    ).exclude(system_menu=u"favorite")
    if not menus:
        # create default menus
        menus = ScenarioMenu.objects.init_biz_scenario_menu(cc_biz_id)
    return render_mako_context(
        request, '/monitor/dataview/operation/left_menus.html', locals()
    )


@decorators.check_perm
def operation_menu_add(request, cc_biz_id):
    # 新增菜单
    menu_name = request.POST.get("menu_name", "")
    h = HTMLParser.HTMLParser()
    menu_name = unicodedata.normalize("NFKD", h.unescape(menu_name).strip())
    return render_json(
        ScenarioMenu.objects.add_scenario_menu(cc_biz_id, menu_name)
    )


@decorators.check_perm
def operation_menu_edit(request, cc_biz_id):
    # 编辑菜单
    menu_name = request.POST.get("menu_name", "")
    menu_id = request.POST.get("menu_id", "")
    h = HTMLParser.HTMLParser()
    menu_name = unicodedata.normalize("NFKD", h.unescape(menu_name).strip())
    return render_json(
        ScenarioMenu.objects.edit_scenario_menu(menu_id, menu_name, cc_biz_id)
    )


@decorators.check_perm
def operation_menu_del(request, cc_biz_id):
    # 删除菜单
    menu_id = request.POST.get("menu_id", "")
    return render_json(
        ScenarioMenu.objects.del_scenario_menu(menu_id, cc_biz_id)
    )


@decorators.check_perm
def operation_graph_panel(request, cc_biz_id):
    # 渲染右侧图表面板
    menu_id = request.GET.get("menu_id")
    try:
        if not menu_id:
            # 拿收藏
            menu = ScenarioMenu.objects.get(
                biz_id=cc_biz_id, system_menu="favorite"
            )
        else:
            menu = ScenarioMenu.objects.get(pk=menu_id)
    except:
        return HttpResponse(u"无效的请求")
    if not check_permission(menu, cc_biz_id):
        return HttpResponseForbidden(u"无权限")
    # 获取对应的监控视图
    locations = MonitorLocation.objects.filter(
        menu_id=menu.id, biz_id=cc_biz_id).order_by("graph_index"
    )
    invalid_location_ids = list()
    for l in locations:
        # if not l.monitor or l.monitor.is_deleted or not l.monitor.is_enabled:
        if not l.monitor or l.monitor.is_deleted:
            invalid_location_ids.append(l.pk)
            l.is_deleted = True
            l.save()
    locations = locations.exclude(pk__in=invalid_location_ids)
    menu_id = menu.id
    value_method_desc = VALUE_METHOD_DESC
    return render_mako_context(
        request, '/monitor/dataview/operation/right_panel.html', locals()
    )



@decorators.check_perm
def get_filter_field_results_by_monitor(request, cc_biz_id):
    """
    获取菜单上，过滤参数的所有取值范围,
    """
    args = request.POST
    monitor_id = args.get("monitor_id")
    field = args.get("field")
    time_range = args.get("time_range")
    m = Monitor.objects.get(pk=monitor_id)
    if not check_permission(m, cc_biz_id):
        return render_json(failed(u"无权限"))
    result_table_id = m.monitor_result_table_id
    # 过滤条件
    ext_filter = args.get("ext_filter") or "{}"
    ext_filter_dict = {k: v for k, v in (json.loads(ext_filter) or {}).items() if v}
    data = get_field_values_options(
        result_table_id, field,
        ext_filter=ext_filter_dict,
        time_range=time_range
    )
    return render_json(ok_data(data))


@decorators.check_perm
def get_operation_monitor_point(request, cc_biz_id):
    start = time.time()
    kwargs = {}
    config_key_words = ["monitor_id", "value_method"]
    monitor_id = request.GET.get("monitor_id", "")
    try:
        m = Monitor.objects.get(pk=monitor_id)
    except JAItemDoseNotExists:
        return render_json(failed(u"监控不存在"))
    if m.is_deleted:
        return render_json(failed(u"监控不存在"))
    if not check_permission(m, cc_biz_id):
        return render_json(failed(u"无权限查看"))
    rt_id = m.monitor_result_table_id
    value_method = request.GET.get("value_method", "sum")
    value_field = "%s(%s)" % (value_method.lower(), m.monitor_field)
    if value_method == "count":
        value_field = "count(*)"
    h = HTMLParser.HTMLParser()
    for k, v in request.GET.items():
        if k not in config_key_words:
            v = unicodedata.normalize("NFKD", h.unescape(v).strip())
            # v = v.replace('&nbsp;', " ")
            if v:
                kwargs[k] = v
    if "time_range" not in kwargs:
        kwargs["time_range"] = get_time_range(datetime.datetime.now())
    try:
        data = DataProcessor.operation_monitor_data(
            rt_id, value_field, kwargs, monitor_id=m.id
        )
        data = {'data': data, 'echo_sql': data['echo_sql']}
        # del data["data"]["echo_sql"]
        spend_time = str(round(time.time() - start, 2))
        data["spend_time"] = spend_time
        data["update_time"] = datetime.datetime.now()
        return render_json(ok_data(data))
    except SqlQueryException, e:
        logger.exception(u"查询失败，原因: %s" % e)
        return render_json(failed_data(
            u"数据查询异常，请联系管理员！",
            {'echo_sql': "", 'error_class': 'info'}
        ))
    except TableNotExistException, e:
        logger.exception(e)
        # echo_sql = cache.get(cache_key, u"未能成功生成查询sql")
        # 判断是否是新接入的图表 5分钟
        if ((datetime.datetime.now() - arrow.get(m.create_time).naive) <
                datetime.timedelta(seconds=60*10)):
            try:
                interval = m.result_table.count_freq / 60
            except:
                interval = 5
            e = (u"请稍等，数据正在接入中…（请%s分钟后刷新图表）" %
                 (interval + 1))
        else:
            e = u"数据查询异常，请联系管理员！（数据表不存在）"
        echo_sql = ""
        return render_json(failed_data(u"%s" % e, {
            'echo_sql': echo_sql,
            'error_class': "info",
            'need_access': "need_access"
        }))
    except Exception, e:
        logger.exception(u"后台异常: %s" % e)
        # echo_sql = cache.get(cache_key, u"未能成功生成查询sql")
        return render_json(failed_data(
            u"生成图表异常", {'echo_sql': "", 'error_class': 'info'}
        ))


@decorators.check_perm
def get_operation_monitor_alert_list(request, cc_biz_id):
    # 获取告警列表
    args = request.GET
    time_range = args.get("time_range")
    time_range = time_range.replace('&nbsp;', " ")
    start_time, end_time = get_date_range(time_range)
    monitor_id = args.get("monitor_id")
    try:
        monitor = Monitor.objects.get(pk=monitor_id)
    except JAItemDoseNotExists:
        return render_json(failed(u"监控不存在"))
    if monitor.is_deleted:
        return render_json(failed(u"监控不存在"))
    if not check_permission(monitor, cc_biz_id):
        return render_json(failed(u"无权限"))
    alerts = AlarmInstance.get_alarm_by_monitor_id(
        start_time, end_time, monitor_id
    )
    filter_dict = dict()
    for k, v in request.GET.items():
        if k not in ["time_range", "monitor_id", "value_method"]:
            filter_dict[k] = v
    if filter_dict.keys():
        alerts = filter_alarms(alerts, filter_dict)
    alert_group_dict = {}
    # 聚合
    for alert in alerts:
        hit = True
        for k, v in filter_dict.items():
            if k in alert.dimensions:
                if v and v != str(alert.dimensions[k]):
                    hit = False
            else:
                if v:
                    hit = False
        if not hit:
            continue
        alert_time_point = datetime.datetime.strptime(
            alert.source_time.strftime(
                '%Y-%m-%d %H:%M:00'
            ), '%Y-%m-%d %H:%M:%S'
        )
        alert.source_time = alert_time_point
        if alert_time_point not in alert_group_dict:
            setattr(alert, "alert_count", 1)
            setattr(alert, "alert_count_info", {1: 0, 2: 0, 3: 0})
            setattr(alert, "alert_ids", [alert.id])
            alert.alert_count_info[alert.level] += 1
            alert_group_dict[alert_time_point] = alert

        else:
            old_alert = alert_group_dict[alert_time_point]
            new_alert = alert if old_alert.level > alert.level else old_alert
            setattr(new_alert, "alert_count", old_alert.alert_count)
            setattr(new_alert, "alert_ids", old_alert.alert_ids)
            setattr(new_alert, "alert_count_info", old_alert.alert_count_info)
            new_alert.alert_count += 1
            new_alert.alert_ids.append(alert.id)
            new_alert.alert_count_info[alert.level] += 1
            alert_group_dict[alert_time_point] = new_alert
        # 影响范围
    data = get_group_of_alarm(alert_group_dict.values())
    data["interval"] = monitor.result_table.count_freq * 1000
    return render_json(ok_data(data))



@decorators.check_perm
def favorite_toggle(request, cc_biz_id):
    # 收藏 or 取消收藏
    args = request.POST
    monitor_id = args.get("monitor_id")
    try:
        monitor = Monitor.objects.get(pk=monitor_id)
    except JAItemDoseNotExists:
        return render_json(failed(u"监控不存在"))
    if monitor.is_deleted:
        return render_json(failed(u"监控不存在"))
    if not check_permission(monitor, cc_biz_id):
        return render_json(failed(u"无权限"))
    try:
        sm = ScenarioMenu.objects.get(
            is_deleted=False, system_menu=u"favorite", biz_id=cc_biz_id
        )
    except:
        return render_json(failed(u"收藏夹未创建"))
    m = MonitorLocation.objects.filter(
        is_deleted=False,
        monitor_id=monitor_id,
        menu_id=sm.id,
        biz_id=cc_biz_id
    )
    if m.exists():
        m.update(is_deleted=True)
        return render_json(ok_data({'status': False}))
    else:
        MonitorLocation(
            biz_id=cc_biz_id, monitor_id=monitor_id, menu_id=sm.id
        ).save()
        return render_json(ok_data({'status': True}))



@decorators.check_perm
def delete_monitor_location(request, cc_biz_id):
    # 删除监控视图
    args = request.POST
    location_id = args.get("location_id")
    del_monitor = args.get("del_monitor")
    location = MonitorLocation.objects.get(pk=location_id)
    if not check_permission(location, cc_biz_id):
        return render_json(failed(u"无权限查看"))
    location.is_deleted = True
    location.save()
    if del_monitor:
        MonitorLocation.objects.filter(
            biz_id=cc_biz_id, is_deleted=False, monitor_id=location.monitor_id
        ).update(is_deleted=True)
        # close monitor
        Monitor.objects.get(pk=location.monitor_id).delete()
    return render_json(ok())



@decorators.check_perm
def add_monitor_loaction(request, cc_biz_id):
    if request.method == "GET":
        # 新增视图modal弹框
        redirect_url = ""
        menu_id = request.GET.get("menu_id")
        is_overview = request.GET.get("overview")
        # 列出在此菜单下的所有视图
        menu_locations = MonitorLocation.objects.filter(
            menu_id=menu_id, is_deleted=False, biz_id=cc_biz_id
        )
        exists_monitor_ids = set([l.monitor_id for l in menu_locations])
        monitors = Monitor.objects.filter(
            is_deleted=False, biz_id=cc_biz_id, scenario="custom"
        )
        monitors_ids = set([m.id for m in monitors if
                            m.id not in exists_monitor_ids])
        group_monitors = []
        # 按分组列出监控视图
        menus = ScenarioMenu.objects.filter(biz_id=cc_biz_id, is_deleted=False)
        for menu in menus:
            if menu.system_menu != u"favorite":
                # logger.info("menu_id: %s, biz_id: %s" % (menu.id, cc_biz_id))
                this_menu_locations = MonitorLocation.objects.filter(
                    menu_id=menu.id, biz_id=cc_biz_id
                )
                this_monitors = []
                for l in this_menu_locations:
                    if (l.monitor and
                            not l.monitor.is_deleted and
                            l.monitor.id not in exists_monitor_ids):
                        this_monitors.append(l.monitor)
                        if l.monitor.id in monitors_ids:
                            monitors_ids.remove(l.monitor.id)
                group_monitors.append([menu.name, this_monitors])
        none_menu_monitors = Monitor.objects.filter(
            id__in=",".join(map(str, monitors_ids))
        ) if monitors_ids else []
        group_monitors.append([u"未分组", none_menu_monitors])
        return render_mako_context(
            request,
            '/monitor/dataview/operation/modal_add_location.html.part',
            locals()
        )
    else:
        # 新增视图
        menu_id = request.POST.get("menu_id")
        monitor_id = request.POST.get("monitor_id")
        try:
            monitor = Monitor.objects.get(pk=monitor_id)
        except JAItemDoseNotExists:
            return render_json(failed(u"监控不存在"))
        if monitor.is_deleted:
            return render_json(failed(u"监控不存在"))
        if not check_permission(monitor, cc_biz_id):
            return render_json(failed(u"无权限"))
        if MonitorLocation.objects.filter(
                biz_id=cc_biz_id, menu_id=menu_id, monitor_id=monitor_id
        ).exists():
            return render_json(failed(u"监控已经在分组中了"))
        new_location = MonitorLocation(
            biz_id=cc_biz_id, menu_id=menu_id, monitor_id=monitor_id
        )
        new_location.save()
        value_method_desc = VALUE_METHOD_DESC
        html = render_mako_context(
            request,
            '/monitor/dataview/operation/one_panel.html.part',
            locals()
        ).content
        return render_json(ok_data({"html": html}))


@decorators.check_perm
def monitor_info(request, cc_biz_id):
    monitor_id = request.GET.get("monitor_id")
    if monitor_id:
        monitor = Monitor.objects.filter(pk=monitor_id)
        if monitor:
            if monitor[0].is_deleted:
                return render_json(failed(u"监控不存在"))
            if not check_permission(monitor[0], cc_biz_id):
                return render_json(failed(u"无权限"))
            monitor_info_dict = dict()
            for k in monitor[0].__dict__.keys():
                if not k.startswith("_"):
                    monitor_info_dict[k] = getattr(monitor[0], k, "")
            return render_json(ok_data(monitor_info_dict))
    return render_json(failed_data(u"监控不存在", {}))



@decorators.check_perm
def graph_detail(request, cc_biz_id):
    # 展示图表详情弹层
    monitor_id = request.GET.get("monitor_id", "")
    if not monitor_id:
        return HttpResponse(u"无效请求")
    try:
        m = Monitor.objects.get(pk=monitor_id)
    except JAItemDoseNotExists:
        return render_json(failed(u"监控不存在"))
    if m.is_deleted:
        return render_json(failed(u"监控不存在"))
    if not check_permission(m, cc_biz_id):
        return render_json(failed(u"无权限"))
    fields = m.dimensions
    rt_id = m.monitor_result_table_id
    value_method = request.GET.get("value_method", m.count_method)
    field_id_list = [f.field for f in fields]
    field_values = get_field_results(rt_id, ",".join(field_id_list))
    if field_values and len(field_id_list) == 1:
        field_values = [[i] for i in field_values]
    return render_mako_context(
        request, "/monitor/dataview/operation/graph_detail.html", locals()
    )


@decorators.check_perm
def get_all_field_values(request, cc_biz_id):
    # 获取所有维度对应的值
    monitor_id = request.GET.get("monitor_id", "")
    if not monitor_id:
        return HttpResponse(u"无效请求")
    try:
        m = Monitor.objects.get(pk=monitor_id)
    except JAItemDoseNotExists:
        return render_json(failed(u"监控不存在"))
    if m.is_deleted:
        return render_json(failed(u"监控不存在"))
    if not check_permission(m, cc_biz_id):
        return render_json(failed(u"无权限"))
    fields = m.dimensions
    rt_id = m.monitor_result_table_id
    field_id_list = [f.field for f in fields]
    date_str = request.GET.get("date_str")
    field_values = get_field_results(
        rt_id,
        ",".join(field_id_list),
        time_range=get_time_range_by_datestr(date_str)
    )
    if field_values and len(field_id_list) == 1:
        field_values = [[i] for i in field_values]
    return render_json(ok_data(field_values))



@decorators.check_perm
def graph_detail_point(request, cc_biz_id):
    start = time.time()
    args = request.POST
    monitor_id = args.get("monitor_id", "")
    try:
        m = Monitor.objects.get(pk=monitor_id)
    except JAItemDoseNotExists:
        return render_json(failed(u"监控不存在"))
    if m.is_deleted:
        return render_json(failed(u"监控不存在"))
    if not check_permission(m, cc_biz_id):
        return render_json(failed(u"无权限"))
    rt_id = m.monitor_result_table_id
    value_method = args.get("value_method", m.count_method)
    value_field = "%s(%s)" % (value_method.lower(), m.monitor_field)
    if value_method == "count":
        value_field = "count(*)"
    group_field = ",".join([d.field for d in m.dimensions])
    datestr = args.get("date_str")
    filter_str = args.get("filter_str")
    h = HTMLParser.HTMLParser()
    filter_str = unicodedata.normalize("NFKD", h.unescape(filter_str).strip())
    kwargs = {}
    if not datestr:
        kwargs["time_range"] = get_time_range(datetime.datetime.now())
    else:
        kwargs["time_range"] = get_time_range_by_datestr(datestr)
    try:
        data = DataProcessor.make_multiple_graph_point(
            rt_id,
            value_field,
            group_field,
            params=kwargs,
            filter_str=filter_str,
            monitor_id=m.id
        )
        data = {'data': data, 'echo_sql': data['echo_sql']}
        del data["data"]["echo_sql"]
        spend_time = str(round(time.time() - start, 2))
        data["spend_time"] = spend_time
        data["update_time"] = datetime.datetime.now()
        return render_json(ok_data(data))
    except SqlQueryException, e:
        logger.exception(u"查询失败，原因: %s" % e)
        return render_json(failed_data(
            u"数据查询异常，请联系管理员！",
            {'echo_sql': "", 'error_class': 'info'})
        )
    except TableNotExistException, e:
        logger.exception(e)
        # 判断是否是新接入的图表 5分钟
        if ((datetime.datetime.now() - arrow.get(m.create_time).naive) <
                datetime.timedelta(seconds=60*10)):
            try:
                interval = m.result_table.count_freq / 60
            except:
                interval = 5
            e = (u"请稍等，数据正在接入中…（请%s分钟后刷新图表）" %
                 (interval + 1))
        else:
            e = u"数据查询异常，请联系管理员！（数据表不存在）"
        echo_sql = ""
        return render_json(failed_data(u"%s" % e, {
            'echo_sql': echo_sql,
            'error_class': "info",
            'need_access': "need_access"
        }))
    except EmptyQueryException, e:
        return render_json(failed_data(
            u"查询无数据", {'echo_sql': "", 'error_class': 'info'}
        ))
    except Exception, e:
        logger.exception(u"后台异常: %s" % e)
        return render_json(failed_data(
            u"生成图表异常", {'echo_sql': "", 'error_class': 'info'}
        ))

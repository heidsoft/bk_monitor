# -*- coding: utf-8 -*-
import datetime
import json

from django.views.decorators.http import require_POST

from common.log import logger
from common.mymako import render_json, render_mako_context
from monitor.api.data import access_performance, get_bp_data_id
from monitor.constants import AGENT_STATUS, DISPLAY_STANDARD_PROPERTY_LIST, \
    AGENT_SETUP_URL
from monitor.errors import (EmptyQueryException, SqlQueryException,
                            TableNotExistException)
from monitor.models import AlarmStrategy, MonitorHostSticky
from monitor.performance.models import AlarmInstance, Host, HostIndex, BaseHostIndex
from monitor.performance.solutions import SolutionConf
from utils.common_utils import (failed, failed_data, host_key, href_link,
                                ignored, ok, ok_data, parse_host_id)
from utils.dataview_tools import DataProcessor, get_field_results
from utils.decorators import check_perm
from utils.query_cc import CCBiz, get_plat
from utils.time_status import TimeStats


@check_perm
def get_cc_set(request, cc_biz_id):
    """
    根据业务id 查询其在游戏云上的拓扑结构,获取大区信息（{大区id，大区名称}）
    """
    set_list = []
    try:
        sets, total_count = CCBiz.sets(cc_biz_id)
        set_list = [{'id': _set['SetID'], 'text': _set['SetName']}
                    for _set in sets]
        set_list.insert(0, {'id': '0', 'text': u'全部 [%s]' % total_count})
    except Exception as e:
        logger.exception(u"获取集群信息失败，错误详情：%s" % e)
        set_list.insert(0, {'id': '-1', 'text': u'加载集群列表失败'})
        return render_json(
            {'result': False, 'data': set_list, 'message': u'获取集群信息失败.'}
        )
    return render_json({'result': True, 'data': set_list})


@check_perm
def get_cc_module(request, cc_biz_id):
    """
    获取大区下面的模块
    """
    mod_list = []
    try:
        set_id = request.GET.get("set_id", None)
        mods, total_count = CCBiz.modules(cc_biz_id, set_id)
        mod_list = [{'id': mod['ModuleID'], 'text': mod['ModuleName']}
                    for mod in mods if mod]
        if set_id in [None, "", "0"]:
            mod_list = [{'id': '0', 'text': u'全部 [%s]' % total_count}]
        else:
            mod_list.insert(0, {'id': '0', 'text': u'全部 [%s]' % total_count})
    except Exception as e:
        logger.exception(u"获取模块列表失败，错误详情：%s" % e)
        mod_list.insert(0, {'id': '-1', 'text': u'加载模块列表失败'})
    finally:
        return render_json({'result': True, 'data': mod_list})


@check_perm
def get_host_property_list(request, cc_biz_id):
    """
    获取业务主机属性
    """
    property_list = [{'id': '0', 'text': u'全部'}]
    property_tag = (
        ("standard", u"标准属性"),
        ("customer", u"自定义属性"),
    )
    try:
        result = CCBiz.host_property_list(cc_biz_id)
        for tag, tag_name in property_tag:
            property_info = result.get(tag)
            if property_info:
                children = list()
                for _id, desc in property_info.iteritems():
                    if desc == "Cpu":
                        desc = desc.upper()
                    children.append({'id': _id, 'text': desc})
                if tag == "standard":
                    children = filter(
                        lambda c: c['id'] in DISPLAY_STANDARD_PROPERTY_LIST,
                        children
                    )
                    children.sort(
                        key=lambda x:
                        DISPLAY_STANDARD_PROPERTY_LIST.index(x['id'])
                    )
                property_list.append({
                    "text": tag_name,
                    "children": children
                })
    except Exception as e:
        logger.exception(u"获取主机属性列表失败，错误详情：%s" % e)
    finally:
        return render_json({'result': True, 'data': property_list})


@check_perm
def get_plat_list(request, cc_biz_id):
    """
    获取云平台信息列表
    """
    return render_json(ok_data(get_plat(cc_biz_id)))


@check_perm
def get_agent_status(request, cc_biz_id):
    """
    获取主机agent状态,
    """
    host_id = request.GET.get("host_id")
    if not host_id:
        return render_json(failed(u"无效请求"))
    agent_status = Host.get_agent_status_by_hostid(
        cc_biz_id, host_id).get(host_id)
    return render_json(ok_data({'status': agent_status}))


@check_perm
def index(request, cc_biz_id):
    """
    request.method:
    get:    基础性能页面首页
    post:   主机性能信息，包括主机属性，主机各指标信息。
    """
    def get_access_status(cc_biz_id):
        """
        获取数据平台基础性能接入进展
        :return: {
            "accessed": True,
            "div_message": u"正在接入中",
            "btn_message": u"确定"
        }
        """
        btn_message = u"确定"
        div_message = u"您的性能指标采集任务已下发正在进行中，请稍候再试！"
        # step 1 获取该业务下基础性能接入的data_id
        data_id_exist = any(get_bp_data_id(cc_biz_id))
        # step 2 如果data_id 不存在，则直接返回未接入
        if not data_id_exist:
            div_message = (u"检测到您的业务尚未开启监控，"
                           u"点击下面按钮开启主机指标采集，\n"
                           u"10-20分钟后刷新此页面即可查看到主机数据，请耐心等待！\n"
                           u"（未安装agent的主机，"
                           u"在主机详情页中按照指引完成部署并开启数据采集。）")
            btn_message = u"开始采集"
        return {
            "accessed": data_id_exist,
            "div_message": div_message,
            "btn_message": btn_message
        }
    data = {
        "hosts": [],
        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if request.method == "GET":
        count_per_page = 10
        # 获取云区域信息
        plat_info = CCBiz.plat_info(cc_biz_id)
        checkhost_id = request.GET.get("alarm_strategy_id")
        return render_mako_context(
            request, '/monitor/performanceV2/home.html', locals()
        )
    ts = TimeStats(u"get_host_info_list: %s" % cc_biz_id)
    # 获取所有主机信息（前台分页）
    ts.split(u"获取主机列表")
    hosts = CCBiz.hosts(cc_biz_id).get("data") or []
    host_ids = set([host_key(h) for h in hosts])
    ts.split(u"获取主机agent状态")
    hosts_agent_status = CCBiz.agent_status(cc_biz_id, host_ids)
    default_status_info = {
        'alarm': {
            'level': [0, 0, 0],
        },
        'component': [],
    }
    try:
        # 主机性能数据结果表字典，当性能获取需要查询之前查过的结果表的时候，
        # 直接使用已有的client，节省查询时间。
        # cpu 总使用率
        ts.split(u"获取主机cpu 总使用率")
        cpu_usage_info = HostIndex.get_host_performance(
            cc_biz_id, item="cpuusage", category="cpu",
            result_table_id="ja_gse_cpu_cpuusage"
        )
        # CPU 5分钟负载
        ts.split(u"获取主机cpu 5分钟负载")
        cpu_load_info = HostIndex.get_host_performance(
            cc_biz_id, item="locdavg", category="cpu",
            result_table_id="ja_gse_cpu"
        )
        # cpu 单核使用率
        ts.split(u"获取主机cpu 单核使用率")
        cpu_single_usage_info = HostIndex.get_host_performance(
            cc_biz_id, item="cpuusage", category="cpu",
            result_table_id="ja_gse_cpu_core_cpuusage"
        )
        # 磁盘使用量 (暂时隐藏)
        # disk_used_info = get_host_performance(cc_biz_id, item="used_percent",
        # category="disk", result_table_id="ja_gse_disk_used")
        # IO等待
        ts.split(u"获取主机IO等待")
        io_util_info = HostIndex.get_host_performance(
            cc_biz_id, item="util", category="disk",
            result_table_id="ja_gse_disk_iostats"
        )
        host_list = list()
        ts.split(u"处理整合所有数据")
        for h in hosts:
            host = Host(h)
            for k, v in default_status_info.iteritems():
                setattr(host, k, v)
            host.is_stickied = MonitorHostSticky.objects.host_is_stickied(
                host.id
            )
            # 基础性能数据
            host.cpu_usage = cpu_usage_info.get(host.id)
            host.cpu_single_usage = cpu_single_usage_info.get(host.id)
            host.cpu_load = cpu_load_info.get(host.id)
            host.io_util = io_util_info.get(host.id)
            if host.io_util and isinstance(host.io_util.get("val"), list):
                io_util = dict()
                for _io_util in host.io_util["val"]:
                    for k, v in _io_util.iteritems():
                        io_util[k] = v
                host.io_util["val"] = max(io_util.values())
            host.status = hosts_agent_status.get(host.id, AGENT_STATUS.UNKNOWN)
            index_list = [host.cpu_usage, host.cpu_single_usage, host.cpu_load, host.io_util]
            if host.status == AGENT_STATUS.ON and not any(index_list):
                host.status = AGENT_STATUS.NO_DATA
            # 控制前端页面展示的参数
            # 是否被选中
            host.checked = False
            # 是否显示（按属性分组时）
            host._is_show = True
            host_list.append(host)
        host_list.sort(key=lambda x: x.status, reverse=True)
        data["hosts"] = host_list
        return render_json(ok_data(data))
    except (TableNotExistException, SqlQueryException) as e:
        # 前端引导用户接入
        if not hosts:
            data["need_access"] = False
            data["access_div_message"] = (
                u"检测到当前业务没有主机，请前往 %s 快速部署主机！" %
                href_link(u"Agent安装", AGENT_SETUP_URL)
            )
            data["access_btn_message"] = u"确定"
        else:
            host_list = list()
            for h in hosts:
                host = Host(h)
                for k, v in default_status_info.iteritems():
                    setattr(host, k, v)
                host.is_stickied = MonitorHostSticky.objects.host_is_stickied(
                    host.id
                )
                # 基础性能数据
                host.cpu_usage = None
                host.cpu_single_usage = None
                host.cpu_load = None
                host.io_util = None
                host.status = hosts_agent_status.get(host.id, AGENT_STATUS.UNKNOWN)
                if host.status == AGENT_STATUS.ON:
                    host.status = AGENT_STATUS.NO_DATA
                # 控制前端页面展示的参数
                # 是否被选中
                host.checked = False
                # 是否显示（按属性分组时）
                host._is_show = True
                host_list.append(host)
            host_list.sort(key=lambda x: x.status, reverse=True)
            data["hosts"] = host_list
            access_status = get_access_status(cc_biz_id)
            data["need_access"] = not access_status.get("accessed")
            if isinstance(e, SqlQueryException):
                logger.exception(u"数据平台查询失败：%s" % e)
                data["access_div_message"] = u"数据查询异常，请联系管理员"
            else:
                data["access_div_message"] = access_status.get("div_message")
            data["access_btn_message"] = access_status.get("btn_message")
        return render_json(failed_data(u"", data))
    # except SqlQueryException as e:
    #     logger.exception(u"数据平台查询失败：%s" % e)
    #     return render_json(failed_data(u"数据查询异常", data))
    except Exception as e:
        logger.exception(u"拉取主机性能信息失败: %s" % e)
        return render_json(failed_data(u"系统错误", data))
    finally:
        ts.stop()
        time_stats_info = ts.display()
        logger.warning(time_stats_info)


@check_perm
def stick_host(request, cc_biz_id):
    """
    主机置顶/取消置顶
    """
    args = request.POST
    host_id = args.get("host_id")
    if not (host_id and "|" in host_id):
        return render_json(failed(u"无效请求"))
    ip, plat_id = parse_host_id(host_id)
    MonitorHostSticky.objects.filter(host=ip, plat_id=plat_id,
                                     cc_biz_id=cc_biz_id).delete()
    if args.get("action") == "add":
        hs = MonitorHostSticky(host=ip, plat_id=plat_id, cc_biz_id=cc_biz_id)
        hs.save()
        return render_json(ok_data(hs.id))
    return render_json(ok_data(0))


@check_perm
def get_alarm_list(request, cc_biz_id):
    """
    获取ip关联的告警事件列表
    """
    args = request.GET
    alarm_date = args.get("alarm_date")
    host_id = args.get("host_id")
    if not host_id:
        return render_json(failed(u"无效的请求"))
    alarm_list = AlarmInstance.get_alarm_list_by_host_id(
        host_id, cc_biz_id, alarm_date
    )
    alarm_info_list = filter(
        lambda alarm: alarm, map(lambda a: a.detail, alarm_list)
    )
    return render_json(ok_data({"alarm_info_list": alarm_info_list}))


@check_perm
def get_alarm_count(request, cc_biz_id):
    """
    获取一串主机某日的告警事件数
    """
    args = request.GET
    alarm_date = args.get("alarm_date")
    host_id_list = args.get("host_id_list")
    if not host_id_list:
        return render_json(failed(u"无效的请求"))
    host_id_list = host_id_list.split(',')
    alarm_count_info = AlarmInstance.get_alarm_count_by_host_id_list(
        host_id_list, cc_biz_id, alarm_date
    )
    return render_json(ok_data({"alarm_count_info": alarm_count_info}))


@check_perm
def get_alarm_strategy_list(request, cc_biz_id):
    """
    获取ip关联的告警策略列表
    """

    strategy_info_list = list()
    args = request.GET
    host_id = args.get("host_id")
    if not host_id:
        return render_json(failed(u"无效的请求"))
    alarm_strategys = AlarmStrategy.objects.get_strategy_by_host_id(
        host_id, cc_biz_id
    )
    for strategy in alarm_strategys:
        item = AlarmStrategy.objects.get_alarm_strategy_info(strategy)
        if item is not None:
            strategy_info_list.append(item)
    return render_json(ok_data(strategy_info_list))


@check_perm
def host_index_option_list(request, cc_biz_id):
    """
    主机性能列表，select2展示参数
    :param request:
    :param cc_biz_id:
        ("cpu", u"CPU"),
        ("net", u"网卡"),
        ("mem", u"内存"),
        ("disk", u"磁盘"),
        ("process", u"进程"),
    """

    info_list = []
    fields = {
        'cpu': u"CPU",
        'net': u"网卡",
        'mem': u"内存",
        'disk': u"磁盘",
        # 'process': u"进程",
    }
    for _f in fields:
        # 只过滤需要展示的内容
        hosts = HostIndex.objects.filter(graph_show=True, category=_f)
        data = []
        for _h in hosts:
            info = dict(id=_h.id, item=_h.item,
                        text=_h.desc, unit=_h.unit_display)
            data.append(info)
        info_list.append({"text": fields[_f], "children": data})
    categories_sorted_list = [i[1] for i in HostIndex.CATEGORY_CHOICES]
    info_list = sorted(
        info_list,
        key=lambda x: categories_sorted_list.index(x["text"])
        if x["text"] in categories_sorted_list else 10000)
    info_list.append(BaseHostIndex.get_base_hostindex_options())
    return render_json(ok_data(info_list))


@check_perm
def host_index_list(request, cc_biz_id):
    """
    获取单个主机性能列表
    """

    def index_to_dict(host_index_obj, dimension_field_value=""):
        return {
            "description": host_index_obj.desc,
            "category": host_index_obj.get_category_display(),
            "dimension_field": host_index_obj.dimension_field,
            "dimension_field_value": dimension_field_value,
            "index_id": host_index_obj.id,
            "unit_display": host_index_obj.unit_display,
        }

    all_graphs = list()
    index_info = HostIndex.get_bp_graph_index()
    bp_index_list = [_index for index_list in index_info.values()
                     for _index in index_list]
    dimension_values_cache = {}
    for bp_index in bp_index_list:
        # 是否维度细分
        if bp_index.dimension_field and bp_index.dimension_field == "name":
            from utils.trt import trans_bkcloud_rt_bizid
            rt_id = trans_bkcloud_rt_bizid("%s_%s" % (cc_biz_id, bp_index.result_table_id))
            cache_key = "%s:%s" % (rt_id, bp_index.dimension_field)
            if cache_key not in dimension_values_cache:
                dimension_values = get_field_results(
                    rt_id,
                    bp_index.dimension_field
                )
                dimension_values_cache[cache_key] = dimension_values
            else:
                dimension_values = dimension_values_cache[cache_key]
            # 网卡拆分 这里列出了业务下所有主机的eth网卡，在前端需要根据ip展示。
            eth_values = filter(lambda eth: str(eth).strip().startswith("eth"),
                                dimension_values)
            if eth_values:
                for v in eth_values:
                    all_graphs.append(index_to_dict(bp_index, v))
                continue
        all_graphs.append(index_to_dict(bp_index))
    categories_sorted_list = [i[1] for i in HostIndex.CATEGORY_CHOICES]
    all_graphs = sorted(all_graphs,
                        key=lambda x:
                        categories_sorted_list.index(x["category"])
                        if x["category"] in categories_sorted_list else 10000)
    return render_json(ok_data(all_graphs))


@check_perm
def get_eth_info(request, cc_biz_id):
    """
    获取各主机对应的网卡信息, rt_id: ja_gse_net_detail
    """
    return render_json(ok_data(HostIndex.get_eth_info_by_biz(cc_biz_id)))


@check_perm
def graph_point(request, cc_biz_id):
    """
    获取图表数据
    """
    args = request.GET
    time_range = None
    single_graph_date = args.get("graph_date")
    host_id = request.GET.get("host_id", "")
    index_id = args.get("index_id", "")
    ip = plat_id = index_obj = ""
    with ignored(Exception):
        # 主机信息
        ip, plat_id = parse_host_id(host_id)
        # 需要转换平台id（gse的0 等于 cc的1）........................
        plat_id = "0" if plat_id == "1" else plat_id
        index_obj = HostIndex.get(id=index_id)
        # 时间解析
        if single_graph_date:
            start = datetime.datetime.strptime(single_graph_date, "%Y-%m-%d")
            end = start + datetime.timedelta(days=1)
            time_range = "%s -- %s" % (
                start.strftime("%Y-%m-%d %H:%M"),
                end.strftime("%Y-%m-%d %H:%M"))
    if not all([ip, plat_id, index_obj]):
        return render_json(failed(u"无效的请求"))
    try:
        unit = index_obj.unit_display
        conversion = float(index_obj.conversion)
        ext_kw = {"unit": unit, "conversion": conversion,
                  "series_label_show": index_obj.desc}
        kwargs = {
            "time_range": time_range,
            "ip": ip,
            "cloud_id": str(plat_id)
        }
        result_table_id = index_obj.result_table_id
        value_field = index_obj.item
        group_field = index_obj.dimension_field
        rt_id = "%s_%s" % (cc_biz_id, result_table_id)
        if group_field:
            ext_kw["group_field"] = group_field
        series_suffix = ""
        dimension_field = args.get("dimension_field",
                                   index_obj.dimension_field)
        dimension_value = args.get("dimension_field_value", "")
        if dimension_field and dimension_value:
            kwargs[dimension_field] = dimension_value
        series_name_list = []
        series_list = []
        from utils.trt import trans_bkcloud_rt_bizid
        rt_id = trans_bkcloud_rt_bizid(rt_id)
        data = DataProcessor.base_performance_data(rt_id, value_field,
                                                         kwargs, **ext_kw)
        for series_name in data["series_name_list"]:
            series_name_list.append(series_name + series_suffix)
        for series in data["series"]:
            if series["name"] in [u"本周期"]:
                series["zIndex"] = 5
            series["name"] += series_suffix
            series_list.append(series)
        data["series"] = series_list
        data["series_name_list"] = series_name_list
        data["min_y"] = min(data["min_y"], 0)
        data["max_y"] = max(data["max_y"], 0)
        if data["min_y"] == data["max_y"]:
            if data["max_y"] == 0:
                data["yaxis_range"] = "0:1"
            if data["max_y"] > 0:
                data["yaxis_range"] = "0:"
            if data["max_y"] < 0:
                data["yaxis_range"] = ":0"
        data = {'data': data, 'echo_sql': data['echo_sql']}
        del data["data"]["echo_sql"]
        data["update_time"] = datetime.datetime.now()
        return render_json(ok_data(data))
    except EmptyQueryException:
        return render_json(
            failed_data(
                u"查询无数据，请确认该主机（%s）的数据上报是否正常！" % ip,
                {
                    'echo_sql': "",
                    'error_class': 'info'
                }
            )
        )
    except SqlQueryException as e:
        logger.exception(u"查询失败，原因: %s" % e)
        return render_json(
            failed_data(
                u"查询失败，原因: %s" % e,
                {
                    'echo_sql': "",
                    'error_class': 'warning'
                }
            )
        )
    except TableNotExistException as e:
        logger.exception(e)
        return render_json(
            failed_data(
                u"查询无数据！" ,
                {
                    'echo_sql': "",
                    'error_class': 'info',
                    'need_access': "need_access"
                }
            )
        )
    except Exception as e:
        logger.exception(u"后台异常: %s" % e)
        return render_json(
            failed_data(
                u"生成图表异常",
                {
                    'echo_sql': "",
                    'error_class': 'critical'
                }
            )
        )

@require_POST
@check_perm
def bp_access(request, cc_biz_id):
    """
    基础性能接入
    """
    args = request.POST
    hostid_list = args.get("hostid_list", "")
    ip_list = None
    if hostid_list:
        hostid_list = hostid_list.split(",")
        # 置顶ip列表接入
        ip_list = []
        for hostid in hostid_list:
            ip, plat_id = parse_host_id(hostid)
            ip_list.append({
                "ip": ip,
                "plat_id": plat_id,
            })
    try:
        result = access_performance(cc_biz_id, ip_list)
        if result.get("result"):
            return render_json(ok())
        else:
            return render_json(failed(u"基础性能接入失败：%s" % result.get("message")))
    except Exception as e:
        logger.exception(u"基础性能接入失败:%s" % e)
        return render_json(failed(u"基础性能接入失败，请联系管理员"))


@check_perm
def get_task_list(request, cc_biz_id):
    solution_type = request.GET.get("solution_type")
    solution_model = SolutionConf.solution_model(solution_type)
    if solution_model is None:
        return render_json(failed_data(u"无效的请求", []))
    task_list = solution_model.task_list(cc_biz_id)
    return render_json(ok_data(task_list))

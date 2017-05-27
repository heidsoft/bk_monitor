# -*- coding: utf-8 -*-
from django.conf.urls import patterns

# 主机性能监控
performance_urlpatterns = patterns(
    "monitor.performance.views",
    # 基础性能监控V2
    (r"^(?P<cc_biz_id>\d+)/bp/$", "index"),
    # 查询集群
    (r"^(?P<cc_biz_id>\d+)/get_cc_set/$", "get_cc_set"),
    # 查询模块
    (r"^(?P<cc_biz_id>\d+)/get_cc_module/$", "get_cc_module"),
    # 查询主机属性列表
    (r"^(?P<cc_biz_id>\d+)/get_host_property_list/$", "get_host_property_list"),
    # 查询业务下各主机网卡信息
    (r"^(?P<cc_biz_id>\d+)/get_eth_info/$", "get_eth_info"),
    # 查询业务下云平台信息列表
    (r"^(?P<cc_biz_id>\d+)/get_plat_list/$", "get_plat_list"),
    # 主机置顶/取消置顶
    (r"^(?P<cc_biz_id>\d+)/bp/stick_host/$", "stick_host"),
    # 根据主机id获取主机agent状态
    (r"^(?P<cc_biz_id>\d+)/get_agent_status/$", "get_agent_status"),
    # 获取主机告警事件列表
    (r"^(?P<cc_biz_id>\d+)/bp/get_alarm_list/$", "get_alarm_list"),
    # 获取主机告警事件数
    (r"^(?P<cc_biz_id>\d+)/bp/get_alarm_count/$", "get_alarm_count"),
    # 获取主机关联告警策略列表
    (r"^(?P<cc_biz_id>\d+)/bp/get_alarm_strategy_list/$", "get_alarm_strategy_list"),
    # 获取主机性能指标列表
    (r"^(?P<cc_biz_id>\d+)/bp/host_index_list/$", "host_index_list"),
    # 获取主机性能指标列表select2参数
    (r"^(?P<cc_biz_id>\d+)/bp/host_index_option_list/$", "host_index_option_list"),
    # 获取主机性能指标图表数据
    (r"^(?P<cc_biz_id>\d+)/bp/graph/point/$", "graph_point"),
    # 基础性能接入
    (r"^(?P<cc_biz_id>\d+)/bp/access/$", "bp_access"),
    # 获取作业平台任务列表
    (r"^(?P<cc_biz_id>\d+)/get_task_list/$", "get_task_list"),

)

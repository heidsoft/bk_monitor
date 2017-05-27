# -*- coding: utf-8 -*-
from django.conf.urls import patterns


# 自定义监控
dataview_urlpatterns = patterns(
    "monitor.dataview.views",

    # 运营数据监控
    (r"^(?P<cc_biz_id>\d+)/operation_monitor/$", "operation_monitor"),
    # 菜单列表
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/menu/list/$", "operation_menu_list"),
    # 渲染视图面板
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/graph/panel/$", "operation_graph_panel"),
    # 新增菜单
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/menu/add/$", "operation_menu_add"),
    # 编辑菜单
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/menu/edit/$", "operation_menu_edit"),
    # 删除菜单
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/menu/del/$", "operation_menu_del"),
    # 根据监控获取维度字段取值
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/field/values/$", "get_filter_field_results_by_monitor"),
    # 获取监控视图数据
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/graph/point/$", "get_operation_monitor_point"),
    # 获取监控告警列表
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/alert/list/$", "get_operation_monitor_alert_list"),
    # 收藏/取消收藏
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/favorite/toggle/$", "favorite_toggle"),
    # 删除视图
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/location/del/$", "delete_monitor_location"),
    # 新增视图
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/location/add/$", "add_monitor_loaction"),
    # 获取监控信息
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/info/$", "monitor_info"),
    # 获取图表详情页面
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/graph_detail/$", "graph_detail"),
    # 获取图表详情数据
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/graph_detail_point/$", "graph_detail_point"),
    # 获取所有维度对应的值
    (r"^(?P<cc_biz_id>\d+)/operation/monitor/get_all_field_values/$", "get_all_field_values"),

)

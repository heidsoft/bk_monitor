# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'monitor.overview.views',
    url(r'^$', 'overview'),
    # 概览-关注面板
    (r"^star/panel/$", "render_star_panel"),
    # 事件列表数据
    (r"^get_event_data/(?P<event_type>[a-zA-Z]+)/(?P<begin_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/"
     r"(?P<end_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/(?P<page>\d+)/$", "get_event_data"),
    # 告警数量数据
    (r"^get_alarm_num_data/(?P<period>[a-zA-Z]+)/(?P<group_field>[a-zA-Z]+)/(?P<recent_intervals>\d+)/$",
     "get_alarm_num_data"),
    # 自定义监控数量
    (r"^get_custom_monitor_num/$", "get_custom_monitor_num"),
    # 获取agent安装状态
    (r"^get_agent_status/$", "get_agent_status"),
    # 获取agent上报数据状态
    (r"^get_agent_data_report_status/$", "get_agent_data_report_status"),
)

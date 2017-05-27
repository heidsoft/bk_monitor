# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns(
    "monitor.event_center.views",
    (r"^$", "home"),
    (r"^get_alarm_data/$", "get_alarm_data"),
    # 告警数量数据
    (r"^get_alarm_num_data/(?P<period>[a-zA-Z]+)/"
     r"(?P<group_field>[a-zA-Z]+)/(?P<begin_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/"
     r"(?P<end_time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/$", "get_alarm_num_data"),
)

events_urlpatterns = patterns(
    "monitor.event_center.views",
    # 告警详情
    (r"^(?P<cc_biz_id>\d+)/alarm/(?P<alarm_id>\d+)/$", "alarm_detail"),
    (r"^alarm/(?P<alarm_id>\d+)/$", "alarm_detail"),
    (r"^get_alarm_detail_chart_list/$", "get_alarm_detail_chart_list"),
    (r"^get_alarm_detail_main_chart_data/$", "get_alarm_detail_main_chart_data"),
    (r"^get_alarm_detail_sub_chart_data/$", "get_alarm_detail_sub_chart_data"),
)
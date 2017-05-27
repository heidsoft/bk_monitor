# coding=utf-8

# import from standard lib here

# import from third lib here
from django.conf.urls import patterns, url

# import from apps here

urlpatterns = patterns(
    'monitor.datasource.views',
    url(r'^$', 'home'),
    # 获取数据源列表
    url(r'^get_ds_list/(?P<page>\d+)/(?P<page_size>\d+)/$', 'get_ds_list'),
    # 获取数据源详情
    url(r'^get_ds/(?P<ds_id>\d+)/$', 'get_ds'),
    # 获取数据源上报数据节点状态
    url(r'^get_agent_status/(?P<ds_id>\d+)/(?P<page>\d+)/(?P<page_size>\d+)/$', 'get_agent_status'),
    # 获取数据源数据明细总数
    url(r'^get_ds_data_total/(?P<ds_id>\d+)/$', 'get_ds_data_total'),
    # 获取数据源的数据明细
    url(r'^get_ds_data_list/(?P<ds_id>\d+)/(?P<page>\d+)/(?P<page_size>\d+)/$', 'get_ds_data_list'),
    # 新增/编辑数据源
    url(r'^config/(?P<ds_id>\d+)/$', 'config_ds'),
    # 启用/停用数据源
    url(r'^(?P<action>on|off)/(?P<ds_id>\d+)/$', 'toggle_ds'),
    # 新增/删除/重新下发agent
    url(r'^manage_agent/(?P<action>append|remove|refresh)/(?P<ds_id>\d+)/(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/$', 'manage_agent'),
    # 获取配置项
    url(r'^get_options/$', 'get_options'),
    # 获取数据源关联监控项
    url(r'^get_ds_monitors/(?P<ds_id>\d+)/$', 'get_ds_monitors'),
    # 更新数据源状态
    url(r'^update_ds_status/$', 'update_ds_status'),
)
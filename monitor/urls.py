# -*- coding: utf-8 -*-
from django.conf.urls import include, patterns, url

from monitor.api.urls import api_urlpatterns
from monitor.config.urls import config_urlpatterns
from monitor.dataview.urls import dataview_urlpatterns
from monitor.event_center.urls import events_urlpatterns
from monitor.performance.urls import performance_urlpatterns


urlpatterns_monitor = patterns(
    '',
    # 首页
    url(r'^$', "monitor.overview.views.home"),
    url(r'^(?P<cc_biz_id>\d+)/overview/', include('monitor.overview.urls')),
    # 事件中心
    url(r'^(?P<cc_biz_id>\d+)/event_center/', include('monitor.event_center.urls')),
    # 数据源接入
    url(r'^(?P<cc_biz_id>\d+)/datasource/', include('monitor.datasource.urls'))
)

urlpatterns_monitor += events_urlpatterns
urlpatterns_monitor += performance_urlpatterns
urlpatterns_monitor += api_urlpatterns
urlpatterns_monitor += config_urlpatterns
urlpatterns_monitor += dataview_urlpatterns

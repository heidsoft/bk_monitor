# -*- coding: utf-8 -*-

from django.conf.urls import patterns

urlpatterns = patterns('home_application.views',
    # 首页--your index
    (r'^$', 'home'),
    (r'^dev-guide/$', 'dev_guide'),
    (r'^contactus/$', 'contactus'),
    # 功能开关
    (r'^get_func_part/$', 'get_func_part'),
    (r'^switch_func/$', 'switch_func'),
    (r'^excute_func/$', 'excute_func'),
)

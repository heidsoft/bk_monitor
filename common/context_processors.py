# -*- coding: utf-8 -*-
"""
context_processor for common(setting)

除setting外的其他context_processor内容，均采用组件的方式(string)
"""
from __future__ import absolute_import
import datetime
from django.conf import settings
from utils import query_cc



def generate_biz_names():
    cc_biz_names = {
        info["ApplicationID"]: info["ApplicationName"]
        for info in query_cc.get_app_by_user()}
    return cc_biz_names


def mysetting(request):
    return {
        # 基础信息
        'RUN_MODE': settings.RUN_MODE,
        'APP_CODE': settings.APP_ID,
        'SITE_URL': settings.SITE_URL,
        'BK_PAAS_HOST': settings.BK_PAAS_HOST,
        # 静态资源
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_VERSION': settings.STATIC_VERSION,
        # 登录跳转链接
        'LOGIN_URL': settings.LOGIN_URL,
        'LOGOUT_URL': settings.LOGOUT_URL,
        # 当前页面，主要为了login_required做跳转用
        'APP_PATH': request.get_full_path(),
        'NOW': datetime.datetime.now(),
        'NICK': request.session.get('nick', ''),  # 用户昵称
        'AVATAR': request.session.get('avatar', ''),
        'cc_biz_names': generate_biz_names()
    }

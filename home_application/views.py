# -*- coding: utf-8 -*-

from common.mymako import render_mako_context, render_json
from common.log import logger
from app_control.decorators import function_check
from app_control.models import Function_controller


def home(request):
    """
    首页
    """
    return render_mako_context(request, '/home_application/home.html')


def dev_guide(request):
    """
    开发指引
    """
    return render_mako_context(request, '/home_application/dev_guide.html')


def contactus(request):
    """
    联系我们
    """
    return render_mako_context(request, '/home_application/contact.html')


# =========================================================================
# 功能开关示例
# =========================================================================
def get_func_part(request):
    """
    加载功能推荐页面
    """
    # 查询示例功能开关是否开启
    try:
        func_info = Function_controller.objects.filter(func_code='func_test')
        if func_info:
            func_info = func_info[0]
        else:
            func_info = Function_controller.objects.create(
                func_code='func_test',
                func_name=u"示例功能",
                enabled=False,
                func_developer='',
            )
        # 获取功能开启状态
        is_enabled = func_info.enabled
    except Exception, e:
        logger.error(u"加载功能推荐页面失败，异常信息：%s" % e)
        is_enabled = False
    return render_mako_context(request, '/home_application/func_check.part',
                               {'is_enabled': is_enabled})


def switch_func(request):
    """
    开启、关闭示例功能
    """
    try:
        status = int(request.POST.get('status', '0'))
        # 更改功能开关的状态
        Function_controller.objects.filter(func_code='func_test').update(enabled=status)
    except Exception, e:
        msg = u"更改功能状态出错，异常信息：%s" % e
        return render_json({'res': False, 'msg': msg})
    return render_json({'res': True, 'msg': u"操作成功"})


@function_check('func_test')
def excute_func(request):
    """
    开启、关闭示例功能
    """
    return render_json({'res': True, 'msg': u"这是一个功能开关示例"})

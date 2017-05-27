# -*- coding: utf-8 -*-

import functools
import json
import sys
import traceback

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse

from utils.query_cc import get_user_biz
from common.log import logger


def api(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return_value = func(*args, **kwargs)
        except Exception, e:
            _, _, tb = sys.exc_info()
            filepath, lineno, _, _ = traceback.extract_tb(tb)[-1]
            result = {"result": False,
                      "data": None,
                      "message": u"",
                      "code": str(lineno)}
            logger.exception("API ERROR %s", e)
        else:
            result = {"result": True,
                      "data": return_value,
                      "message": "",
                      "code": "0"}
        return HttpResponse(json.dumps(result))
    return wrapper


def check_perm(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request = kwargs.get("request") or args[0]
        cc_biz_id = kwargs.get("cc_biz_id") or args[1]
        try:
            check_perm_with_raise(request.user, cc_biz_id)
        except Exception, e:
            raise PermissionDenied(unicode(e))
        return func(*args, **kwargs)
    return wrapper


def check_param_perm(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        request = kwargs.get("request") or args[0]
        cc_biz_id = (request.POST.get('cc_biz_id') or
                     request.POST.get('biz_id') or
                     request.GET.get('cc_biz_id') or
                     request.GET.get('biz_id'))
        if not cc_biz_id:
            try:
                param = json.loads(request.POST['param'])
                cc_biz_id = param.get('cc_biz_id') or param.get('biz_id')
            except Exception, e:
                logger.exception(e)
                cc_biz_id = None
        logger.info("check_param_perm biz_id: %s" % cc_biz_id)
        try:
            check_perm_with_raise(request.user, cc_biz_id)
        except Exception, e:
            raise PermissionDenied(unicode(e))
        return func(*args, **kwargs)
    return wrapper


def check_perm_with_raise(user, cc_biz_id):
    if settings.RUN_MODE != "DEVELOP" or 1:
        if cc_biz_id not in get_user_biz(user):
            raise Exception(u"对不起，您没有该业务的权限")

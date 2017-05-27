# -*- coding: utf-8 -*-
from django.dispatch import Signal

from common.log import logger

#===============================================================================
# 中间件并且提供方法：Django中在view中调用函数（function），不需要向函数传递request参数，就能获取到request
#===============================================================================
class SingleHandlerSignal(Signal):
    """
    @summary: 用于处理注册事件类
    """
    allowed_receiver='utils.request_middlewares.RequestProvider'

    def __init__(self,providing_args = None):
        Signal.__init__(self,providing_args)

    def connect(self, receiver, sender=None, weak=True, dispatch_uid=None):
        receiver_name = '.'.join(
            [receiver.__class__.__module__, receiver.__class__.__name__]
        )
        if receiver_name != self.allowed_receiver:
            logger.error(u"没有注册过signal receiver: %s" % receiver_name)
        Signal.connect(self, receiver, sender, weak, dispatch_uid)


request_accessor = SingleHandlerSignal()

class RequestProvider(object):
    """
    @summary: request事件接收者
    """
    def __init__(self):
        self._request = None
        request_accessor.connect(self)

    def process_request(self,request):
        self._request = request
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        self._request.biz_id = view_kwargs.get("cc_biz_id", "")

    def __call__(self,**kwargs):
        return self._request


def get_request():
    """
    @summary: 获取request
    """
    return request_accessor.send(None)[0][1]


def get_x_request_id(is_logger_call=False):
    """
    @summary: 获取APP请求头唯一标识 x-request-id
    """
    try:
        x_request_id = ''
        http_request = get_request()
        if hasattr(http_request, 'META'):
            meta = http_request.META
            x_request_id = (meta.get('HTTP_X_REQUEST_ID', '')
                            if isinstance(meta, dict) else '')
    except Exception, e:
        #如果是logger函数调用则不可将异常写入日志，否则可能会引起死循环
        #非logger调用此函数的可以使用logger
        if not is_logger_call:
            #logger.error(u"get_x_request_id: %s" % e)
            pass
        x_request_id = ''
    return x_request_id


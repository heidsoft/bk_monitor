# -*- coding: utf-8 -*-
from django.conf import settings

from utils.request_middlewares import get_request


# 这里配置sdk包名和setting.RUN_VER的对应关系,需要维护
plat_package_map = {
    # 内部版
    "ied": "ieod",
    # 腾讯云
    "qcloud": "qcloud",
    # 混合云
    "clouds": "clouds",
    # 社区版
    "openpaas": ""
}


class SDKClient(object):
    sdk_package = None
    sdk_plat_module = dict()

    @property
    def __version__(self):
        return self.__class__.sdk_package.__version__

    def __new__(cls):
        if cls.sdk_package is None:
            try:
                cls.sdk_package = __import__(sdk_module_name(),
                                             fromlist=['shortcuts'])
            except ImportError, e:
                raise ImportError("sdk for platform(%s) is not installed: %s"
                                  % (sdk_plat(), e))
        return super(SDKClient, cls).__new__(cls)

    def __init__(self):
        self.mod_name = ""
        self.sdk_mod = None

    def __getattr__(self, item):
        if not self.mod_name:
            ret = SDKClient()
            ret.mod_name = item
            ret.setup_modules()
            if callable(ret.sdk_mod):
                return ret.sdk_mod
            return ret
        else:
            # 真实sdk调用入口
            ret = getattr(self.sdk_mod, item)
        if callable(ret):
            print self.mod_name, "->", item
        else:
            ret = self
        return ret

    def setup_modules(self):
        self.sdk_mod = getattr(self.sdk_client, self.mod_name, None)
        if self.sdk_mod is None:
            raise ImportError("sdk for platform(%s) has no module :%s" %
                              (sdk_plat(), self.mod_name))

    @property
    def sdk_client(self):
        try:
            request = get_request()
            # 调用sdk方法获取sdk client
            return self.sdk_package.shortcuts.get_client_by_request(request)
        except:
            if settings.RUN_MODE != "DEVELOP":
                raise TypeError("sdk can only be invoked through a Web request")
            else:
                try:
                    from account.models import BkUser as User
                except ImportError:
                    from account.models import User
                return self.sdk_package.shortcuts.get_client_by_user(User.objects.all().order_by("-last_login")[0])


def sdk_module_name():
    plat = sdk_plat()
    plat = ".%s" % plat if plat else plat
    return 'blueking.component{plat}'.format(plat=plat)


def sdk_plat():
    return plat_package_map.get(settings.RUN_VER, settings.RUN_VER)


client = SDKClient()

# -*- coding: utf-8 -*-
import json
import collections

from common.log import logger
from monitor.constants import AGENT_STATUS
from utils.cache import web_cache
from utils.common_utils import ignored, host_key, parse_host_id
from utils.sdk_client import client


def get_user_biz(user=None):
    return [info["ApplicationID"] for info in get_app_by_user()]


@web_cache(60*10)
def get_app_by_user():
    result = client.cc.get_app_by_user({})
    apps = []
    if result["result"]:
        apps = [app for app in (result["data"] or []) if app["Default"] != "1"]
    return apps


def get_plat(app_id):
    result = client.cc.get_plat_id()
    plat_list = []
    if not result["result"]:
        return []
    all_plat = [d for d in result["data"] if not d["platCompany"]]
    info = client.cc.get_app_host_list(dict(app_id=app_id))
    if not info["result"]:
        return []
    for i in info["data"]:
        if i["Source"] == "0":
            plat_list.append("1")
        else:
            plat_list.append(i["Source"])
    data = [_id for _id in all_plat if _id["platId"] in plat_list]
    return data


class CCBiz(object):
    """
    使用方法：
    >>> CCBiz(cc_biz_id=120).get("GroupName")

    >>> CCBiz.items(key="ApplicationID", value="DisplayName")  # 获取字典

    一些常用的属性：  (更多请参考 http://ccapi.ied.com/)
    "DisplayName" 产品名称，如"穿越火线"
    "Abbreviation" 英文缩写，如"CF"
    "GameTypeName" 产品子类，如"移动终端"表示手游
    "GroupName" 运维小组，如"深圳自研业务组"
    "Maintainers" 业务运维，如"reidwang;yarkeezhou"
    """

    def __init__(self, cc_biz_id=None, cc_biz_name=None):
        assert cc_biz_id or cc_biz_name
        if cc_biz_id:
            self.key = "ApplicationID"
            self.key_value = unicode(cc_biz_id)
        elif cc_biz_name:
            self.key = "DisplayName"
            self.key_value = unicode(cc_biz_name)

    @staticmethod
    @web_cache(60)
    def sets(cc_biz_id):
        """获取业务下SET列表，按机器数量排序"""
        # 获取set列表
        with ignored(Exception):
            ips = set([])
            set_list = client.cc.get_sets_by_property(
                app_id=cc_biz_id
            ).get("data") or []
            set_id_list = [set_item["SetID"] for set_item in set_list]
            host_list = CCBiz._hosts(cc_biz_id).get("data") or []
            if set_id_list:
                set_info = collections.defaultdict(set)
                for host in host_list:
                    if host["SetID"] in set_id_list:
                        set_info[host["SetID"]].add(host_key(host))
                        set_info["0"].add(host_key(host))
                for set_item in set_list:
                    set_item["host_count"] = len(set_info[set_item["SetID"]])
                    set_item["SetName"] += ' [%s]' % set_item["host_count"]
                set_list = sorted(
                    set_list, key=lambda x: x['host_count'], reverse=True
                )
                return set_list, len(set_info["0"])
        return [], 0

    @staticmethod
    @web_cache(60)
    def modules(cc_biz_id, set_id_list=None):
        """获取业务下的模块列表，按机器数量排序"""
        with ignored(Exception):
            ips = set([])
            if set_id_list and (not hasattr(set_id_list, "__iter__")):
                set_id_list = [set_id_list]
            if set_id_list is not None:
                set_id_list = ";".join(map(str, set_id_list))
            module_list = client.cc.get_modules_by_property(
                app_id=cc_biz_id, set_id=set_id_list
            ).get("data") or []
            module_id_list = [module_item["ModuleID"]
                              for module_item in module_list]
            host_list = CCBiz._hosts(cc_biz_id).get("data") or []
            if module_id_list:
                module_info = collections.defaultdict(set)
                for host in host_list:
                    if host["ModuleID"] in module_id_list:
                        module_info[host["ModuleID"]].add(host_key(host))
                        module_info["0"].add(host_key(host))
                for set_item in module_list:
                    set_item["host_count"] = len(
                        module_info[set_item["ModuleID"]]
                    )
                    set_item["ModuleName"] += ' [%s]' % set_item["host_count"]
                module_list = sorted(
                    module_list, key=lambda x: x['host_count'], reverse=True)
                return module_list, len(module_info["0"])
        return [], 0

    @staticmethod
    def agent_status(cc_biz_id, host_id_list):
        """获取agent状态信息
        agent状态详细分成4个状态：正常，离线，未安装。已安装，无数据。
        """
        result = collections.defaultdict(int)
        with ignored(Exception):
            ip_info_list = list()
            if not hasattr(host_id_list, "__iter__"):
                host_id_list = [host_id_list]
            for host_id in host_id_list:
                ip, plat_id = parse_host_id(host_id)
                plat_id = plat_id if plat_id != "1" else "0"
                ip_info_list.append({
                    "ip": ip,
                    "plat_id": plat_id
                })
            if not ip_info_list:
                return {}
            status_list = client.job.get_agent_status(
                app_id=cc_biz_id,
                ip_infos=ip_info_list, is_real_time=1
            ).get("data") or []
            for info in status_list:
                plat_id = info["plat_id"]
                ip = info["ip"]
                host_id = host_key(ip=ip, plat_id=plat_id)
                exist = bool(info["status"])
                if not exist:
                    result[host_id] = AGENT_STATUS.NOT_EXIST
                    continue
                else:
                    result[host_id] = AGENT_STATUS.ON
        return result

    @staticmethod
    @web_cache(60)
    def set_module_ips(cc_biz_id, set_id="", module_id=""):
        """获取业务下大区下模块的ip列表，根据平台id和ip组合去重"""
        ips = set(list())
        with ignored(Exception):
            if module_id:
                result = client.cc.get_module_host_list(
                    app_id=cc_biz_id, module_id=module_id
                )
            else:
                result = client.cc.get_hosts_by_property(
                    app_id=cc_biz_id, set_id=set_id
                )
            if result["result"]:
                for host in (result.get("data") or []):
                    ips.add(host_key(host))
        return sorted(list(set(ips)))

    @staticmethod
    @web_cache(60)
    def ips(cc_biz_id, plat_id=None):
        """获取业务下的ip列表，按IP排序"""
        ips = []
        with ignored(Exception):
            result = CCBiz._hosts(cc_biz_id)
            if result["result"]:
                for data in (result.get("data") or []):
                    if data["Source"] == "0":
                        data["Source"] = "1"
                    if plat_id is not None and plat_id == data["Source"]:
                        ips.append(data["InnerIP"])
        return sorted(ips)

    @staticmethod
    @web_cache(60)
    def _hosts(cc_biz_id):
        result = client.cc.get_app_host_list(app_id=cc_biz_id)
        if result["result"]:
            for data in (result.get("data") or []):
                if data["Source"] == "0":
                    data["Source"] = "1"
        return result

    @staticmethod
    def hosts(cc_biz_id):
        return CCBiz._hosts(cc_biz_id)

    @staticmethod
    def host_detail(cc_biz_id, ip, plat_id):
        result = dict()
        with ignored(Exception):
            result = client.cc.get_host_list_by_ip(
                ip=ip, app_id=cc_biz_id, plat_id=plat_id
            )
        return result.get("data") or []

    @staticmethod
    def host_property_list(cc_biz_id):
        result = dict()
        with ignored(Exception):
            result = client.cc.get_property_list(
                app_id=cc_biz_id, type=4
            )
        return result.get("data", {})

    @staticmethod
    def maintainers(cc_biz_id):
        result = client.cc.get_app_by_id(dict(app_id=cc_biz_id))
        biz_info = (result.get("data") or []) if result["result"] else []
        maintainer = biz_info[0]["Maintainers"].split(";") if biz_info else []
        user_info_list = get_owner_info()
        user_info = {item['username']: item['chname']
                     for item in user_info_list
                     if str(item['username']) in maintainer}
        return user_info

    @staticmethod
    @web_cache(60)
    def set_name(cc_biz_id, set_id_list):
        if not hasattr(set_id_list, "__iter__"):
            set_id_list = [set_id_list]
        set_list = client.cc.get_sets_by_property(
            app_id=cc_biz_id
        ).get("data") or []
        set_name_dict = dict().fromkeys(set_id_list, u"未知")
        for set_item in set_list:
            if set_item["SetID"] in set_name_dict:
                set_name_dict[set_item["SetID"]] = set_item["SetName"]
        return set_name_dict

    @staticmethod
    @web_cache(60)
    def module_name(cc_biz_id, module_id_list):
        if not hasattr(module_id_list, "__iter__"):
            module_id_list = [module_id_list]
        module_list = client.cc.get_modules(app_id=cc_biz_id).get("data") or []
        module_name_dict = dict().fromkeys(module_id_list, u"未知")
        for module_item in module_list:
            if "ModuleID" not in module_item:
                continue
            module_id = module_item["ModuleID"]
            if module_id in module_name_dict:
                module_name_dict[module_id] = module_item["ModuleName"]
        return module_name_dict


    @staticmethod
    @web_cache(60)
    def user_info():
        # key 转换成字符串
        user_dict = {}
        userinfo_list = get_owner_info()
        for userinfo in userinfo_list:
            user_dict[str(userinfo['username'])] = userinfo['chname']
        return user_dict

    @staticmethod
    @web_cache(60)
    def plat_info(cc_biz_id):
        result = client.cc.get_plat_id()
        plat_list = []
        if not result["result"]:
            return []
        all_plat = [d for d in (result.get("data") or [])
                    if not d["platCompany"]]
        info = client.cc.get_app_host_list(dict(app_id=cc_biz_id))
        logger.info("info: %s" % json.dumps(info))
        if not info["result"]:
            return []
        for i in (info["data"] or []):
            if i["Source"] == "0":
                plat_list.append("1")
            else:
                plat_list.append(i["Source"])
        data = {_id["platId"]: _id["platName"]
                for _id in all_plat if _id["platId"] in plat_list}
        return data

    @staticmethod
    def task_list(cc_biz_id):
        res = client.job.get_task(app_id=cc_biz_id)
        if res.get("result"):
            return res["data"]

        logger.error(u"获取ijob任务列表失败：[cc_biz_id: %s]" % cc_biz_id)
        return []

    @staticmethod
    def task_detail(cc_biz_id, task_id):
        res = client.job.get_task_detail(app_id=cc_biz_id, task_id=task_id)
        if res.get("result"):
            return res["data"]

        logger.error(
            u"获取ijob任务详细信息失败：[cc_biz_id: %s][task_id: %s]" %
            (cc_biz_id, task_id)
        )
        return {}


@web_cache(60*10)
def get_owner_info():
    return client.bk_login.get_all_user()['data'] or []


@web_cache(60)
def get_nick_by_uin(uin_list, show_detail=False):
    if not uin_list:
        return {}
    if not hasattr(uin_list, "__iter__"):
        if "," in uin_list:
            uin_list = uin_list.split(",")
        else:
            uin_list = [uin_list]

    user_info = CCBiz.user_info()
    logger.info(user_info)
    result = {}.fromkeys(uin_list)
    for uin in uin_list:
        if uin:
            if uin in user_info:
                result[uin] = (u"%s(%s)" % (user_info[uin], uin)
                               if show_detail else user_info[uin])
            else:
                result[uin] = uin
    return result
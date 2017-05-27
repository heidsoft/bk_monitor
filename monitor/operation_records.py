# -*- coding: utf-8 -*-
import json
import threading

from common.log import logger
from common.mymako import DictObj
from utils.common_utils import ignored
from utils.query_cc import get_nick_by_uin
from utils.request_middlewares import get_request
from monitor.models import (AlarmDef, DataCollector, DataGenerateConfig,
                            Monitor, MonitorCondition, MonitorConditionConfig,
                            MonitorLocation, OperateRecord, ScenarioMenu)

# 定义需要记录的model
MODELS_TO_LOG = (DataCollector, DataGenerateConfig, AlarmDef,
                 Monitor, MonitorCondition, MonitorConditionConfig,
                 ScenarioMenu, MonitorLocation)

def pre_save_models(sender, instance, **kwargs):
    if isinstance(instance, MODELS_TO_LOG):
        if (not hasattr(instance, 'id')) or instance.id < 1:
            return
        with ignored(Exception):
            before_save_obj = instance
            # 如果是alarm_def 则比较麻烦， 需要在pre_save的时候把收敛，处理，通知
            if isinstance(instance, AlarmDef):
                from monitor.models import AlarmStrategy
                try:
                    converge = instance.converge
                except:
                    converge = False
                if converge:
                    setattr(
                        before_save_obj,
                        'converge_string',
                        AlarmStrategy.gen_converge_str(instance.converge)
                    )
                else:
                    setattr(before_save_obj, 'converge_string', u'无')

                notify_way = []
                try:
                    notify = json.loads(instance.notify)
                    for key in notify:
                        if 'notify_' in key:
                            notify_way.append(key.replace('notify_', ''))
                except:
                    notify = {}
                setattr(
                    before_save_obj,
                    'notify_string',
                    AlarmStrategy.gen_notify_final_str(notify_way, notify)
                )

            before_save_obj = serialize_object(before_save_obj)
            request = get_request()
            # 把保存前的信息存入session
            if not request.session.get('model_operation_cache', False):
                request.session['model_operation_cache'] = {}
            key = "%s_%s" % (sender.__name__, instance.id)
            request.session['model_operation_cache'][key] = before_save_obj


def post_save_models(sender, instance, created, **kwargs):
    if isinstance(instance, MODELS_TO_LOG):
        change_type = 'create' if created else 'update'
        t = threading.Thread(target=save_change_log, args=(sender, change_type, instance))
        t.start()
        # save_change_log(sender, change_type, instance)


def post_delete_models(sender, instance, **kwargs):
    if isinstance(instance, MODELS_TO_LOG):
        change_type = 'delete'
        t = threading.Thread(target=save_change_log, args=(sender, change_type, instance))
        t.start()
        # save_change_log(sender, change_type, instance)


def save_change_log(sender, change_type, instance):
    # 判断是否为软删除
    if hasattr(instance, 'is_deleted') and instance.is_deleted == 1:
        change_type = 'delete'

    change_model = unicode(sender.__name__)
    data = serialize_object(instance)
    ori_data = '[{}]'
    request = get_request()
    if change_type == 'update':
        # 把session中保存的信息取出来
        if not request.session.get('model_operation_cache', False):
            request.session['model_operation_cache'] = {}
        key = "%s_%s" % (sender.__name__, instance.id)
        try:
            ori_data = request.session['model_operation_cache'].get(key, {})
        except:
            ori_data = '[{}]'
    try:
        username = request.user.username
        user_nick = get_nick_by_uin(username).get(username, username)
    except:
        username = "*SYSTEM*"   # celery backend process
        user_nick = u'系统'

    # 获取biz_id
    if hasattr(instance, 'biz_id'):
        biz_id = instance.biz_id
    elif hasattr(instance, 'alarm_def_id'):
        try:
            alarm_def = AlarmDef.objects.get(id=instance.alarm_def_id)
            biz_id = alarm_def.biz_id
        except:
            biz_id = 0
    elif hasattr(instance, 'monitor_id'):
        try:
            monitor = Monitor.objects.get(id=instance.monitor_id)
            biz_id = monitor.biz_id
        except:
            biz_id = 0
    elif hasattr(instance, 'monitor_item_id'):
        try:
            monitor_item = MonitorCondition.objects.get(
                id=instance.monitor_item_id
            )
            alarm_def = monitor_item.alarm_def
            biz_id = alarm_def.biz_id
        except:
            biz_id = 0
    else:
        biz_id = 0

    if not biz_id:
        biz_id = 0

    try:
        OperateRecord.objects.create(
            config_type=change_model,
            config_id=instance.id,
            operate=change_type,
            operator=username,
            data=data,
            data_ori=ori_data,
            biz_id=biz_id,
            operator_name=user_nick
        )
    except Exception, e:
        logger.error(u'save operation log error! %s' % e)


def serialize_object(object):
    class_name = object.__class__.__name__
    module = object.__class__.__module__
    info = object.__dict__
    return json.dumps({"class": class_name, "module": module, "info": info}, cls=IgnoreForeignKeyEncoder)


class IgnoreForeignKeyEncoder(json.JSONEncoder):
    def default(self, obj):
        if issubclass(obj.__class__, DictObj):
            return ""
        return json.JSONEncoder.default(self, obj)


def unserialize_object(string_content):
    json_info = json.loads(string_content)
    class_name = json_info.get("class", "")
    module_name = json_info.get("module", "")
    info = json_info.get("info", {})
    module = __import__(
        module_name, globals(), {}, [module_name.split('.')[-1]]
    )
    obj = getattr(module, class_name)(info)
    return obj

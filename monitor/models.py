# -*- coding: utf-8 -*-

import json
import re
import uuid

from django.conf import settings
from django.db import models, transaction
from monitor.performance.solutions import SolutionConf

from utils.request_middlewares import get_request
from account.models import BkUser
from common.log import logger
from monitor.constants import (ALARM_LEVEL_COLOR, NOTIRY_MAN_DICT,
                               NOTIRY_MAN_STR_DICT, NOTIRY_WAY_DICT,
                               NOTIRY_WAY_DICT_NEW, NOTIRY_WAY_NAME_DICT,
                               STRATEGY_CHOICES)
from monitor.errors import JAItemDoseNotExists
from monitor.performance.models import (AlarmDef, AlarmInstance, BaseHostIndex,
                                        HostIndex, Monitor, MonitorCondition,
                                        MonitorConditionConfig, ShieldApi,
                                        AlarmConvergeConfig, set_rel,
                                        AlarmNoticeConfig)
from utils.common_utils import (base_hostindex_id_to_page_id, check_permission,
                                failed, ignored, ok, ok_data, parse_host_id,
                                safe_int)
from utils.query_cc import CCBiz, get_nick_by_uin
from utils.cache import lazy_property
from monitor.datasource.models import Datasource, AgentStatus


class OperateManager(models.Manager):

    def all(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(OperateManager, self).filter(is_deleted=False)

    def filter(self, *args, **kwargs):
        # 默认都不显示被标记为删除的告警定义
        return super(OperateManager, self)\
            .filter(*args, **kwargs).filter(is_deleted=False)


class OperateRecordModel(models.Model):

    objects = OperateManager()
    origin_object = models.Manager()

    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    create_user = models.CharField(u"创建人", max_length=32)
    update_time = models.DateTimeField(u"修改时间", auto_now=True)
    update_user = models.CharField(u"修改人", max_length=32)
    is_deleted = models.BooleanField(u"是否删除", default=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        request = get_request()
        username = request.user.username
        if self.pk is None:
            self.create_user = username
        self.update_user = username
        return super(OperateRecordModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        删除方法，不会删除数据
        而是通过标记删除字段 is_deleted 来软删除
        """
        self.is_deleted = True
        if hasattr(self, "is_enabled"):
            self.is_enabled = False
        self.save()

    @property
    def show_update_time(self):
        return self.update_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_title(self):
        return ''

    def gen_operate_desc(self, operate, ori_data=False):
        """
        根据操作类型，与变更前后的配置生成操作说明
        :param operate: 操作类型：create/update/delete
        :param ori_data: 操作前的配置信息 [可选]
        :return: operate_desc 变更说明
        """
        op_desc = self.get_title()
        if operate in ['create', 'delete']:
            return op_desc
        elif operate == 'update':
            if not ori_data:
                return op_desc
            # 获得2次修改之间， 变更了哪些配置
            changed_config = self.get_operate_changed_config(ori_data)
            # 根据变更的配置， 生成对应的wording
            op_desc = self.gen_op_desc_by_changed_config(changed_config)
        return op_desc

    def get_operate_changed_config(self, ori_data):
        return {}

    def gen_op_desc_by_changed_config(self, changed):
        return self.get_title()


class OperateRecord(models.Model):

    biz_id = models.IntegerField(u"业务cc_id", default=0)
    config_type = models.CharField(u"配置类型", max_length=32)
    config_id = models.IntegerField(u"操作config_id")
    config_title = models.CharField(u"配置标题", default="", max_length=512)
    operator = models.CharField(u"操作人", max_length=32)
    operator_name = models.CharField(u"操作人昵称", default="", max_length=32)
    operate = models.CharField(u"具体操作", max_length=32)
    operate_time = models.DateTimeField(u"操作时间", auto_now_add=True)
    data = models.TextField(u"数据(JSON)")
    data_ori = models.TextField(u"修改前数据(JSON)", default='{}')
    operate_desc = models.TextField(u"操作说明", default='')

    class Meta:
        verbose_name = u"操作记录"
        verbose_name_plural = u"操作记录"

    def gen_operate_desc(self):
        # 准备数据
        from monitor.operation_records import unserialize_object
        try:
            config_obj = unserialize_object(self.data)
            if not config_obj:
                self.operate_desc = ''
                self.config_title = ''
                return False
        except Exception, e:
            # 信息解析失败， 无法生成操作说明
            self.operate_desc = ''
            self.config_title = ''
            return False

        self.config_title = config_obj.get_title()
        if self.operate in ['create', 'delete']:
            self.operate_desc = config_obj.gen_operate_desc(self.operate)
        elif self.operate == 'update':
            # 准备修改前数据
            try:
                from monitor.operation_records import unserialize_object
                config_ori_obj = unserialize_object(self.data_ori)
                if not config_ori_obj:
                    self.operate_desc = ''
                    return False
            except Exception, e:
                self.operate_desc = ''
                return False
            self.operate_desc = config_obj.gen_operate_desc(self.operate, config_ori_obj)
        else:
            self.operate_desc = ''
        return True

    def save(self, *args, **kwargs):
        # 如果是update， 则保存原始值
        try:
            self.gen_operate_desc()
        except Exception, e:
            logger.exception(u'saving operate record fail: gen operate desc fail %s' % e)
        return super(OperateRecord, self).save()

    @staticmethod
    def update_chname(data_list):
        """
        获取中文名
        :param data_list:
        :return:
        """
        username_list = [data['operator'] for data in data_list]
        user_dict = BkUser.get_chname_by_username(set(username_list))
        for data in data_list:
            if data['operator_name'] == data['operator']:
                user_nick = user_dict.get(data['operator'], data['operator'])
                if user_nick == data['operator_name']:
                    user_nick = get_nick_by_uin(data['operator_name']).get(user_nick)
                data['operator_name'] = user_nick

    @staticmethod
    def build_operate_record_data(data_queryset, page, page_size=10):
        """组装操作流水列表数据

        :param data_queryset:
        :param page: page为0表示不分页，返回全部数据
        :param page_size:
        :return:
        """
        if page == 0:
            return list(data_queryset)
        else:
            start = (page - 1) * page_size
            end = start + page_size
            return list(data_queryset[start: end])


class DataGenerateConfig(OperateRecordModel):

    """
        记录数据处理过程
        biz_id: 业务
        collector_id: 采集表id
        template_id: 模板id
        template_args: 模版参数
        project_id: 子项目ID
        job_id: 对应的作业ID
    """

    STATUS_CHOICES = (
        ("starting", u"启动中"),
        ("running", u"正在运行"),
        ("stopping", u"停止中"),
        ("not running", u"未启动"),
    )

    biz_id = models.IntegerField(u"业务ID")
    collector_id = models.IntegerField(u"关联数据接入配置")
    template_id = models.IntegerField(u"模版ID")
    template_args = models.TextField(u"模版参数")
    project_id = models.IntegerField(u"子项目ID")
    job_id = models.CharField(u"对应的作业ID", max_length=32)
    bksql = models.TextField(u"bksql描述", default="")
    status = models.CharField(u"作业状态", max_length=16, default="starting",
                              choices=STATUS_CHOICES)


class DataCollector(OperateRecordModel):
    """
        记录通过监控系统接入的数据来源及配置信息
        biz_id: 业务
        source_type: 数据库 / log / msdk / tqos
        collector_config: 采集数据需要用到的配置信息
        data_set: 数据基简称
        data_id: 数据id
        data_description: 数据描述
        data_type: 数据类型 在线==
    """
    biz_id = models.IntegerField(u"业务ID")
    source_type = models.CharField(u"数据源类型", max_length=32)
    collector_config = models.TextField(u"数据接入配置信息")
    data_id = models.IntegerField(u"下发data id")
    data_type = models.CharField(u"数据类型", max_length=32)
    data_set = models.CharField(u"db_name+table_name", max_length=32)
    data_description = models.TextField(u"数据描述", null=True)


class DataResultTableField(models.Model):
    """result table fields"""
    result_table_id = models.CharField(u"result table id", max_length=64)
    monitor_id = models.IntegerField(u"monitor id", default=0)
    generate_config_id = models.IntegerField(u"关联的data etl config id", default=0)
    field = models.CharField(u"field name", max_length=32)
    desc = models.CharField(u"中文名称", max_length=32, blank=True, null=True)
    field_type = models.CharField(u"field type", max_length=16)
    processor = models.CharField(u"processor", max_length=32, null=True)
    processor_args = models.TextField(null=True)
    is_dimension = models.BooleanField(u"是否维度字段", default=False)
    origins = models.CharField(u"origins list", max_length=64, null=True)
    field_index = models.IntegerField(u"index")
    value_dict = models.TextField(u"值映射(JSON)", null=True, blank=True)

    @property
    def alias_name(self):
        return self.desc


class DataResultTable(models.Model):
    """data counter 表信息"""
    result_table_id = models.CharField(u"result table id", max_length=64, primary_key=True)
    monitor_id = models.IntegerField(u"monitor id", default=0)
    biz_id = models.IntegerField(u"业务ID")
    table_name = models.TextField(u"表名称")
    generate_config_id = models.IntegerField(u"关联的data etl config id", primary_key=True)
    count_freq = models.IntegerField(u"统计频率")
    parents = models.CharField(u"父表id list", max_length=128, null=True)

    @property
    def generate_config(self):
        if self.generate_config_id:
            return DataGenerateConfig.objects.get(id=self.generate_config_id)


class MonitorHostStickyManager(models.Manager):

    def host_is_stickied(self, host_id):
        """
        主机是否置顶，未置顶返回0，置顶返回置顶记录id
        """
        ip, plat_id = host_id.split("|")
        q_set = self.filter(host=ip, plat_id=plat_id)
        if q_set.exists():
            row = q_set[0]
            return row.id
        return 0


class MonitorHostSticky (models.Model):
    """
    主机基础性能列表置顶信息
    """
    plat_id = models.IntegerField(u"平台ID", null=True)
    host = models.CharField(u"主机IP",max_length=128, null=True, db_index=True)
    cc_biz_id = models.CharField(u"cc业务id", max_length=30)

    objects = MonitorHostStickyManager()


class CallMethodRecord(models.Model):
    # 接口调用记录
    action = models.CharField(u"调用接口名", max_length=512)
    url = models.CharField(u"url", max_length=256)
    method = models.CharField(u"http方法", max_length=10, default="")
    param = models.TextField(u"参数")
    result = models.TextField(u"返回结果")
    operate_time = models.DateTimeField(u"操作时间", auto_now_add=True)


class AlarmStrategyManager(models.Manager):

    def get_strategy_by_host_id(self, host_id, cc_biz_id):
        """
        根据host_id获取该up机器关联的告警策略列表。
        :param host_id:
        :return:
        """
        ip, plat_id = parse_host_id(host_id)
        include_mods = []
        include_sets = []
        # step 1: 获取该主机详细模块信息和大区信息
        host_info_list = CCBiz.host_detail(cc_biz_id, ip, plat_id)
        strategy_list = []
        if not host_info_list:
            return strategy_list
        for host_info in host_info_list:
            include_mods.append(host_info['ModuleID'])
            include_sets.append(host_info['SetID'])
        if not any((include_mods, include_sets,)):
            return strategy_list
        # step 2: 取出业务下所有基础性能监控策略monitor_item
        performance_monitor = Monitor.get_active_performance_monitors(cc_biz_id)
        performance_monitor_id_list = [m.id for m in performance_monitor]
        if not performance_monitor_id_list:
            return strategy_list
        performance_monitor_items = MonitorCondition.objects.filter(
            monitor_id__in=",".join(map(str, performance_monitor_id_list)))
        s_id = self.model.create_s_id()
        hit_monitor_item_list = []
        for monitor_item in performance_monitor_items:
            condition = monitor_item.condition_dict
            # 大区模块全选，condition为空字典
            if not condition:
                hit_monitor_item_list.append(monitor_item)
                continue
            hit = False
            # 静态ip策略
            ip_range_str = condition.get('ip')
            if ip_range_str:
                if ip in ip_range_str.split(","):
                    hit = True
            else:
                # 动态模块，大区配置策略（and）关系
                cc_module = condition.get("cc_app_module")
                cc_set = condition.get("cc_topo_set")
                strategy_mod_list = (cc_module.split(",")
                                     if cc_module else include_mods)
                strategy_set_list = (cc_set.split(",")
                                     if cc_set else include_sets)
                # 检查主机所在的模块，大区是否匹配策略
                if (any(mod in strategy_mod_list for mod in include_mods) and
                        any(_s in strategy_set_list for _s in include_sets)):
                    hit = True
            if hit:
                hit_monitor_item_list.append(monitor_item)
        if not hit_monitor_item_list:
            return []
        alarm_def_id_range_str = ",".join([str(mm.alarm_def_id) for mm in hit_monitor_item_list])
        alarm_defs = AlarmDef.objects.filter(id__in=alarm_def_id_range_str)
        set_rel(alarm_defs, AlarmNoticeConfig, "alarm_notice_config", "alarm_notice_id", "id")
        set_rel(alarm_defs, AlarmConvergeConfig, "converge", "id", "alarm_source_id", lambda x: x.config if x else '{}')
        set_rel(hit_monitor_item_list, performance_monitor, "_monitor", "monitor_id", "id")
        set_rel(hit_monitor_item_list, alarm_defs, "alarm_def", "alarm_def_id", "id")
        set_rel(hit_monitor_item_list, MonitorConditionConfig, "condition_config", "id", "monitor_item_id")
        for monitor_item in hit_monitor_item_list:
            strategy = self.model.get_by_monitor_item(monitor_item, s_id, monitor_item._monitor)
            strategy_list.append(strategy)
        strategy_list = set_rel(strategy_list, performance_monitor, "monitor", "monitor_id", "id")
        strategy_list = sorted(strategy_list, key=lambda x: x.update_time, reverse=True)
        return strategy_list

    def get_alarm_strategy_info(self, strategy_id_or_obj):
        # 获取告警策略信息
        with ignored(AlarmStrategy.DoesNotExist):
            if isinstance(strategy_id_or_obj, AlarmStrategy):
                strategy = strategy_id_or_obj
            else:
                strategy = AlarmStrategy.objects.get(id=strategy_id_or_obj)

            strategy_desc = "%s<br>%s" % (
                strategy.strategy_desc, strategy.condition_str)
            if strategy.scenario == "base_alarm":
                strategy_desc = strategy.condition_str
            strategy_show_str = (
                (strategy_desc[0:50] + '...')
                if len(strategy_desc) > 50 else strategy_desc
            )
            enabled_html = u"<span class='text-success'>"u"已启用</span>" \
                if strategy.is_enabled \
                else u"<span class='text-danger'>未启用</span>"
            strategy_info = {
                'id': strategy.id,
                'strategy_name': strategy.strategy_name,
                'strategy_desc': strategy_desc,
                'strategy_show_str': strategy_show_str,
                'monitor_level_name': strategy.get_monitor_level_display(),
                'monitor_level_color': strategy.monitor_level_color,
                'scenario': strategy.scenario,
                'is_enabled': strategy.is_enabled,
                'is_enabled_str': enabled_html,
                # # monitor
                'monitor_id': strategy.monitor.id,
                'monitor_field': strategy.monitor.monitor_field_show_name,
                # solution
                'solution_name': strategy.solution_name
            }
            return strategy_info

    def handle_strategy_list(self, cc_biz_id, s_id, alrm_strategys):
        """
        将AlarmStrategy 表中的数据处理为 kendo 渲染的js
        """
        strategy_list = []
        for strategy in alrm_strategys:
            solution_name = strategy.solution_name
            strategy_desc = "%s<br>%s" % (
                strategy.strategy_desc, strategy.condition_str)
            if strategy.scenario == "base_alarm":
                strategy_desc = strategy.condition_str
            strategy_show_str = (strategy_desc[0:50]+'...'
                                 if len(strategy_desc) > 50
                                 else strategy_desc)

            # 通知人
            role_list = strategy.role_list
            # 根据通知角色获取通知人的展示方式
            notify_man_html = self.model.get_notify_html_by_role(cc_biz_id, role_list)
            # 额外通知人
            if strategy.responsible:
                responsible_str_format = NOTIRY_MAN_STR_DICT.get('responsible')
                responsible_str = responsible_str_format % "; ".join(get_nick_by_uin(strategy.responsible, show_detail=True).values())
                notify_man_html += responsible_str

            strategy_list.append({
                's_id': str(s_id),
                'id': strategy.id,
                'display_name': strategy.display_name if strategy.display_name else strategy.strategy_name,
                'strategy_name': strategy.strategy_name,
                'strategy_desc': strategy_desc,
                'strategy_show_str': strategy_show_str,
                'monitor_level_name': strategy.get_monitor_level_display(),
                'monitor_level_color': strategy.monitor_level_color,
                'solution_name': solution_name,
                'notify_way_str': self.model.gen_notify_way_str(strategy.notify_way),
                'scenario': strategy.scenario,
                'is_enabled': strategy.is_enabled,
                'is_enabled_str': u"<span class='text-success'>已启用</span>" if strategy.is_enabled else u"<span class='text-danger'>未启用</span>",
                # 通知人
                'notify_man_html': notify_man_html,
                'alarm_def_id': strategy.alarm_def_id,
            })
        return strategy_list

    def update_config_by_strategy_data(self, strategy_id, strategy_data, monitor):
        try:
            if strategy_id == 0:
            # create
                alarm_strategy = self.model(**strategy_data)
                alarm_strategy.save()
                if monitor:
                    self.create_config_by_strategy(alarm_strategy, monitor)
                return {'result': True, 'message': u"保存成功"}
            # update
            with transaction.atomic():
                alarm_strategy = self.filter(id=strategy_id)
                alarm_strategy.update(**strategy_data)
                if monitor:
                    alarm_strategy = alarm_strategy[0]
                    alarm_source = AlarmDef.objects.get(id=alarm_strategy.alarm_def_id)
                    alarm_strategy._alarm_def = alarm_source
                    alarm_strategy._alarm_def = alarm_source.update(**alarm_strategy.gen_alarm_sources_config(monitor))
                    monitor_item = MonitorCondition.objects.get(id=alarm_strategy.condition_id)
                    alarm_strategy._monitor_item = monitor_item
                    alarm_strategy._monitor_item = monitor_item.update(**alarm_strategy.gen_monitor_items_config(monitor))
                    condition_config = MonitorConditionConfig.objects.get(id=alarm_strategy.condition_config_id).update(**alarm_strategy.gen_detect_algorithm_config(monitor_item))
            return {'result': True, 'message': u"保存成功"}
        except Exception as e:
            logger.exception(u"新建告警策略临时表失败:%s" % e)
            return {'result': False, 'message': u"保存出错"}

    def create_config_by_strategy(self, strategy_obj, monitor):
        strategy_obj.monitor = monitor
        strategy_obj.monitor_id = monitor.id
        alarm_source = AlarmDef.create(strategy_obj, monitor)
        strategy_obj.alarm_def_id = alarm_source.id
        strategy_obj._alarm_def = alarm_source
        monitor_item = MonitorCondition.create(strategy_obj, monitor)
        strategy_obj.condition_id = monitor_item.id
        strategy_obj._monitor_item = monitor_item
        condition_config = MonitorConditionConfig.create(strategy_obj, monitor_item)
        strategy_obj.condition_config_id = condition_config.id
        strategy_obj.save()

class AlarmStrategy(models.Model):

    cc_biz_id = models.CharField(u"cc业务id", max_length=30)
    s_id = models.CharField(u"关联Moniter表的id", max_length=50)
    monitor_level = models.CharField(u"告警级别", max_length=10,
                                     choices=AlarmInstance.ALARM_LEVEL)
    monitor_name = models.CharField(u"监控名称", max_length=32, default="")
    condition = models.TextField(u"筛选条件", null=True, blank=True)
    strategy_id = models.CharField(u"算法id", max_length=10)
    strategy_option = models.TextField(u"算法参数")
    monitor_config = models.TextField(u"通知参数", help_text=u"该字段废弃，不再使用")
    rules = models.TextField(u"收敛规则")
    display_name = models.CharField(u"策略名称", max_length=50, default="")
    responsible = models.TextField(u"额外通知人", null=True, blank=True, default='')
    solution_id = models.CharField(u"自愈套餐id", max_length=30,
                                   null=True, blank=True, default='')
    notify_way = models.TextField(u"通知方式")
    role_list = models.TextField(u"通知人角色")
    prform_cate = models.CharField(u"基础性能配置", max_length=30,
                                   null=True, blank=True, default='')
    ip = models.TextField(u"IP", null=True, blank=True, default='')
    plat_id = models.TextField(u"平台", null=True, blank=True, default='')
    cc_module = models.TextField(u"模块", null=True, blank=True, default='')
    cc_set = models.TextField(u"SET", null=True, blank=True, default='')
    notify = models.TextField(u"通知配置", default='{}')
    creator = models.CharField(u"创建者", max_length=30)
    updator = models.CharField(u"更新者", max_length=30)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)
    nodata_alarm = models.IntegerField(u"无数据告警(连续多少周期)", default=0)
    monitor_id = models.IntegerField(null=True)
    condition_id = models.IntegerField(null=True)
    condition_config_id = models.IntegerField(null=True)
    alarm_def_id = models.IntegerField(null=True)
    is_enabled = models.BooleanField(u"是否启用", default=True)
    scenario = models.CharField(u"监控场景", default="custom", max_length=32)
    alarm_solution_config = models.TextField(u"自动处理配置", default='{}')

    objects = AlarmStrategyManager()

    def __uincode__(self):
        return self.s_id

    class Meta:
        verbose_name = u"告警策略临时表"

    @staticmethod
    def create_s_id():
        return uuid.uuid4()

    @classmethod
    def get_by_monitor_id(cls, monitor_id):
        # request = get_request()
        # username = request.user.username
        if isinstance(monitor_id, Monitor):
            monitor = monitor_id
        else:
            monitor = Monitor.objects.get(id=monitor_id)
        alarm_strategys = []
        cur_s_id = cls.create_s_id()
        set_rel(monitor.condition_list, AlarmDef, "alarm_def", "alarm_def_id", "id")
        alarm_defs = [mm.alarm_def for mm in monitor.condition_list]
        set_rel(alarm_defs, AlarmNoticeConfig, "alarm_notice_config", "alarm_notice_id", "id")
        set_rel(alarm_defs, AlarmConvergeConfig, "converge", "id", "alarm_source_id", lambda x: x.config if x else '{}')
        set_rel(monitor.condition_list, MonitorConditionConfig, "condition_config", "id", "monitor_item_id")
        for monitor_item in monitor.condition_list:
            alarm_strategy = cls.get_by_monitor_item(monitor_item, cur_s_id, monitor)
            if alarm_strategy:
                alarm_strategys.append(alarm_strategy)
        return cur_s_id, alarm_strategys

    @classmethod
    def get_by_monitor_item(cls, monitor_item, s_id="", monitor=None):
        if not s_id:
            s_id = cls.create_s_id()
        if not monitor:
            monitor = Monitor.objects.get(id=monitor_item.monitor_id)
        try:
            condition_config = monitor_item.condition_config
            alarm_source = monitor_item.alarm_def
            notify_dict = alarm_source.notify_dict
        except JAItemDoseNotExists, e:
            logger.error(u"获取告警策略失败：%s" % e)
            return None
        alarm_strategy = AlarmStrategy.objects.create(
            monitor_name=monitor.monitor_name,
            cc_biz_id=monitor.biz_id,
            s_id=s_id,
            scenario=monitor.scenario,
            monitor_level=str(alarm_source.monitor_level),
            condition=monitor_item.condition,
            strategy_id=condition_config.algorithm_id,
            strategy_option=condition_config.strategy_option,
            rules=alarm_source.converge,
            display_name=alarm_source.title,
            is_enabled=alarm_source.is_enabled,
            responsible=notify_dict.get("responsible") or "",
            solution_id=0,
            notify_way=cls.get_notify_way_from_alarm_def(
                notify_dict),
            role_list=json.dumps(
                (notify_dict.get("role_list") or []) + (notify_dict.get("group_list") or [])),
            notify=alarm_source.notify,
            nodata_alarm=json.loads(monitor_item.is_none_option).get("continuous", 0),
            creator="sys",
            updator="sys",

            monitor_id=monitor.id,
            condition_id=monitor_item.id,
            condition_config_id=condition_config.id,
            alarm_def_id=alarm_source.id,
            alarm_solution_config=(alarm_source.alarm_solution_config or '{}'),
        )
        if monitor.scenario in ["performance", "base_alarm"]:
            ip = monitor_item.condition_dict.get("ip")
            cc_module = monitor_item.condition_dict.get("cc_app_module")
            cc_set = monitor_item.condition_dict.get("cc_topo_set")
            plat_id = monitor_item.condition_dict.get("plat_id")
            if ip:
                alarm_strategy.prform_cate = "ip"
                if isinstance(ip, list):
                    ip = ",".join(ip)
                alarm_strategy.ip = ip
                alarm_strategy.plat_id = plat_id
            else:
                alarm_strategy.cc_module = cc_module
                alarm_strategy.cc_set = cc_set
                alarm_strategy.prform_cate = "set"
            alarm_strategy.save()
        return alarm_strategy

    @staticmethod
    def get_notify_way_from_alarm_def(notify_dict):
        result = []
        for method in ["mail", "wechat", "sms", "im", "phone"]:
            for status in ["begin_", "success_", "failure_", ""]:
                if notify_dict.get("%snotify_%s" % (status, method)):
                    result.append(method)
                    break
        return json.dumps(result)

    @property
    def monitor(self):
        @lazy_property()
        def _monitor(self):
            return Monitor.objects.get(id=self.monitor_id)
        return _monitor(self)

    @monitor.setter
    def monitor(self, val):
        cache_key = lazy_property.gen_cache_key(self, "_monitor")
        # 设置缓存
        setattr(self, cache_key, val)

    @property
    def strategy_desc(self):
        return self.gen_strategy_desc(self.strategy_id, self.strategy_option)

    @property
    def solution_name(self):
        solution_name = u"不处理，仅通知"
        alarm_solution_config = self.alarm_solution_config
        with ignored(Exception):
            alarm_solution_config = json.loads(self.alarm_solution_config)
        if alarm_solution_config:
            try:
                solution_is_enable = alarm_solution_config["is_enabled"]
                solution_type = alarm_solution_config["solution_type"]
                solution_config = json.loads(alarm_solution_config["config"])
                solution_task_id = solution_config["job_task_id"]
            except KeyError as e:
                logger.warning(u"alarm_solution_config 配置格式出错，缺少key: %s" % e)
                return solution_name
            if solution_is_enable and solution_task_id:
                solution_name = (
                    u"【%s】%s" % (
                        SolutionConf.solution_type_display_name(
                            solution_type
                        ),
                        solution_config['job_task_name'])
                )
        return solution_name

    @staticmethod
    def gen_strategy_desc(strategy_id, option):
        try:
            strategy_id = "%s" % strategy_id
            if type(option) is not dict:
                strategy_option = json.loads(option)
            else:
                strategy_option = option
        except:
            strategy_option = {}
            logger.exception(u"算法参数格式错误")

        if strategy_id == "1000":
            method_dict = {
                u"eq": u"=",
                u"gte": u"≥",
                u"gt": u">",
                u"lt": u"<",
                u"lte": u"≤",
            }
            return u"当前值%s阈值:%s" % (method_dict.get(strategy_option.get('method', 'eq')), strategy_option.get('threshold', ''))
        if strategy_id in ["1001", "1002", "1003", "1004"]:
            span_html = u' <span class="strategy_desc"> 或</span>  '
            desc = u"指标当前值"
            if strategy_id in ["1001"]:
                desc += u"较上周同一时刻值"
                if strategy_option.get('ceil', ''):
                    desc += u"上升%s%%" % strategy_option.get('ceil', '')
                    if strategy_option.get('floor', ''):
                        desc += span_html
                if strategy_option.get('floor', ''):
                    desc += u"下降%s%%" % strategy_option.get('floor', '')
            if strategy_id in ["1002"]:
                desc += u"较前一时刻值"
                if strategy_option.get('ceil', ''):
                    desc += u"上升%s%%" % strategy_option.get('ceil', '')
                    if strategy_option.get('floor', ''):
                        desc += span_html
                if strategy_option.get('floor', ''):
                    desc += u"下降%s%%" % strategy_option.get('floor', '')
            if strategy_id in ["1003"]:
                if strategy_option.get('ceil', ''):
                    desc += u"较%s天内同一时刻绝对值的均值" % strategy_option.get('ceil_interval', '')
                    desc += u"上升%s%%" % strategy_option.get('ceil', '')
                    if strategy_option.get('floor', ''):
                        desc += span_html
                if strategy_option.get('floor', ''):
                    desc += u"较%s天内同一时刻绝对值的均值" % strategy_option.get('floor_interval', '')
                    desc += u"下降%s%%" % strategy_option.get('floor', '')
            if strategy_id in ["1004"]:
                if strategy_option.get('ceil', ''):
                    desc += u"较%s个时间点的均值" % strategy_option.get('ceil_interval', '')
                    desc += u" 上升%s%%" % strategy_option.get('ceil', '')
                    if strategy_option.get('floor', ''):
                        desc += span_html
                if strategy_option.get('floor', ''):
                    desc += u"较%s个时间点的均值" % strategy_option.get('floor_interval', '')
                    desc += u" 下降%s%%" % strategy_option.get('floor', '')
            return desc
        return u"默认参数"

    @property
    def converge_str(self):
        return self.gen_converge_str(self.rules)

    @staticmethod
    def gen_converge_str(rules):
        CONVERGE_DESC = {
            "0": u"系统默认",
            "2": u"自第{count}次告警后{continuous}内不再发出告警",
            "1": u"{continuous}内，满足{count}次告警条件时，才触发告警"
        }
        converge_dict = json.loads(rules)
        converge_id = converge_dict.get("converge_id", '0')
        continuous = safe_int(converge_dict.get("continuous", 5))
        count = safe_int(converge_dict.get("count", 1), 1)
        if continuous > 60:
            continuous = u"%s小时" % (continuous / 60)
        else:
            continuous = u"%s分钟" % continuous
        return CONVERGE_DESC.get(str(converge_id), "0").format(count=count, continuous=continuous)

    @property
    def condition_str(self):
        return self.gen_condition_str(self.condition, self.cc_biz_id, self.scenario, self.prform_cate,
                                      self.ip, self.cc_set, self.cc_module)

    @staticmethod
    def gen_condition_str(condition_value, cc_biz_id="", scenario="", prform_cate="", ip="", cc_set="", cc_module=""):
        condition = condition_value
        expr_display = {
            'eq': u"等于",
            'gte': u"大于",
            'lte': u"小于",
            'reg': u"正则"
        }
        try:
            if type(condition) is not dict:
                condition = json.loads(condition)
            con_str_list = []
            # 基础性能监控 显示 ip,set,module
            if scenario in ["performance", "base_alarm"]:
                if prform_cate == "ip":
                    con_str_list.append('IP: %s' % ip)
                elif prform_cate == 'set':
                    if cc_set:
                        cc_set_list = cc_set.split(",")
                        cc_set_info = CCBiz.set_name(cc_biz_id, cc_set_list)
                        cc_set_display = ",".join([cc_set_info[c] for c in cc_set_list])
                    else:
                        cc_set_display = u"全部"
                    con_str_list.append(u'集群: %s' % cc_set_display)
                    if cc_module:
                        cc_module_list = cc_module.split(",")
                        cc_module_info = CCBiz.module_name(cc_biz_id, cc_module_list)
                        cc_module_display = ",".join([cc_module_info[c] for c in cc_module_list])
                    else:
                        cc_module_display = u"全部"
                    con_str_list.append(u'模块: %s' % cc_module_display)
            else:
                if isinstance(condition[0], dict):
                    condition = [condition]
                for con_list in condition:
                    if con_list:
                        sub_con_str_list = []
                        for con in con_list:
                            method = con.get('method', '')
                            expr_str = expr_display.get(method, method)
                            val = con.get('value', '')
                            if isinstance(val, list):
                                val = ",".join(map(str, val))
                            con_str = "%s %s %s" % (con.get('field', ''),
                                                    expr_str, val)
                            sub_con_str_list.append(con_str)
                        con_str_list.append("(" + ' and '.join(sub_con_str_list) + ")")
                return ' or '.join(con_str_list) if con_str_list else u"当前所有维度"
        except Exception as e:
            logger.exception(u"告警策略中筛选条件格式错误: %s" % e)
            return u"筛选条件异常"
        else:
            return '; '.join(con_str_list)

    @property
    def strategy_name(self):
        if self.scenario == "base_alarm":
            return u"-"
        return self.gen_strategy_name(self.strategy_id)

    @staticmethod
    def gen_strategy_name(strategy_id):
        strategy_id = safe_int(strategy_id)
        strategy_name = dict(STRATEGY_CHOICES).get(strategy_id, u"无")
        return strategy_name

    @classmethod
    def get_base_hostindex(cls, cc_biz_id, s_id, monitors=None):
        base_hostindex = {"text": u"基础", "children": [], "category": "base_alarm"}
        base_alarms = BaseHostIndex.objects.filter(is_enable=True)
        if not monitors:
            monitors = Monitor.objects.filter()
        children = []
        for _h in base_alarms:
            info = dict(id=base_hostindex_id_to_page_id(_h.alarm_type), item=_h.title,
                        text=_h.description, unit="")
            monitor = filter(
                lambda x: x.biz_id == cc_biz_id and
                          x.monitor_field == _h.title, monitors)
            info.update(dict(monitor_id=monitor[0].id if monitor else 0, s_id=str(s_id)))
            children.append(info)
        base_hostindex["children"] = children
        return base_hostindex

    @classmethod
    def get_host_info(cls, cc_biz_id, s_id, monitors=None):
        info_list = []
        hosts = HostIndex.objects.filter(graph_show=True)
        if not monitors:
            monitors = Monitor.objects.filter()
        for _id, desc in HostIndex.CATEGORY_CHOICES:
            # 只过滤需要展示的内容
            if _id == "process":
                continue
            category_hosts = filter(lambda x: x.category == _id, hosts)
            data = []
            for _h in category_hosts:
                info = dict(id=_h.id, item=_h.item,
                            text=_h.desc, unit=_h.unit_display)
                monitor = filter(
                    lambda x: x.biz_id == cc_biz_id and
                              x.monitor_field == _h.item and
                              x.monitor_result_table_id == _h.result_table_id,
                    monitors)
                info.update(dict(monitor_id=monitor[0].id if monitor else 0, s_id=str(s_id)))
                data.append(info)
            info_list.append({"text": desc, "children": data, "category": _id})
        return info_list

    # @classmethod
    # def get_sid(cls, cc_biz_id, monitor_field, new_sid, result_table_id=""):
    #     if result_table_id:
    #         from utils.trt import trans_bkcloud_rt_bizid
    #         monitor_result_table_id = trans_bkcloud_rt_bizid("%s_%s" % (cc_biz_id, result_table_id))
    #         monitors = Monitor.objects.filter(
    #             biz_id=cc_biz_id, monitor_field=monitor_field,
    #             monitor_result_table_id=monitor_result_table_id)
    #     else:
    #         monitors = Monitor.objects.filter(
    #             biz_id=cc_biz_id, monitor_field=monitor_field,
    #             monitor_type=monitor_field)
    #     if len(monitors) == 0:
    #         return dict(monitor_id=0, s_id=str(new_sid))
    #     if len(monitors) > 1:
    #         logger.exception(u"基础性能指标重复接入，请排查")
    #         return dict(monitor_id=0, s_id=str(new_sid))
    #     return dict(monitor_id=monitors[0].id, s_id=str(new_sid))

    @property
    def monitor_level_color(self):
        color_dict = dict(ALARM_LEVEL_COLOR)
        return color_dict.get(str(self.monitor_level), color_dict["1"])

    @property
    def notify_dict(self):
        @lazy_property()
        def _notify_dict(self):
            if self.alarm_def_id > 0:
                return AlarmDef.objects.get(id=self.alarm_def_id).notify_dict
            else:
                return json.loads(self.notify)
        return _notify_dict(self)

    @staticmethod
    def gen_notify_way_str(notify_way_value):
        notify_way_str = []
        notify_way = notify_way_value
        try:
            if type(notify_way) is not dict:
                notify_way_list = json.loads(notify_way)
            else:
                notify_way_list = notify_way
            for way in notify_way_list:
                way_str = NOTIRY_WAY_DICT.get(way, u'')
                if way_str:
                    notify_way_str.append(way_str)
        except:
            logger.exception(u"告警策略中通知方式格式错误")
            return u"通知方式异常"
        return " ".join(notify_way_str)

    @property
    def notify_way_str_v2(self):
        return self.gen_notify_way_str_v2(self.notify_way, self.notify_dict)

    @staticmethod
    def gen_notify_way_str_v2(notify_way, notify_dict):
        notify_way_str = []
        try:
            notify_way_list = json.loads(notify_way)
            for way in notify_way_list:
                way_str = NOTIRY_WAY_DICT_NEW.get(way, '')
                if way_str:
                    notify_way_str.append(way_str.format(STATIC_URL=settings.STATIC_URL))
        except:
            logger.exception(u"告警策略中通知方式格式错误")
            return u"通知方式异常"
        return " ".join(notify_way_str)

    @staticmethod
    def get_notify_html_by_role(biz_id, role_list):
        """
        根据角色列表，获取前台展示的html元素
        """
        try:
            role_list = json.loads(role_list)
        except:
            logger.exception(u"角色列表解析异常")
            role_list = []
        role_str_list = []
        role_list = sorted(role_list, cmp=None, key=lambda x: ["Operator", "BakOperator", "Maintainers"].index(x))
        for role in role_list:
            role_span_format = NOTIRY_MAN_STR_DICT.get(role, '')
            if role_span_format:
                # 获取角色对应的rtx名
                if role == "Maintainers":
                    maintainer = CCBiz.maintainers(biz_id)
                    role_rtx = ";".join(["%s(%s)" % (k, v) for k, v in maintainer.items()])
                    role_rtx = role_rtx if role_rtx else u"无"
                    role_str = role_span_format % role_rtx
                    role_str_list.append(role_str)
                else:
                    role_str_list.append(role_span_format)
        return ' '.join(role_str_list)

    @classmethod
    def gen_notify_way_name(cls, notify_way, notify_dict):
        notify_way_str = []
        try:
            if type(notify_way) is not list:
                notify_way_list = json.loads(notify_way)
            else:
                notify_way_list = notify_way
            for way in notify_way_list:
                way_str = NOTIRY_WAY_NAME_DICT.get(way, u'')
                if not way_str:
                    continue
                if way == 'phone':
                    phone_receivers = ''
                    if notify_dict.get("phone_receiver"):
                        phone_receivers = cls.gen_receiver_list_str(notify_dict.get("phone_receiver"))
                    phone_receivers = phone_receivers.rstrip(',')
                    way_str += u'[%s]' % phone_receivers
                notify_way_str.append(way_str)
        except:
            logger.exception(u"告警策略中通知方式格式错误")
            return u"通知方式异常"
        way_str = u'无' if len(notify_way_str) < 1 else " ".join(notify_way_str)
        return way_str

    @staticmethod
    def gen_receiver_list_str(receivers):
        name_list_str = ''
        user_info = CCBiz.user_info()
        receiver_list = receivers.split(",")
        for receiver in receiver_list:
            if receiver.strip(' ') == "":
                continue
            name_list_str += "%s(%s)," % (user_info.get(receiver, receiver), receiver)
        if name_list_str == "":
            name_list_str = u'无'
        return name_list_str.rstrip(',')

    @staticmethod
    def gen_notify_role_str(role_list_value):
        notify_role_str = []
        role_list = role_list_value
        try:
            if type(role_list) not in [dict, list]:
                role_list = json.loads(role_list)
            for role in role_list:
                role_str = NOTIRY_MAN_DICT.get(role, '')
                if role_str:
                    notify_role_str.append(role_str)
        except:
            logger.exception(u"告警策略中通知人格式错误")
            return u"通知人异常"
        return "; ".join(notify_role_str)

    @classmethod
    def gen_notify_final_str(cls, notify_way, notify_dict):
        final_str = u''
        final_str += u'通知方式: %s,' % cls.gen_notify_way_name(notify_way, notify_dict)
        role_list = notify_dict.get('role_list', [])
        if len(role_list) > 0:
            final_str += u'通知角色: %s,' % cls.gen_notify_role_str(role_list)
        responsible = notify_dict.get('responsible', '')
        if responsible:
            final_str += u'其它通知人: %s,' % responsible
        final_str += u'通知时间段: %s - %s' % (notify_dict.get('alarm_start_time', '00:00'),
                                          notify_dict.get('alarm_end_time', "23:59"))
        return final_str

    def delete(self, using=None):
        with ignored(JAItemDoseNotExists, AssertionError):
            MonitorConditionConfig.objects.get(id=self.condition_config_id).delete()
        with ignored(JAItemDoseNotExists, AssertionError):
            MonitorCondition.objects.get(id=self.condition_id).delete()
        with ignored(JAItemDoseNotExists, AssertionError):
            AlarmDef.objects.get(id=self.alarm_def_id).delete()
        super(AlarmStrategy, self).delete(using)

    def toggle(self, enable=True):
        enable = bool(enable)
        MonitorConditionConfig.objects.get(id=self.condition_config_id).update(is_enabled=enable)
        MonitorCondition.objects.get(id=self.condition_id).update(is_enabled=enable)
        AlarmDef.objects.get(id=self.alarm_def_id).update(is_enabled=enable)
        self.is_enabled = enable
        self.save()


    def gen_converge_config(self):
        converge_config = json.loads(self.rules)
        converge_def_id = safe_int(converge_config.get('converge_id', 0))
        params = {
            "title": u'%s收敛规则' % self.monitor_name,
            "config": json.dumps(converge_config),
            "converge_id": converge_def_id,
            "is_deleted": False
        }
        alarm_source = None
        if getattr(self, "_alarm_def", None):
            alarm_source = self._alarm_def
        elif self.alarm_def_id > 0:
            alarm_source = AlarmDef.objects.get(id=self.alarm_def_id)
        if alarm_source:
            params["is_deleted"] = alarm_source.is_deleted
            params['alarm_source_id'] = alarm_source.id
        return params


    def gen_notice_config(self):
        notify = json.loads(self.notify)
        notice_config = {
            "alarm_start_time": notify.get('alarm_start_time', '00:00'),
            "alarm_end_time": notify.get('alarm_end_time', '23:59'),
            "notify_config": self.notify,
            "title": u"%s通知方式" % self.display_name,
            'is_deleted': False
        }
        alarm_source = None
        if getattr(self, "_alarm_def", None):
            alarm_source = self._alarm_def
        elif self.alarm_def_id > 0:
            alarm_source = AlarmDef.objects.get(id=self.alarm_def_id)
        if alarm_source:
            notice_config["is_deleted"] = alarm_source.is_deleted
            notice_config['id'] = alarm_source.alarm_notice_id
        return notice_config

    def gen_monitor_items_config(self, monitor):
        kwargs = {
            'biz_id': self.cc_biz_id,
            'title': self.display_name,
            'monitor_id': monitor.id,
            'condition': self.gen_condition_config(monitor),
            'is_none': 1 if self.nodata_alarm > 0 else 0,
            'is_none_option': json.dumps({"continuous": self.nodata_alarm}),
            'monitor_level': self.monitor_level,
            'alarm_params': json.dumps(self.gen_alarm_sources_config(monitor)),
            'is_enabled': True,
            'is_deleted': False
        }
        monitor_item = None
        if getattr(self, "_monitor_item", None):
            monitor_item = self._monitor_item
        elif self.condition_id > 0:
            monitor_item = MonitorCondition.objects.get(id=self.condition_id)
        if monitor_item:
            kwargs["is_deleted"] = monitor_item.is_deleted
            kwargs["is_enabled"] = monitor_item.is_enabled
        return kwargs

    def gen_detect_algorithm_config(self, monitor_item):
        # if self.condition_id > 0:
        #     monitor_item = MonitorCondition.objects.get(id=self.condition_id)
        if hasattr(monitor_item, 'id'):
            monitor_item_id = monitor_item.id
            is_deleted = monitor_item.is_deleted
        else:
            monitor_item_id = monitor_item.get('id', 0)
            is_deleted = monitor_item.get('is_deleted', 0)
        result = {
            "algorithm_id": self.strategy_id,
            "config": self.strategy_option,
            "monitor_item_id": monitor_item_id,
            "title": u"%s异常检测" % self.display_name,
            'is_deleted': is_deleted
        }
        return result

    def gen_alarm_sources_config(self, monitor):
        if self.alarm_def_id > 0:
            monitor = self.monitor

        result = {
            'biz_id': self.cc_biz_id,
            'title': self.display_name,
            'description': monitor.monitor_name,
            'condition': self.gen_condition_config(monitor),
            'src_type': 'GSE' if monitor.scenario == 'base_alarm' else 'JA',
            'alarm_type': monitor.monitor_type,
            'scenario': monitor.scenario,
            'source_info': monitor.stat_source_info,
            'timeout': AlarmDef.timeout,
            'alarm_attr_id': monitor.id,
            'is_deleted': False,
            'is_enabled': self.is_enabled,
            'alarm_collect_id': 1,
            'alarm_notice_config': json.dumps(self.gen_notice_config()),
            'monitor_level': self.monitor_level,
            'monitor_target': monitor.monitor_target,
            'full_strategy': 'true',
            'alarm_converge_config': json.dumps(self.gen_converge_config()),
        }
        if json.loads(self.alarm_solution_config):
            result['alarm_solution_config'] = self.alarm_solution_config
        if self.alarm_def_id > 0:
            result['id'] = self.alarm_def_id
        return result

    def gen_condition_config(self, monitor):
        def get_multi_value_to_list(val, sep=","):
            if sep in val:
                return val.split(sep)
            return val

        condition = json.loads(self.condition)

        if isinstance(condition, list):
            return self.condition
        condition = [[]]

        if self.prform_cate == "ip" and self.ip:
            condition[0].append(dict(
                field="ip",
                value=get_multi_value_to_list(self.ip),
                method="eq"))
        else:
            if self.cc_set:
                condition[0].append(dict(
                    field="cc_topo_set",
                    value=get_multi_value_to_list(self.cc_set),
                    method="eq"))
            if self.cc_module:
                condition[0].append(dict(
                    field="cc_app_module",
                    value=get_multi_value_to_list(self.cc_module),
                    method="eq"))
        if monitor.monitor_type == "net":
            condition[0].append(dict(
                field="name",
                method="reg",
                value="^eth\d$"))
        return json.dumps(condition)


class ScenarioMenuManager(OperateManager):

    def init_biz_scenario_menu(self, biz_id):
        # 初始化用户场景菜单列表
        sms = list()
        for i, (system_menu, menu_name) in enumerate(self.model.system_menu_choices):
            if system_menu:
                if self.filter(system_menu=system_menu, biz_id=biz_id, menu_name=menu_name).exists():
                    continue
                sm = self.model(system_menu=system_menu, biz_id=biz_id,
                                  menu_name=menu_name, menu_index=i)
                sm.save()
                sms.append(sm)
        return sms

    def add_scenario_menu(self, biz_id, menu_name):
        # 新建场景菜单
        if not menu_name:
            return failed(u"组名不能为空")
        menu_name = menu_name.strip()
        exists = self.filter(menu_name=menu_name, biz_id=biz_id).exists()
        if exists:
            return failed(u"组名已存在，无法新增相同分组")
        if len(menu_name.encode("gbk")) > 20:
            return failed(u"组名长度不能超过20个字符，一个中文算2个字符。")
        sm = self.model(biz_id=biz_id, menu_name=menu_name)
        sm.save()
        return ok_data(sm.id)

    def edit_scenario_menu(self, menu_id, menu_name, cc_biz_id):
        # 新建场景菜单
        try:
            menu = self.get(pk=menu_id)
        except self.model.DoesNotExist:
            return failed(u"无效的请求")
        if not check_permission(menu, cc_biz_id):
            return failed(u"无权限")
        menu_name = menu_name.strip()
        count = self.filter(menu_name=menu_name, biz_id=menu.biz_id).exclude(pk=menu_id).count()
        if count > 0:
            return failed(u"同名分组已存在")
        if len(menu_name.encode("gbk")) > 20:
            return failed(u"组名长度不能超过20个字符，一个中文算2个字符。")
        menu.menu_name = menu_name
        menu.save()
        return ok()

    def del_scenario_menu(self, menu_id, cc_biz_id):
        # 新建场景菜单
        try:
            menu = self.get(pk=menu_id)
        except self.model.DoesNotExist:
            return failed(u"无效的请求")
        if not check_permission(menu, cc_biz_id):
            return failed(u"无权限")
        menu.is_deleted = True
        menu.save()
        return ok()


class ScenarioMenu(OperateRecordModel):
    """
    左侧场景菜单
    """
    system_menu_choices = (
        (u"", u"用户自定义"),
        (u"favorite", u"关注"),
        (u"default", u"默认分组"),
    )
    system_menu = models.CharField(u"系统菜单栏",
                                   choices=system_menu_choices,
                                   max_length=32, default="")
    biz_id = models.CharField(u"业务ID", max_length=100)

    menu_name = models.CharField(u"菜单名", max_length=255)
    menu_index = models.IntegerField(u"菜单顺序", default=999)

    objects = ScenarioMenuManager()

    def __unicode__(self):
        return u"【%s】%s" % (self.biz_id, self.name)

    class Meta:
        verbose_name = u'左侧菜单'
        verbose_name_plural = u'左侧菜单'

    @property
    def name(self):
        if self.system_menu:
            return self.get_system_menu_display()
        return self.menu_name

    @property
    def allowed_edit(self):
        if not self.system_menu:
            return True
        return self.system_menu not in [c[0] for c in ScenarioMenu.system_menu_choices]


class MonitorLocationManager(OperateManager):

    def get_scenario_menu_list_by_monitor_id(self, monitor_id):
        # 通过监控id获取对应的所有场景菜单列表
        locations = self.filter(monitor_id=monitor_id)
        menus = []
        for l in locations:
            if l.menu and l.menu.system_menu != u"favorite":
                menus.append(l.menu)
        return list(set(menus))

    def get_monitor_list_by_scenario_menu(self, menu_id):
        # 通过场景菜单id获取对应的监控列表
        locations = self.filter(menu_id=menu_id)
        monitors = []
        for l in locations:
            if not l.monitor.is_deleted and l.monitor.is_enabled:
                monitors.append(l.monitor)
        return list(set(monitors))



class MonitorLocation(OperateRecordModel):

    """
    监控映射
    """

    biz_id = models.CharField(u"业务ID", max_length=100)

    menu_id = models.IntegerField(u"菜单id")
    monitor_id = models.IntegerField(u"监控id")
    graph_index = models.IntegerField(u"图表所在栏目位置", default=9999999)
    width = models.IntegerField(u"宽度", default=6)

    objects = MonitorLocationManager()

    class Meta:
        verbose_name = u'监控映射'
        verbose_name_plural = u'监控映射'

    @property
    def monitor(self):
        try:
            if not hasattr(self, "_monitor"):
                _monitor = Monitor.objects.get(id=self.monitor_id)
                self._monitor = _monitor
            return self._monitor
        except JAItemDoseNotExists:
            return None

    @property
    def menu(self):
        try:
            return ScenarioMenu.objects.get(pk=self.menu_id)
        except ScenarioMenu.DoesNotExist:
            return None


class Shield(OperateRecordModel):

    biz_id = models.CharField(u"业务ID", max_length=256)
    begin_time = models.DateTimeField(u"屏蔽开始时间", db_index=True)
    end_time = models.DateTimeField(u"屏蔽结束时间", db_index=True)
    dimension = models.TextField(u"屏蔽维度(JSON)")
    description = models.TextField(u"屏蔽描述", default="")
    event_raw_id = models.CharField(u"屏蔽ID", max_length=256)
    hours_delay = models.IntegerField(u"屏蔽时间（小时）", default=0)

    # 关联监控告警后台策略ID--AlarmShieldConfigId
    backend_id = models.IntegerField(u"关联监控告警后台策略ID", default=0)

    @property
    def dimension_config(self):
        return json.loads(self.dimension or "{}")

    @property
    def alarm_type(self):
        dimension = json.loads(self.dimension)
        alarm_type = dimension.get("category", [""])[0]
        return alarm_type

    def save(self, *args, **kwargs):
        # 维护dimension参数
        dimension_dict = self.dimension_config
        if "hours_delay" in dimension_dict:
            self.hours_delay = dimension_dict.pop("hours_delay")
        self.dimension = json.dumps(dimension_dict)
        # 调用后台api
        result = ShieldApi.save_shield(self)
        if not result.get('result', False):
            raise Exception(u"保存失败: %s" % result.get('message', ''))
        self.backend_id = result.get('data', {}).get('id', 0)
        super(Shield, self).save(*args, **kwargs)

    @property
    def cc_biz_id(self):
        return json.loads(self.biz_id)[0]

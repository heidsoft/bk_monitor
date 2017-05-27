# -*- coding: utf-8 -*-
from django.conf.urls import patterns


# 配置相关
config_urlpatterns = patterns(
    "monitor.config.views",

    # 快速新增/编辑 基础性能告警
    (r"^(?P<cc_biz_id>\d+)/bp/config/performance/(?P<alarm_strategy_id>\d+)/$",
     "bp_config_monitor"),
    # 获取基础性能告警策略
    (r"^(?P<cc_biz_id>\d+)/bp/get_bp_strategy/$", "get_bp_strategy"),
    # 保存基础性能告警策略
    (r"^(?P<cc_biz_id>\d+)/bp/save_bp_strategy/$", "save_bp_strategy"),
    # 保存基础性能告警策略
    (r"^(?P<cc_biz_id>\d+)/bp/save_custom_strategy/$", "save_custom_strategy"),
    # 检测是否重复配置告警
    (r"^(?P<cc_biz_id>\d+)/bp/duplication_strategy/$", "duplication_strategy"),
    # 获取自定义监控告警策略
    (r"^(?P<cc_biz_id>\d+)/bp/get_custom_strategy/$", "get_bp_strategy"),
    # 获取策略告警事件列表
    (r"^(?P<cc_biz_id>\d+)/get_strategy_alarm_list/$",
     "get_strategy_alarm_list"),
    # 根据条件获取策略id
    (r"^(?P<cc_biz_id>\d+)/get_strategy_id_by_condition/$",
     "get_strategy_id_by_condition"),
    # 根据监控项id获取告警定义信息
    (r"^(?P<cc_biz_id>\d+)/get_alarmdef_by_monitor_id/$",
     "get_alarmdef_by_monitor_id"),
    # 获取屏蔽记录
    (r"^(?P<cc_biz_id>\d+)/shield_info/$", "shield_info"),

    # config V1 保留部分
    # 启用/停用 告警策略
    (r"^(?P<cc_biz_id>\d+)/config/operate_alram/(?P<alram_strategy_id>\d+)/$",
     "operate_alram"),
    # 删除告警策略信息
    (r"^(?P<cc_biz_id>\d+)/config/strategy_del/(?P<alram_strategy_id>\d+)/$",
     "del_strategy"),
    # 自定义告警配置
    (r"^(?P<cc_biz_id>\d+)/config/custom/(?P<monitor_id>\d+)/$",
     "config_custom"),
    # 告警策略列表
    (r"^(?P<cc_biz_id>\d+)/config/strategy/$", "get_strategy_list"),
    # 监控名称检查
    (r"^(?P<cc_biz_id>\d+)/config/check_monitor_name/$", "check_monitor_name"),
    # 更新监控项
    (r"^update/$", "update_monitor_config"),
    # 接入自定义监控
    (r"^access_custom/$", "access_custom"),

    # 配置列表页面
    (r"^(?P<cc_biz_id>\d+)/config/$", "config_list"),
    (r"^(?P<cc_biz_id>\d+)/config/get_config_data/$", "get_config_data"),
    # 启用/停用  监控
    (r"^(?P<cc_biz_id>\d+)/config/operate_monitor/(?P<monitor_id>\d+)/$",
     "operate_monitor"),
    # 编辑页面，启用/停用告警策略 （临时表）
    (r"^(?P<cc_biz_id>\d+)/config/operate_alarm_strategy/(?P<alram_strategy_id>\d+)/$",
     "operate_alram"),

    # 新增屏蔽
    (r"^(?P<cc_biz_id>\d+)/access_shield/$", "access_shield"),
    # 删除屏蔽
    (r"^(?P<cc_biz_id>\d+)/remove_shield/$", "remove_shield"),
    # 获取监控项下的策略列表
    (r"^(?P<cc_biz_id>\d+)/config/rel_strategy/$", "get_rel_strategy_list"),
    # 删除监控项
    (r"^(?P<cc_biz_id>\d+)/delete_monitor_config/$", "delete_monitor_config"),
    (r"^(?P<cc_biz_id>\d+)/custom_monitor_option_list/$",
     "custom_monitor_option_list"),

)

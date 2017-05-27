# -*- coding: utf-8 -*-
from django.contrib import admin

from monitor import models


class DatasourceAdmin(admin.ModelAdmin):
    list_display = ('cc_biz_id', 'data_set', 'data_desc', 'status', 'has_exception', 'creator',
                    'create_time', 'update_time')
    search_fields = ('data_desc', 'data_set')
    list_filter = ('cc_biz_id', 'status', 'creator')


class AgentStatusAdmin(admin.ModelAdmin):
    list_display = ('ds_id', 'ip', 'status')
    search_fields = ('ds_id',)
    list_filter = ('ds_id', 'status')


class CallMethodRecordAdmin(admin.ModelAdmin):
    list_display = ('action', 'url', 'method', 'param', 'result', 'operate_time')
    search_fields = ('action', 'method')
    list_filter = ('action', 'method')


class ScenarioMenuAdmin(admin.ModelAdmin):
    list_display = ('system_menu_choices', 'system_menu', 'biz_id', 'menu_name')
    search_fields = ('system_menu', 'biz_id', 'menu_name')
    list_filter = ('system_menu', 'biz_id', 'menu_name')


class AlarmStrategyAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Datasource, DatasourceAdmin)
admin.site.register(models.AgentStatus, AgentStatusAdmin)
admin.site.register(models.CallMethodRecord, CallMethodRecordAdmin)
admin.site.register(models.ScenarioMenu, ScenarioMenuAdmin)
admin.site.register(models.AlarmStrategy, AlarmStrategyAdmin)

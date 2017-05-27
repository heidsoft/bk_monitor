# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1495878375.186013
_enable_loop = True
_template_filename = '/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/monitor/overview/overview.html'
_template_uri = '/monitor/overview/overview.html'
_source_encoding = 'utf-8'
_exports = [u'content', u'css', u'script']


def _mako_get_namespace(context, name):
    try:
        return context.namespaces[(__name__, name)]
    except KeyError:
        _mako_generate_namespaces(context)
        return context.namespaces[(__name__, name)]
def _mako_generate_namespaces(context):
    pass
def _mako_inherit(template, context):
    _mako_generate_namespaces(context)
    return runtime._inherit_from(context, u'/monitor/base_new.html', _template_uri)
def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        def script():
            return render_script(context._locals(__M_locals))
        AGENT_SETUP_URL = context.get('AGENT_SETUP_URL', UNDEFINED)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        SITE_URL = context.get('SITE_URL', UNDEFINED)
        def content():
            return render_content(context._locals(__M_locals))
        cc_biz_id = context.get('cc_biz_id', UNDEFINED)
        def css():
            return render_css(context._locals(__M_locals))
        __M_writer = context.writer()
        __M_writer(u'\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'css'):
            context['self'].css(**pageargs)
        

        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'content'):
            context['self'].content(**pageargs)
        

        __M_writer(u'\n\n')
        if 'parent' not in context._data or not hasattr(context._data['parent'], 'script'):
            context['self'].script(**pageargs)
        

        __M_writer(u'\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_content(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        def content():
            return render_content(context)
        AGENT_SETUP_URL = context.get('AGENT_SETUP_URL', UNDEFINED)
        cc_biz_id = context.get('cc_biz_id', UNDEFINED)
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        SITE_URL = context.get('SITE_URL', UNDEFINED)
        __M_writer = context.writer()
        __M_writer(u'\n<div class="iframe-mask hidden"></div>\n<style>\n    .star-chart-panel{\n        min-height: 850px;\n    }\n    .portlet-header{\n        cursor:auto;\n        position: relative;\n    }\n.chart-add > a {\n    color: #5C90D2;\n    cursor: pointer;\n}\n.chart-add {\n    line-height: 220px;\n    font-size: 120px;\n    color: black;\n}\n    button.favorite > i.fa-star{\n        color: #999;\n    }\n    button.active > i.fa-star{\n        color:#E6A20C;\n    }\n    button.hover > i.fa-star{\n        color:#E6A20C;\n    }\n    .highcharts-tooltip span {\n        height:auto;\n        min-width:180px;\n        max-width:250px;\n        overflow:auto;\n        white-space:normal !important; // add this line...\n    }\n.king-btn.king-disabled {\n    cursor: not-allowed;\n}\n.event-danger {\n    background-color: #d26a5c;\n}\n.event-warning {\n    background-color: #4a9bff;\n}\n.event-info {\n    background-color: #888686;\n}\n</style>\n\n\n    <article class="new-content clearfix">\n            <section class="new-chart pull-left">\n                <div class="show-contents clearfix">\n                    <div class="show-content-block pull-left mainframe-monitor clearfix">\n                        <div class="left-title pull-left">\n                            <div class="left-title-inside">\n                                <i class="iconfont icon-weibiaoti1-1"></i>\n                                <p class="name">\u4e3b\u673a\u76d1\u63a7</p>\n                            </div>\n                        </div>\n                        <div class="right-content pull-right">\n                            <p class="total"><span id="host_num"></span>\u53f0</p>\n                            <div class="buttons-block">\n                                <div class="buttons-block-wrapper" style=\'\'>\n                                    <p class="button-row hide" id="no_agent_display">\n                                        <a class="king-btn new-btn error" title="\u672a\u5b89\u88c5Agent" id="agentBtn" target="_blank" href="')
        __M_writer(unicode(AGENT_SETUP_URL))
        __M_writer(u'">\n                                            <span id="no_agent_num"></span>\u53f0\u672a\u5b89\u88c5Agent\n                                        </a>\n                                    </p>\n                                    <p class="button-row hide" id="silent_agent_display">\n                                        <a class="king-btn new-btn" title="\u672a\u4e0a\u4f20\u6570\u636e" id="uploadData" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/bp/?status=1/">\n                                            <span id="silent_agent_num"></span>\u53f0\u672a\u4e0a\u62a5\u6570\u636e\n                                        </a>\n                                    </p>\n                                    <p class="button-row hide" id="perfect_agent_display">\n                                        <a class="king-btn new-btn success-btn" title="">\u592a\u68d2\u4e86\uff0c\u60a8\u7684\u4e3b\u673a\u90fd\u63a5\u5165\u76d1\u63a7\u4e86</a>\n                                    </p>\n                                    <p class="button-row hide" id="goto_cc_display">\n                                        <a class="king-btn king-round new-btn" target="_blank" href="')
        __M_writer(unicode(AGENT_SETUP_URL))
        __M_writer(u'">\u5feb\u901f\u90e8\u7f72</a>\n                                    </p>\n                                </div>\n                            </div>\n                        </div>\n                    </div>\n                    <div class="show-content-block pull-left custom-monitor">\n                        <div class="left-title pull-left">\n                            <div class="left-title-inside">\n                                <i class="iconfont icon-weibiaoti-1"></i>\n                                <p class="name">\u81ea\u5b9a\u4e49\u76d1\u63a7</p>\n                            </div>\n                        </div>\n                        <div class="right-content pull-right">\n                            <p class="total"><span id="custom_monitor_num"></span>\u9879</p>\n                            <div class="buttons-block">\n                                <div class="buttons-block-wrapper">\n                                    <p class="button-row">\n                                        <a class="king-btn king-round new-btn" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/operation_monitor/" id="checkDetail"></a>\n                                    </p>\n                                </div>\n                            </div>\n\n                        </div>\n                    </div>\n                </div>\n                <div class="show-chart">\n                    <div class="show-chart-header clearfix" id="chart_header">\n                        <span class="title">\u6700\u8fd1{{ days }}\u5929\u544a\u8b66\u6570\u91cf\u7edf\u8ba1</span>\n                        <div class="tool pull-right" id="headerMenu">\n                            <img src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/img/menu.png">\n                            <div class="menu">\n                                <ul>\n                                    <li><a href="###" v-on:click="reload_chart" data-days="3">\u6700\u8fd13\u5929</a></li>\n                                    <li><a href="###" v-on:click="reload_chart" data-days="7">\u6700\u8fd17\u5929</a></li>\n                                    <li><a href="###" v-on:click="reload_chart" data-days="30">\u6700\u8fd130\u5929</a></li>\n                                </ul>\n                            </div>\n                        </div>\n                    </div>\n                    <div class="show-chart-content" style="position:relative;">\n                        <div class="main-chart" id="chart"></div>\n                        <!-- \u52a0\u8f7d\u906e\u7f69 -->\n                        <div class="loading hide" id="chartLoading">\n                            <div class="loading-content">\n                                <img alt="loadding" src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'img/hourglass_36.gif">\n                                \u52a0\u8f7d\u4e2d\uff0c\u8bf7\u7a0d\u7b49\n                            </div>\n                        </div>\n                    </div>\n                </div>\n            </section>\n            <section class="new-list pull-right">\n                <div class="tab-box" id="alert-list">\n                    <ul class="nav nav-tabs king-nav-tabs2 king-tab-info">\n                        <li class="active">\n                            <a href="#recentAlert" data-toggle="tab">\u8fd1\u671f\u544a\u8b66\u4e8b\u4ef6</a>\n                        </li>\n                        <li>\n                            <a href="#alwaysAlert" data-toggle="tab">\u6700\u8fd1\u9891\u7e41\u544a\u8b66\u4e8b\u4ef6</a>\n                        </li>\n                        <li>\n                            <a href="#recentOperate" data-toggle="tab">\u6700\u8fd1\u64cd\u4f5c\u4e8b\u4ef6</a>\n                        </li>\n                    </ul>\n                    <div class="tab-content">\n                        <div class="tab-pane fade in active" id="recentAlert">\n                            <div class="scroll-list" data-type="scrollList">\n                                <ul class="recent-list">\n                                    <li class="empty-item hide">\n                                        \u8fd1\u671f\u6ca1\u6709\u544a\u8b66\u4e8b\u4ef6\u53d1\u751f\n                                    </li>\n                                   <template v-for="item in items">\n                                       <li>\n                                           <div class="alert-list-item">\n                                                <div class="item-content">\n                                                    <div class="emit clearfix item-{{ item.level | get_alarm_level_class }} item-title" title="">\n                                                        <a class="title pull-left" v-on:click="query_alarm_detail(item.id)">{{ item.alarm_content.title }}</a>\n                                                        <div class="time pull-right">{{ item.source_time | get_alarm_time_display }}</div>\n                                                    </div>\n                                                    <p v-if="item.alarm_content.is_performance_alarm" class="emit" title="">\u7ef4\u5ea6\u4fe1\u606f\uff1a{{ item.alarm_content.dimension }}</p>\n                                                    <p v-else class="emit" title="">\u544a\u8b66\u5bf9\u8c61\uff1a{{ item.alarm_content.source_name }}</p>\n                                                    <p class="emit" title="">\u544a\u8b66\u5185\u5bb9\uff1a{{ item.alarm_content.content }}</p>\n                                                </div>\n                                            </div>\n                                       </li>\n                                    </template>\n                                </ul>\n                                <div class="button-row" v-if="has_more">\n                                    <button type="button" class="new-btn" v-on:click="load_more_data">\u67e5\u770b\u66f4\u591a</button>\n                                </div>\n                            </div>\n                        </div>\n                        <div class="tab-pane fade" id="alwaysAlert">\n                            <div class="scroll-list" data-type="scrollList">\n                                <ul class="frequent-list">\n                                    <li class="empty-item hide">\n                                        \u6700\u8fd1\u6ca1\u6709\u9891\u7e41\u544a\u8b66\u4e8b\u4ef6\u53d1\u751f\n                                    </li>\n                                   <template v-for="item in items">\n                                       <li>\n                                        <div class="alert-list-item">\n                                            <div class="item-img">\n\n                                                <img v-if="item.strategy_type==\'ip\'" src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/img/strategy_type_ip.png">\n                                                <img v-else src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/img/strategy_type_strategy.png">\n                                            </div>\n                                            <div class="item-content">\n                                                <p class="emit">{{ item.strategy_type | get_strategy_type_display }}\uff1a\n                                                    <a v-if="item.strategy_type==\'ip\'" href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/bp/?from_overview=1&alarm_strategy_id={{ item.alarm_strategy_id }}|{{ item.cc_plat_id }}">{{ item.title }}</a>\n                                                    <a v-else href="')
        __M_writer(unicode(SITE_URL))
        __M_writer(unicode(cc_biz_id))
        __M_writer(u'/operation_monitor/?from_overview=1&alarm_strategy_id={{ item.alarm_strategy_id }}">{{ item.title }}</a>\n                                                </p>\n                                                <p class="emit">\u544a\u8b66\u6b21\u6570\uff1a<span class="delete">{{ item.cnt }}</span>\u6b21</p>\n                                            </div>\n                                        </div>\n                                       </li>\n                                    </template>\n                                </ul>\n                                <div class="button-row" v-if="has_more">\n                                    <button type="button" class="new-btn" v-on:click="load_more_data">\u67e5\u770b\u66f4\u591a</button>\n                                </div>\n                            </div>\n                        </div>\n                        <div class="tab-pane fade" id="recentOperate">\n                            <div class="scroll-list" data-type="scrollList">\n                                <ul class="operate-list">\n                                    <li class="empty-item hide">\n                                        \u6700\u8fd1\u6ca1\u6709\u64cd\u4f5c\u4e8b\u4ef6\n                                    </li>\n                                   <template v-for="item in items">\n                                        <li>\n                                            <div class="alert-list-item">\n                                                <div class="item-img" data-qq="{{ item.operator }}" data-name="{{ item.operator_name }}">\n                                                    <img v-bind:src="item.operator | get_qq_avatar_url">\n                                                </div>\n                                                <div class="item-content">\n                                                    <p class="emit">\u64cd\u4f5c\u5bf9\u8c61\uff1a{{ item.config_title }}</p>\n                                                    <p class="emit">\u64cd\u4f5c\u7c7b\u578b\uff1a<span class="{{ item.operate }}">{{ item.operate | get_operate_display }}</span></p>\n                                                    <p class="emit">\u64cd\u4f5c\u8be6\u60c5\uff1a{{{ item.operate_desc | get_operate_desc }}}</p>\n                                                </div>\n                                            </div>\n                                        </li>\n                                    </template>\n                                </ul>\n                                <div class="button-row" v-if="has_more" >\n                                    <button type="button" class="new-btn" v-on:click="load_more_data">\u67e5\u770b\u66f4\u591a</button>\n                                </div>\n                            </div>\n                        </div>\n                        <!-- \u52a0\u8f7d\u906e\u7f69 -->\n                        <div class="loading hide" id="listLoading">\n                            <div class="loading-content">\n                                <img alt="loadding" src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'img/hourglass_36.gif">\n                                \u52a0\u8f7d\u4e2d\uff0c\u8bf7\u7a0d\u7b49\n                            </div>\n                        </div>\n                    </div>\n                </div>\n\n            </section>\n        </article>\n            <div class="king-time-bar in-overview">\n                <div class="time_selector ml15 mr0" style="width:150px;">\n\n                    <div class="input-group">\n                      <div class="input-group-addon"><i class="fa fa-calendar"></i></div>\n                      <input type="text" class="form-control daterangepicker_demo" id="daterangepicker" placeholder="\u9009\u62e9\u65e5\u671f...">\n                    </div>\n                </div>\n                <div class="king-num-bar timeline ui-selectable ml15 mr0" id="selectable">\n                    <div class="icon-time ui-selected">\u6574\u5929</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="0">0</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="1"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="2">2</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="3"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="4">4</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="5"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="6">6</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="7"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="8">8</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="9"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="10">10</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="11"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="12">12</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="13"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="14">14</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="15"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="16">16</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="17"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="18">18</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="19"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="20">20</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="21"></div>\n                    <div class="timeblock  ui-selectee ui-selected" value="22">22</div>\n                    <div class="timeblock  ui-selectee ui-selected" value="23"></div>\n                </div>\n            </div>\n\t        <div class="panel panel-default">\n\t            <div class="panel-heading panel-heading-fix">\n\t                <div class="inline-block">\n\t                    <span class="icon mr5"><i class="fa fa-star"></i></span>\n\t                    <strong>\u5173\u6ce8\u6307\u6807</strong>\n\t                </div>\n\t                <div class="pull-right">\n\t                    <div class="page-btn-group">\n\t                        <a class="king-btn-demo king-btn king-btn-icon king-radius king-default mr15 page-refresh" title="\u5237\u65b0">\n\t                             <i class="fa fa-refresh"></i>\n\t                        </a>\n\t                        <a class="king-btn-demo king-btn king-btn-icon king-radius king-default page-prev" title="\u4e0a\u4e00\u9875">\n\t                            <i class="fa fa-angle-left"></i>\n\t                        </a>\n\t                        <a class="king-btn-demo king-btn king-btn-icon king-radius king-default page-next" title="\u4e0b\u4e00\u9875">\n\t                             <i class="fa fa-angle-right"></i>\n\t                        </a>\n\t                    </div>\n\t                </div>\n\t            </div>\n\t            <div class="panel-body star-chart-panel">\n\t                <img alt="loadding" class="loading-img" src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'img/loading_2_36x36.gif">\n\t            </div>\n\t        </div>\n\t<!-- /.row -->\n    <div class="modal fade" id="modal" role="dialog"> </div>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_css(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        def css():
            return render_css(context)
        __M_writer = context.writer()
        __M_writer(u'\n<link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/css/index.css" rel="stylesheet">\n<link rel="stylesheet" type="text/css" href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/css/overview/css/iconfont.css">\n<link rel="stylesheet" type="text/css" href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/css/overview/css/new.css?v=1">\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


def render_script(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        STATIC_URL = context.get('STATIC_URL', UNDEFINED)
        def script():
            return render_script(context)
        __M_writer = context.writer()
        __M_writer(u'\n\n\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/highcharts-4.1.7/js/highcharts.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/highcharts-4.1.7/js/highcharts-more.js"></script>\n<!--\u65f6\u95f4\u9009\u62e9\u5668-->\n<link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/daterangepicker-2.0/css/daterangepicker.css" rel="stylesheet">\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/daterangepicker-2.0/js/moment.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/daterangepicker-2.0/js/daterangepicker.js"></script>\n<script type="text/javascript" src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'js/jquery-ui.min.js"></script>\n\n\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/js/dataview/graph-highcharts.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/js/overview/echarts-all.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/js/dataview/dataview.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/js/dataview/operation.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/js/overview/overview.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/mCustomScrollbar-3.0.9/jquery.mCustomScrollbar.concat.min.js"></script>\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'alert/js/overview/overview_new.js"></script>\n<!-- \u5305\u62ec\u6240\u6709kendoui\u7684js\u63d2\u4ef6\u6216\u8005\u53ef\u4ee5\u6839\u636e\u9700\u8981\u4f7f\u7528\u7684js\u63d2\u4ef6\u8c03\u7528\u3000-->\n<link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/kendoui-2015.2.624/styles/kendo.common.min.css" rel="stylesheet">\n<link href="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/kendoui-2015.2.624/styles/kendo.default.min.css" rel="stylesheet">\n<script src="')
        __M_writer(unicode(STATIC_URL))
        __M_writer(u'assets/kendoui-2015.2.624/js/kendo.all.min.js"></script>\n<script>\nrender_star_contains(1);\ninit_top_time_bar();\n')
        __M_writer(u'</script>\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"133": 311, "134": 314, "135": 314, "136": 315, "137": 315, "138": 317, "139": 317, "140": 318, "141": 318, "142": 319, "143": 319, "144": 320, "145": 320, "146": 323, "147": 323, "148": 324, "149": 324, "150": 325, "151": 325, "152": 326, "153": 326, "154": 327, "27": 0, "156": 328, "157": 328, "158": 329, "159": 329, "160": 331, "161": 331, "162": 332, "155": 327, "164": 333, "163": 332, "166": 338, "42": 1, "172": 166, "47": 6, "52": 309, "57": 339, "63": 8, "73": 8, "74": 73, "75": 73, "76": 78, "77": 78, "78": 78, "79": 86, "80": 86, "81": 104, "82": 104, "83": 104, "84": 116, "85": 116, "86": 131, "87": 131, "88": 190, "89": 190, "90": 191, "91": 191, "92": 195, "93": 195, "94": 195, "95": 196, "96": 196, "97": 196, "98": 238, "99": 238, "100": 304, "101": 304, "165": 333, "107": 2, "114": 2, "115": 3, "116": 3, "117": 4, "118": 4, "119": 5, "120": 5, "126": 311}, "uri": "/monitor/overview/overview.html", "filename": "/data/bksuite_ce-3.0.22-beta/paas/paas_agent/apps/projects/bk_monitor/code/bk_monitor/templates/monitor/overview/overview.html"}
__M_END_METADATA
"""

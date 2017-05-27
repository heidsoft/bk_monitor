// 数据源列表vue对象
var g_ds_table_vue;
// 查看明细vue对象
var g_ds_detail_vue;

$(document).ready(function(){
    // 创建vue对象
    g_ds_table_vue = init_ds_table_vue();

    // 加载列表数据
    update_ds_table();

    // 初始化控件
    initPlugins();

    // 绑定事件
    bindEvents();

    // 更新节点状态
    update_ds_status();

    // 每10秒更新列表状态
    // setInterval("update_ds_periodic()", 10000)

    $(window).click(function(e) {
        //Hide the menus if visible
        $("#add_agent_part").addClass("hide");
    });

    $('#div_agent_status_title').click(function(event){
        event.stopPropagation();
    });

});


function update_ds_periodic(){
    // 更新节点状态
    update_ds_status();
    // 加载列表数据
    update_ds_table();
}


function iframeCallBack(){
    get_ds_monitors();
    $('.iframe-mask').addClass('hidden');
};


function initPlugins(){
    //初始化数据详情中日期选择
    $('#timerange').daterangepicker({
        locale : {
            "format": "YYYY-MM-DD",// 日期格式
            "separator": " 至 ",
            "applyLabel": "确定",
            "cancelLabel": "取消",
            "fromLabel": "从",
            "toLabel": "到",
            "weekLabel": '周',
            "customRangeLabel": "自定义",
            "daysOfWeek": [
                "日",
                "一",
                "二",
                "三",
                "四",
                "五",
                "六"
            ],
            "monthNames": [
                "一月",
                "二月",
                "三月",
                "四月",
                "五月",
                "六月",
                "七月",
                "八月",
                "九月",
                "十月",
                "十一月",
                "十二月"
            ],
            "firstDay": 1 // 周开始时间
        },
        maxDate: moment(),
        autoApply: true, //选择日期后自动设置值
        singleDatePicker : true, //单选选择一个日期
    });
}


function bind_switch(){
    $('[data-type="switch"]').each(function(){
        var $parent = $(this).parent();
        if (!$parent.hasClass('switch-animate')){
            $parent.bootstrapSwitch();
        }
    });

    //点击状态开关回调函数
    $('.has-switch').on('switch-change', function (e, data) {
        var $el = $(data.el);      //当前元素
        switch($el.data('value')){
            case 'ds-list':
                // 数据源启停
                toggle_ds($el.parents('tr').data('ds_id'), data.value);
                break;
            case 'monitor-list':
                // 数据源关联监控启停
                toggle_monitor($el.parents('tr').data('ds_id'), data.value);
                break;
        }
    });
}


function toggle_ds(ds_id, action){
    $('#ds_list_loading').removeClass('hide');
    action = action ? 'on' : 'off';
    var url = '{0}{1}/datasource/{2}/{3}/'.format(site_url, cc_biz_id, action, ds_id);
    ajax_post(url, {}, toggle_ds_callback);
}


function toggle_monitor(ds_id, action){
    action = action ? 'on' : 'off';
    // 数据源关联监控启停
    console.log(action);
}


function toggle_ds_callback(res){
    if(!res.result){
		return alert_topbar("操作失败", "fail");
	}
    alert_topbar("操作成功", "success");
    update_ds_table();
    setTimeout(function(){
        var url = '{0}{1}/datasource/get_agent_status/{2}/{3}/{4}/'.format(site_url, cc_biz_id,
            g_ds_detail_vue.ds_id, g_ds_detail_vue.agent_status.page, g_ds_detail_vue.agent_status.page_size);
        ajax_get(url, {}, function(){
            var url = '{0}{1}/datasource/get_ds_list/{2}/{3}?keyword={4}'.format(site_url, cc_biz_id, g_ds_table_vue.page, g_ds_table_vue.page_size, g_ds_table_vue.keyword);
            ajax_get(url, {}, render_ds_table_vue_data);
        });
    }, 5000);
}


function ajax_post(url, params, callback) {
    $.post(url, params, callback, 'json');
}


function bindEvents(){
    //数据源列表中预览按钮
    $(document).on('click', '[data-value="main-preview"]', function(){
        // 获取id
        var ds_id = $(this).parents('tr').data('ds_id');
        open_side_dialog(ds_id);
    });

    //数据源列表中编辑按钮
    $(document).on('click', '[data-value="main-modify"]', function(){

    });

    //数据源弹层中删除按钮
    $(document).on('click', '[data-value="side-delete"]', function(){

    });

    //打开侧边弹层
    $('#mainTable').on('click', 'tr', function(e){
        var tagName = e.target.tagName;
        if(tagName == 'TR' || tagName == 'TD'){
            // 获取id
            var ds_id = $(this).data('ds_id');
            open_side_dialog(ds_id);
        }
    });

    function open_side_dialog(ds_id){
        if(ds_id == undefined){
            return;
        }
        var $target = $('#sideDialog');
        $target.removeClass('hidden open');
        getComputedStyle(document.getElementById('sideDialog')).display;
        $target.addClass('open');
        $('html').css('overflow', 'hidden');
        $('body').css('overflow', 'hidden');
        // 加载数据
        load_ds_detail_data(ds_id);
    }

    //关闭侧边弹层
    $('#sideDialog').on('click', function(e){
        var $target = $(e.target),
            $this = $(this);

        if(!$target.parents('.side-dialog-wrapper').length){
            $this.removeClass('open');
            setTimeout(function(){
                $this.addClass('hidden');
                $('html').css('overflow', 'auto');
                $('body').css('overflow', 'auto');
            }, 300);
            // 更新数据源列表
            update_ds_table();
        }


    });
}


function load_ds_detail_data(ds_id){
    // 新建或更新vue对象
    if(g_ds_detail_vue==undefined){
        g_ds_detail_vue = init_ds_detail_vue(ds_id);
    } else{
        g_ds_detail_vue.$data = get_ds_detail_default_vue_data(ds_id);
    }

    // 隐藏添加节点
    $("#add_agent_part").addClass('hide');

    // 拉取基本信息
    var url = '{0}{1}/datasource/get_ds/{2}/'.format(site_url, cc_biz_id, ds_id);
    ajax_get(url, {}, render_ds_basic_info_vue_data);

    // 拉取数据上报节点状态
    get_agent_status();

    // 拉取数据明细
    get_ds_data_total();

    // 拉取关联监控
    get_ds_monitors();
}


function get_ds_detail_default_vue_data(ds_id){
    return {
        open_flag: true,  // 页面打开标记，避免watch中重复请求
        ds_id: ds_id,
        // 基本信息
        basic_info: {},
        // 数据上报节点状态
        agent_status: {
            page: 1,
            page_size: 10,
            total: 0,
            max_page: 0,
            pagination_indexs: [],
            data_list: [],
            new_ip: ''
        },
        // 数据明细
        data_info: {
            date: moment().format('YYYY-MM-DD'),
            page: 1,
            page_size: 10,
            total: 0,
            max_page: 0,
            pagination_indexs: [],
            data_list: [],
        },
        // 关联监控项
        monitor_info: {
            page: 1,
            page_size: 10,
            total: 0,
            max_page: 0,
            pagination_indexs: [],
            data_list: [],
        }
    };
}


function init_ds_detail_vue(ds_id){
    return new Vue({
        el: '#sideDialog',
        data: get_ds_detail_default_vue_data(ds_id),
        computed: {
            field_list: function(){
                // 获取表字段
                var field_list = [];
                try{
                    var fields = JSON.parse(this.basic_info.data_json).fields;
                    for(var i=0; i<fields.length; ++i){
                        if (fields[i].time_format == '1'){
                            continue
                        }
                        field_list.push(fields[i].name);
                    }
                    field_list.push('dtEventTime');
                }
                catch (err){
                    console.log('computed field list exception.')
                }
                return field_list;
            }
        },
        watch: {
            'data_info.date': function (val, oldVal) {
                // 页面重新打开，日期会清空，避免watch中重复请求
                if(val=='' && this.open_flag){
                    this.open_flag = false;
                }
                else if(val=='' || /^\d{4}-\d{2}-\d{2}$/.test(val)){
                    this.data_info.page = 1;
                    get_ds_data_total();
                }
                else{
                    this.data_info.date = oldVal;
                }
            },
        },
        methods: {
            prev_page: function() {
                if( this.data_info.page > 1){
                    this.data_info.page -= 1;
                    update_ds_detail_table();
                }
            },
            next_page: function(){
                if(this.data_info.page < this.data_info.max_page){
                    this.data_info.page += 1;
                    update_ds_detail_table();
                }
            },
            goto_page: function(page){
                if(page!=this.data_info.page && page>=1 && page<=this.data_info.max_page){
                    this.data_info.page = page;
                    update_ds_detail_table();
                }
            },
            agent_status_prev_page: function() {
                if( this.agent_status.page > 1){
                    this.agent_status.page -= 1;
                    get_agent_status();
                }
            },
            agent_status_next_page: function(){
                if(this.agent_status.page < this.agent_status.max_page){
                    this.agent_status.page += 1;
                    get_agent_status();
                }
            },
            agent_status_goto_page: function(page){
                if(page!=this.agent_status.page && page>=1 && page<=this.agent_status.max_page){
                    this.agent_status.page = page;
                    get_agent_status();
                }
            },
            refresh_agent: function(ip){
                // 重新下发配置
                app_confirm("确定重新下发？", function() {
                    manage_agent('refresh', ip);
                });
            },
            remove_agent: function(ip){
                // 删除配置
                app_confirm("确定删除？", function() {
                    manage_agent('remove', ip);
                });
            },
            // 显示添加数据节点输入框
            show_add_agent: function(){
                $("#add_agent_part").removeClass('hide');
            },
            append_agent: function(ip){
                // 添加配置
                var ip = this.agent_status.new_ip;
                // 校验ip
                if(validate_ip(ip)){
                    dialog({
                        width: 260,
                        title: '确认',
                        content: "确定添加？",
                        okValue: '确定',
                        ok: function() {
                            manage_agent('append', ip);
                            event.stopPropagation();
                        },
                        cancelValue: '取消',
                        cancel: function() {
                            event.stopPropagation();
                        }
                    }).show();
                } else{
                    alert_topbar("请输入正确的IP格式", "fail");
                    $("#new_ip").focus();
                }
            },
            monitor_prev_page: function() {
                if( this.monitor_info.page > 1){
                    this.monitor_info.page -= 1;
                    get_ds_monitors();
                }
            },
            monitor_next_page: function(){
                if(this.monitor_info.page < this.monitor_info.max_page){
                    this.monitor_info.page += 1;
                    get_ds_monitors();
                }
            },
            monitor_goto_page: function(page){
                if(page!=this.monitor_info.page && page>=1 && page<=this.monitor_info.max_page){
                    this.monitor_info.page = page;
                    get_ds_monitors();
                }
            },
            edit_monitor: function(id){
                // todo 编辑监控
                var url = '{0}{1}/config/custom/{2}/'.format(site_url, cc_biz_id, id);
                open_div(url);
                $('.iframe-mask').removeClass('hidden');
            },
            delete_monitor: function(id){
                // 删除监控
                app_confirm("确定删除吗？", function(){
                    $('#ds_monitors_loading').removeClass('hide');
                    var url = '{0}{1}/delete_monitor_config/'.format(site_url, cc_biz_id);
                    ajax_post(url, {'monitor_id': id}, delete_monitor_callback);
                })
            }
        }
    })
}


function init_ds_table_vue() {
    return new Vue({
        el: '#ds_table',
        data: {
            ds_list: [],
            keyword: '',
			page: 1,
            page_size: 10,
            total: 0,
            pagination_indexs: []
        },
        computed: {
            max_page: function(){
                return Math.ceil(this.total / this.page_size);
            }
        },
        methods: {
            prev_page: function() {
                if( this.page > 1){
                    this.page -= 1;
                    update_ds_table();
                }
            },
            next_page: function(){
                if(this.page < this.max_page){
                    this.page += 1;
                    update_ds_table();
                }
            },
            goto_page: function(page){
                if(page!=this.page && page>=1 && page<=this.max_page){
                    this.page = page;
                    update_ds_table();
                }
            },
            search: function(event){
                this.page = 1;
                update_ds_table();
            },
            edit_ds: function(ds_id){
                window.location.href = '{0}{1}/datasource/config/{2}/'.format(site_url, cc_biz_id, ds_id);
            }
        },
        watch: {
            'ds_list': function(oldVal, newVal){
                // 数据更新后，重新绑定switch控件
                bind_switch();
                // tootltip
                $(".fa-exclamation-triangle").mouseenter( function(){
                    $(this).next().removeClass('hide');
                } ).mouseleave( function(){
                    $(this).next().addClass('hide');
                } );
            }
        }
    });
}


function update_ds_table(){
    get_ds_table_data(g_ds_table_vue.page, g_ds_table_vue.page_size, g_ds_table_vue.keyword);
}


function update_ds_status(){
    var url = '{0}{1}/datasource/update_ds_status/'.format(site_url, cc_biz_id);
    return ajax_get(url, {}, function(res){console.log('update_ds_status')});
}


function update_ds_detail_table(){
    // 显示loading
    $('#ds_data_loading').removeClass('hide');
    get_ds_detail_table_data(g_ds_detail_vue.ds_id, g_ds_detail_vue.data_info.page,
        g_ds_detail_vue.data_info.page_size, g_ds_detail_vue.data_info.date);
}


function get_agent_status(){
    // 显示loading
    $('#ds_agent_loading').removeClass('hide');
    var url = '{0}{1}/datasource/get_agent_status/{2}/{3}/{4}/'.format(site_url, cc_biz_id,
        g_ds_detail_vue.ds_id, g_ds_detail_vue.agent_status.page, g_ds_detail_vue.agent_status.page_size);
    return ajax_get(url, {}, render_agent_status_data);
}


function get_ds_monitors(){
    // 显示loading
    $('#ds_monitors_loading').removeClass('hide');
    var url = '{0}{1}/datasource/get_ds_monitors/{2}/'.format(site_url, cc_biz_id, g_ds_detail_vue.ds_id);
    return ajax_get(url, {}, render_ds_monitors_data);
}


function manage_agent(action, ip){
    // 显示loading
    $('#ds_agent_loading').removeClass('hide');
    var url = '{0}{1}/datasource/manage_agent/{2}/{3}/{4}/'.format(site_url, cc_biz_id, action, g_ds_detail_vue.ds_id, ip);
    return ajax_get(url, {}, manage_agent_callback);
}


function get_ds_data_total(){
    // 显示loading
    $('#ds_data_loading').removeClass('hide');
    var url = '{0}{1}/datasource/get_ds_data_total/{2}/?date={3}'.format(site_url, cc_biz_id, g_ds_detail_vue.ds_id,
        g_ds_detail_vue.data_info.date);
    return ajax_get(url, {}, render_ds_data_total_vue_data);
}


function get_ds_table_data(page, page_size, keyword){
    $('#ds_list_loading').removeClass('hide');
    var url = '{0}{1}/datasource/get_ds_list/{2}/{3}?keyword={4}'.format(site_url, cc_biz_id, page, page_size, keyword);
    return ajax_get(url, {}, render_ds_table_vue_data);
}


function get_ds_detail_table_data(ds_id, page, page_size, date){
    var url = '{0}{1}/datasource/get_ds_data_list/{2}/{3}/{4}/?date={5}'.format(site_url, cc_biz_id, ds_id, page, page_size, date);
    return ajax_get(url, {}, render_ds_data_table_vue_data);
}


function render_ds_table_vue_data(res) {
    $('#ds_list_loading').addClass('hide');
	if(res.result){
		update_data_to_ds_table_vue(res.data);
	} else{
		alert_topbar("请求数据失败", "fail");
	}
}


function render_ds_data_table_vue_data(res) {
    // 隐藏loading
    $('#ds_data_loading').addClass('hide');
	if(res.result){
		update_data_info_data_to_ds_detail_vue(res.data);
	} else{
		alert_topbar("拉取数据明细失败", "fail");
	}
}


function render_agent_status_data(res) {
    // 隐藏loading
    $('#ds_agent_loading').addClass('hide');
	if(res.result){
		update_agent_status_data_to_ds_detail_vue(res.data);
	} else{
		alert_topbar("拉取数据上报节点数据失败", "fail");
	}
}


function render_ds_monitors_data(res) {
    // 隐藏loading
    $('#ds_monitors_loading').addClass('hide');
	if(res.result){
		update_ds_monitors_data_to_ds_detail_vue(res.data);
	} else{
		alert_topbar("拉取关联监控项数据失败", "fail");
	}
}


function render_ds_data_total_vue_data(res) {
	if(res.result){
		update_data_info_total_to_ds_detail_vue(res.data);
	} else{
        // 隐藏loading
        $('#ds_data_loading').addClass('hide');
		alert_topbar("拉取数据明细失败", "fail");
	}
}


function manage_agent_callback(res) {
    $('#ds_agent_loading').addClass('hide');
	if(res.result){
        // 隐藏添加框
        $("#add_agent_part").addClass("hide");
        // 新增，跳转到第一页
        // 删除和重新下发，更新当前页
        if (res.action=='append'){
            g_ds_detail_vue.agent_status.page = 1;
        }
        g_ds_detail_vue.agent_status.new_ip = '';
        alert_topbar("操作成功", "success");
        get_agent_status();
	} else{
        // 隐藏loading
        $('#ds_data_loading').addClass('hide');
		alert_topbar("操作失败：" + res.message, "fail");
	}
}


function delete_monitor_callback(res) {
    $('#ds_monitors_loading').addClass('hide');
	if(res.result){
        get_ds_monitors();
        alert_topbar("删除成功", "success");
	} else{

		alert_topbar("删除失败", "fail");
	}
}


function render_ds_basic_info_vue_data(res) {
	if(res.result){
		update_basic_info_data_to_ds_detail_vue(res.data);
	} else{
		alert_topbar("拉取基本信息失败", "fail");
	}
}


function update_data_to_ds_table_vue(data) {
    g_ds_table_vue.total = data.total;
    g_ds_table_vue.ds_list = data.list;
    g_ds_table_vue.pagination_indexs = get_pagination_indexs(g_ds_table_vue.page, g_ds_table_vue.page_size, g_ds_table_vue.total);
}


function update_data_info_data_to_ds_detail_vue(data) {
    var data_info = g_ds_detail_vue.data_info;
    data_info.data_list = data.list;
    data_info.pagination_indexs = get_pagination_indexs(data_info.page, data_info.page_size, data_info.total);
}


function update_data_info_total_to_ds_detail_vue(data) {
    var data_info = g_ds_detail_vue.data_info;
    data_info.total = data;
    data_info.max_page = Math.ceil(data_info.total / data_info.page_size);
    if(data>0){
        // 加载列表数据
        update_ds_detail_table();
    } else{
        render_ds_data_table_vue_data({result: true, data: {list: []}});
    }
}


function update_agent_status_data_to_ds_detail_vue(data) {
    var agent_status = g_ds_detail_vue.agent_status;
    agent_status.total = data.total;
    agent_status.data_list = data.data_list;
    agent_status.max_page = Math.ceil(agent_status.total / agent_status.page_size);
    agent_status.pagination_indexs = get_pagination_indexs(agent_status.page, agent_status.page_size, agent_status.total);
}


function update_ds_monitors_data_to_ds_detail_vue(data) {
    for(var i in data){
        data[i].stat_source_info = JSON.parse(data[i].stat_source_info);
    }
    var monitor_info = g_ds_detail_vue.monitor_info;
    monitor_info.total = data.length;
    monitor_info.data_list = data;
    monitor_info.page_size = data.length;
    monitor_info.max_page = Math.ceil(monitor_info.total / monitor_info.page_size);
    monitor_info.pagination_indexs = get_pagination_indexs(monitor_info.page, monitor_info.page_size, monitor_info.total);
}


function update_basic_info_data_to_ds_detail_vue(data) {
    g_ds_detail_vue.basic_info = data;
}


function ajax_get(url, params, callback) {
    $.get(url, params, callback, 'json');
}


// Vue自定义过滤器
Vue.filter('get_status_css_class', function (value) {
    switch(value){
        case 'normal':
            return 'success';
        case 'stopped':
            return 'error';
        default:
            return '';
    }
});


Vue.filter('get_status_display', function (value) {
    switch(value){
        case 'create':
            return '接入中...';
        case 'stop':
            return '停用中...';
        case 'delete':
            return '剔除中...';
        case 'normal':
            return '正常';
        case 'stopped':
            return '停用';
        case 'exception':
            return '异常';
        default:
            return value;
    }
});


Vue.filter('get_ds_disabled_msg', function (value) {
    switch(value){
        case 'create':
            return '数据源正处于接入中状态...';
        case 'stop':
            return '数据源正处于停用中状态...';
        case 'delete':
            return '数据源正处于剔除中状态...';
        case 'normal':
            return '正常';
        case 'stopped':
            return '停用';
        case 'exception':
            return '异常';
        default:
            return value;
    }
});


Vue.filter('ds_disabled', function (value) {
    return value!='normal' && value!='stopped';
});

Vue.filter('get_agent_status_css_class', function (value) {
    switch(value){
        case 'normal':
            return 'success';
        case 'exception':
            return 'warning';
        default:
            return '';
    }
});

Vue.filter('dispaly_monitor_field', function (stat_source_info) {
    return '{0}({1})'.format(stat_source_info.aggregator, stat_source_info.monitor_field);
});

Vue.filter('dispaly_dimensions', function (stat_source_info) {
    return stat_source_info.dimensions.join(' ');
});

Vue.filter('dispaly_monitor_freq', function (stat_source_info) {
    return stat_source_info.count_freq / 60 + ' 分钟';
});


function validate_ip(ip){
    var reg = /^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$/;
    return reg.test(ip);

}


/* 分页逻辑
1、显示第一页和最后一页
2、显示当前页的左右各三个
3、中间显示省略号
4、当前页为第一页时，第一页disable
5、当前页为最后一页时，最后一页disable
@return Array
[1, 2, 3, 4, '...', n]
*/
function get_pagination_indexs(page, page_size, total){
    if(total==0){
        return [];
    }
    var pagination_indexs = [];
    var max_page = Math.ceil(total / page_size);
    // 默认显示第一页
    pagination_indexs.push(1);
    if(page > 1){
        if(page-3>2){
            // 左侧显示省略号
            pagination_indexs.push('...');
        }
        // 获取page左侧的三页
        for(var i=3; i>=1; --i){
            if(page-i>1){
                pagination_indexs.push(page-i);
            }
        }
        pagination_indexs.push(page);
    }
    if(page < max_page){
        // 获取page右侧的三页
        for(var i=1; i<=3; ++i){
            if(page+i < max_page){
                pagination_indexs.push(page+i);
            }
        }
        if(page+3 < max_page-1){
            // 右侧显示省略号
            pagination_indexs.push('...');
        }
        // 默认显示最后一页
        pagination_indexs.push(max_page);
    }
    return pagination_indexs;
}
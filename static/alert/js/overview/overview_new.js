$(document).ready(function () {
    // 默认加载最近频繁告警
    init_tab_data("recentAlert");
    // 加载自定义监控数量数据
    get_custom_alarm_num();

    // 获取agent安装状态
    get_agent_status();

    //绑定最近操作事件头像鼠标hover事件
    $('#recentOperate').on('mouseenter', '.item-img', function(){
        var $this = $(this);
        var html = '<div class="item-info" data-type="item-info">'+
                            '<p class="nickname">操作人: {0}</p>'+
                        '</div>';
        $this.append(html.format($this.data('name')));
    }).on('mouseleave', '.item-img', function(){
        $(this).find('[data-type="item-info"]').remove();
    });
});
/*
存储列表数据
{
	'tab_id': {
		end_time: '',
		has_more: '',
		page: ,
		biz_id,
	}
}
*/
var tab_data = {};
// 一周内
var end_time = moment().format('YYYY-MM-DD HH:mm:ss');
var begin_time = moment().subtract(6, 'days').format('YYYY-MM-DD HH:mm:ss');

// add format method to string
if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != 'undefined'
        ? args[number]
        : match
      ;
    });
  };
}


function get_custom_alarm_num() {
    var url = '{0}{1}/overview/get_custom_monitor_num/'.format(site_url, cc_biz_id);
    $.get(url, {}, render_custom_monitor_num, 'json');
}


function render_custom_monitor_num(res) {
    if(res.result){
        $("#custom_monitor_num").text(res.data);
        $("#checkDetail").text(parseInt(res.data)==0 ? "立即创建" : "查看明细");
    } else{
        alert_topbar("请求自定义监控数据失败：" + res.message, "fail");
    }
}


function get_agent_status() {
    var url = '{0}{1}/overview/get_agent_status/'.format(site_url, cc_biz_id);
    $.get(url, {}, render_agent_status, 'json');
}

var agent_status_data;
function render_agent_status(res) {
    if(res.result){
        agent_status_data = res.details;
        var host_total = agent_status_data.agent_ok_cnt + agent_status_data.agent_fail_cnt;
        $("#host_num").text(host_total);
        $("#no_agent_num").text(agent_status_data.agent_fail_cnt);
        // 为0时不展示
        if (agent_status_data.agent_fail_cnt!=0){
            $("#no_agent_display").removeClass("hide");
        }
        if(host_total==0){
            $("#goto_cc_display").removeClass('hide');
        } else{
            // 获取上报数据状况
            get_agent_data_report_status();
        }

    } else{
        alert_topbar("请求agent状态数据失败", "fail");
    }
}


function get_agent_data_report_status() {
    var url = '{0}{1}/overview/get_agent_data_report_status/'.format(site_url, cc_biz_id);
    $.get(url, {}, render_agent_data_report_status, 'json');
}


function render_agent_data_report_status(res) {
    if(res.result){
        // 未上报数据：已安装agent的iplist 和 实际已上报数据iplist的差集
        var no_data_agent = agent_status_data.ok_ip_list.filter(function(ok_ip){
            return res.data[[ok_ip.ip, ok_ip.cc_plat_id].join('|')]!=true;
        });

        var host_num = $("#host_num").text();

        $("#silent_agent_num").text(no_data_agent.length);
        if (no_data_agent.length!=0){
            $("#silent_agent_display").removeClass("hide");
        } else if ($("#no_agent_num").text()==0){
            // 都为0时，展示 太棒了，您的主机都接入监控了！
            $("#perfect_agent_display").removeClass("hide");
        }
    } else{
        alert_topbar("请求agent上报状态数据失败：" + res.message, "fail");
    }
}


function get_silent_agent_num() {
    var url = '{0}{1}/overview/get_silent_agent_num/'.format(site_url, cc_biz_id);
    $.get(url, {}, render_silent_agent_num, 'json');
}


function render_silent_agent_num(res) {
    if(res.result){
        // 总数 - 未安装agent数
        var no_agent_num = $("#no_agent_num").text();
        var silent_agent_num = Number.parseInt(res.data) - Number.parseInt(no_agent_num);
        $("#silent_agent_num").text(silent_agent_num);
        if (silent_agent_num!=0){
            $("#silent_agent_display").removeClass("hide");
        } else if (no_agent_num==0){
            // 都为0时，展示 太棒了，您的主机都接入监控了！
            $("#perfect_agent_display").removeClass("hide");
        }
    } else{
        alert_topbar("请求agent未上报数据数量失败：" + res.message, "fail");
    }
}


$('#headerMenu').on('click', function(){
    $(this).children('.menu').toggleClass('on');
});


$('[data-type="scrollList"]').mCustomScrollbar({
    setHeight:$('.new-chart').outerHeight() - $('#alert-list > ul').outerHeight() - $('#alert-list').next().outerHeight() - 15,
    theme:"minimal-dark",
    mouseWheel:{
        enable: true,
        scrollAmount: 120,
        axis: 'y',
        preventDefault: true
    },
    callbacks: {
        onUpdate: function(){
            // 获取tab_id
            var tab_id = $(this).parent().attr('id');
            // 已经加载过，切换后不再加载
            if (!(tab_id in tab_data)){
                init_tab_data(tab_id);
            }
        }
    }
});

function init_tab_data(tab_id) {
    // 初始化对象
    tab_data[tab_id] = {
        vue_obj: init_tab_vue(tab_id, [])
    };

    // 加载数据
    get_tab_data(tab_id, tab_data[tab_id].vue_obj.page);
}


var render_tab_data = function(tab_id) {
    return function (res) {
        $("#listLoading").addClass('hide');
        if(res.result){
            // 初始化vue对象
            var data = res.data;
            append_data_to_vue(tab_id, data);
        } else{
            alert_topbar("请求数据失败：" + res.message, "fail");
        }
    }
}


function append_data_to_vue(tab_id, data) {
    var vue_obj = tab_data[tab_id].vue_obj;
    if(data.length < 10){
        vue_obj.has_more = false;
    } else{
        vue_obj.has_more = true;
    }
    if(data.length > 0){
        vue_obj.items.push.apply(vue_obj.items, data);
    }
    if(vue_obj.page==1 && data.length==0){
        // 没有数据，显示提示
        $("#"+tab_id).find("li.empty-item").removeClass("hide");
    }
    vue_obj.page += 1;
}


function get_tab_data(tab_id, page){
    $("#listLoading").removeClass('hide');
    var url = '{0}{1}/overview/get_event_data/{2}/{3}/{4}/{5}/'.format(site_url, cc_biz_id, tab_id, begin_time, end_time, page);
    return ajax_get(url, {}, render_tab_data(tab_id));
}


function ajax_get(url, params, callback) {
    $.get(url, params, callback, 'json');
}


function init_tab_vue(obj_id, items) {
    return new Vue({
        el: '#'+ obj_id,
        data: {
            items: items,
            tab_id: obj_id,
            has_more: false,
            page: 1,
        },
        methods: {
            load_more_data: function (event) {
                get_tab_data(this.tab_id, this.page);
            },
            query_alarm_detail: function (alarm_id){
                var url = '{0}{1}/alarm/{2}/'.format(site_url, cc_biz_id, alarm_id);
			    open_div(url);
                $('.iframe-mask').removeClass('hidden');
            }
        }
    });
}


$('#alert-list').find('.tab-pane').height($('.new-chart').outerHeight() - $('#alert-list > ul').outerHeight() - $('#alert-list').next().outerHeight() - 15);

$(window).resize(function(){
    setTimeout(function(){
        $('#alert-list').find('.tab-pane').height($('.new-chart').outerHeight() - $('#alert-list > ul').outerHeight() - $('#alert-list').next().outerHeight() - 15);
        $('[data-type="scrollList"]').mCustomScrollbar("update");
    }, 200);
});


// 初始化告警数量统计
var chart_header_vm = new Vue({
    el: '#chart_header',
    data: {
        days: '7',  // 默认最近7天
    },
    methods: {
        reload_chart: function (event) {
            // 获取到days
            var days = event.target.dataset.days;
            if(days != this.days){
                get_alarm_num_chart_data(days);
                this.days = days;
            }
        }
    }
});

// var myChart = echarts.init(document.getElementById('chart'));
// window.onresize = myChart.resize;

// 默认3天
get_alarm_num_chart_data(7);


function render_alarm_num_chart(days) {
    return function (res) {
        // $("#chartLoading").addClass('hide');
        hide_loading($("#chart"));
        if(res.result){
            // 初始化vue对象
            var data = res.data;
            var categories = get_categories(data, days);
            // 使用highchart
            $("#chart").highcharts({
                chart: {
                    type: 'areaspline'
                },
                xAxis: {
                    categories: categories,
                    tickmarkPlacement: 'on',
                    min: 0.5,
                    max: categories.length - 1.4,
                },
                yAxis: {
                    title: {
                        enabled: false
                    },
                    minPadding: 0,
                    maxPadding: 0,
                    min: 0,
                    minRange : 0.1,
                },
                plotOptions: {
                    areaspline: {
                        stacking: 'normal',
                        lineColor: '#666666',
                        lineWidth: 1,
                        softThreshold: false,
                        marker: {
                            lineWidth: 1,
                            lineColor: '#666666'
                        }
                    }
                },
                tooltip: {
                    shared: true
                },
                legend: {
                    reversed: true
                },
                series: [
                    {
                        name: '严重告警',
                        smooth: true,
                        data: get_data(data, '1', days),
                        color: '#ff6666',
                    },{
                        name: '普通告警',
                        smooth: true,
                        data: get_data(data, '2', days),
                        color: '#86b1ff',
                    },{
                        name: '轻微告警',
                        smooth: true,
                        data: get_data(data, '3', days),
                        color: '#999',
                    }
                ]
            });
        } else{
            alert_topbar("请求数据失败：" + res.message, "fail");
        }
    }
}


function show_loading(contain){
    contain.html('<img alt="loadding" src="'+static_url+'img/hourglass_36.gif" style="margin-top: 100px;margin-left:45%;">');
}

function hide_loading(contain){
    contain.html("");
}


function get_alarm_num_chart_data(days) {
    // [查询条件]统计周期 [day 按天统计|hour 按小时统计]
    var period = 'day';
    // [查询条件]聚合字段 按此字段group by, 例如按告警级别[level]
    var group_field = 'level';
    var url = '{0}{1}/overview/get_alarm_num_data/{2}/{3}/{4}/'.format(site_url, cc_biz_id, period, group_field, days);
    // myChart.showLoading();
    // $("#chartLoading").removeClass('hide');
    show_loading($("#chart"));
    ajax_get(url, {}, render_alarm_num_chart(days));
}


function get_data(data_dict, key, days) {
    if (key in data_dict){
        return dict_to_list(data_dict[key], 'alarm_cnt');
    } else{
        return new Array(parseInt(days)).fill(0);
    }
}

function get_categories(data_dict, days) {
    for (datas in data_dict){
        return dict_to_list(data_dict[datas], 'time_key');
    }
    return get_latest_days(days);
}

function get_latest_days(days) {
    var day = moment();
    var latest_days = [];
    for(var i=0; i<days; ++i){
        latest_days.push(day.format('YYYY-MM-DD'));
        day = day.subtract(1, 'days');
    }
    return latest_days.reverse();
}

function dict_to_list(datas, key) {
    var array = $.map(datas, function(value, index) {
        return value[key];
    });
    return array;
}

// Vue自定义过滤器
Vue.filter('get_operate_display', function (value) {
    switch(value){
        case 'create':
            return '新建';
        case 'delete':
            return '删除';
        case 'update':
            return '修改';
        default:
            return value;
    }
});

Vue.filter('get_strategy_type_display', function (value) {
    switch(value){
        case 'ip':
            return '主机IP';
        case 'strategy':
            return '告警策略';
        default:
            return value;
    }
});

Vue.filter('get_config_type_display', function (value) {
    switch(value){
        case 'Monitor':
            return '监控';
        case 'MonitorCondition':
            return '监控策略';
        case 'MonitorConditionConfig':
            return '触发条件';
        case 'AlarmDef':
            return '收敛/自动处理/通知方式';
        default:
            return value;
    }
});

Vue.filter('get_qq_avatar_url', function (value) {
    return 'https://q1.qlogo.cn/g?b=qq&nk={0}&s=100'.format(value);
});

Vue.filter('get_alarm_dimension_display', function (value) {
    // key是范围名 value是范围值，展示格式 key1(value1) and key2(value2)
    key_values = [];
    for(key in value){
        key_values.push('{0}({1})'.format(key, value[key]));
    }
    return key_values.join(' and ');
});

Vue.filter('get_alarm_level_class', function (value) {
    // 1：严重告警 2：普通告警 3：轻微告警
    switch (Number.parseInt(value)){
        case 1:
            return 'error';
        case 2:
            return 'update';
        case 3:
            return 'create';
        default:
            return '';
    }
});

Vue.filter('get_alarm_time_display', function (value) {
    // "2016-10-13T20:30:00" => 10-13 20:30
    return moment(value).format('MM-DD HH:mm');
});

Vue.filter('get_operate_desc', function (value) {
    return value.replace('\n', '<br/>');
});
$(document).ready(function(){
    // 检查url是否有参数
    query_params = get_query_params();
    var date;
    if(query_params!=undefined && query_params.monitor_id!=undefined && query_params.start_time!=undefined){
        // 从其他页面跳转，根据monitor_id，打开指定的告警
        flag = 'outside';  // 外部页面跳转
        date = moment(query_params.start_time);
    } else{
        date = moment();
        flag = 'normal';  // 正常打开
    }
    var curYear = date.year();
    var curMonth = date.month() + 1;
	$('#year').attr('data-value', curYear).text(curYear);
	$('#month').attr('data-value', curMonth).text(format_two_digits(curMonth));

	// 初始化日历
	var calendar = new Calendar({
		year: curYear,
		month: curMonth,
		datePosition: 'rightTop',
		// leftTopHTML: '<p class="date-info">解决率</p><p class="date-info" data-value="top-left">98%</p>',
		// leftBottomHTML: '<div class="alert-items-wrapper clearfix"><div class="alert-item slight">1</div><div class="alert-item normal">2</div><div class="alert-item serious">3</div></div>',
		preRenderCallback: function(){	//渲染前回调函数

		},
		postRenderCallback: function(){	//渲染后回调函数
			get_page_data();
		},
		allowHoverOnDisabled: function () {
			console.log('allowHoverOnDisabled');
		},
		hoverCallback: function(){
			var $this = $(this);
			// 判断是否有数据
			if($this.data('allow_tooltip')){
				var html = build_tooltip_html($this.data('date'));
				var itemRight = $this.width() * (6 - $this.index()) + 70;
				$this.append(html);
				var tips = $('#calendarTips');
				if(itemRight < tips.width()){
					tips.css({
						left: 'auto',
						right: '90%'
					});
					tips.find('.calendar-tips-left').hide();
					tips.find('.calendar-tips-right').show().css('borderLeftColor', tips.find('.calendar-tips-item:last').css('backgroundColor'));
				}
                                            else{
                                                tips.find('.calendar-tips-left').css('borderRightColor', tips.find('.calendar-tips-item:first').css('backgroundColor'))
                                            }
                                            tips.find('.calendar-tips-wrapper').css('width', tips.find('.calendar-tips-item').length * 120);
			}
		},
		outCallback: function(){
			$(this).find('#calendarTips').remove();
		},
		allowClickOnDisabled: function () {
			console.log('allowClickOnDisabled');
		},
		clickCallback: function() {
			var $this = $(this);
			// 判断是否有数据
			if($this.data('allow_tooltip')) {
                open_side_content($this.data('date'));
                $('body').css('overflow', 'hidden');
			}
		}
    });

	calendar.init();

      $(document).on('click', '#back_btn_id', function(){
          $('.iframe-mask').addClass('hidden');
      });

	// 加载告警数据
	get_page_data();

    if(flag=='outside'){
        // 外部跳转，打开侧边栏
        open_side_content(date.format('YYYY-MM-DD'));
    }


    // 打开侧边栏
    function open_side_content(calendar_date){
        var sideContent = $('#sideContent');
        sideContent.removeClass('hidden');
        getComputedStyle(document.querySelector('body')).display;
        sideContent.find('#close').addClass('open');
        sideContent.find('.side-content').addClass('open');
        sideContent.find('#side').removeClass('hidden');
        $('article.content').css('overflow', 'hidden');
        $('#listDate').text(calendar_date);

        // tab切换到告警事件
        $("a[href=#alert]").click();

        // 清空搜索框
        $('input[type=text].config__input').val('');

        // 隐藏没有数据提示
        $("div.empty-item").addClass("hide");

        // 初始vue对象，如果已有，则清空数据
        if (g_alarm_vue == undefined) {
            g_alarm_vue = init_alarm_vue();
        } else {
            //再次打开，页面恢复成正常模式
            flag = 'normal';
            update_alarm_vue();
        }
        // 加载告警事件列表
        get_alarm_data(1);

        // 初始事件列表vue对象
        build_operation_tab_data();
        if (g_operation_vue == undefined) {
            g_operation_vue = init_operation_vue();
        } else {
            update_operation_vue();
        }

        // 没有数据，显示提示
        if(g_operation_tab_list.length==0){
            $("#system").find("div.empty-item").removeClass("hide");
        }
    }


	//关闭侧边栏
	$('#close, #sideContent').on('click', function(event){
		if($(event.target).attr('data-type') == 'close'){
			var sideContent = $('#sideContent');
			sideContent.find('.side-content').removeClass('open').children('#side').addClass('hidden');
			sideContent.find('#close').removeClass('open');
			setTimeout(function(){
				sideContent.addClass('hidden');
    			$('article.content').css('overflow', 'auto');
                $('body').css('overflow', 'auto');
			}, 100);
		}
	});

	//事件列表切换
	$('[data-toggle="tab"]').on('click', function(){
		var $this = $(this);
		$this.children('button').addClass('current');
		$this.parent().siblings().each(function(){
			$(this).find('button').removeClass('current');
		});
		// 搜索框
		$($this.attr('href') + 'Search').removeClass('hidden').siblings('[data-type="search"]').addClass('hidden');
	});


	//浮层告警事件鼠标hover事件
	$(document).on('mouseenter', '.alert-event-item', function(){
		var $this = $(this),
			$html = $('<div class="inner-operation"><button type="button" data-type="alert-detail">告警详情</button></div>');

		$this.find('.inner-item').append($html);

		//告警详情事件绑定
		$html.find('[data-type="alert-detail"]').on('click', function(){
			// 告警详情展示
			var alarm_id = $(this).parents('div.alert-event-item').data('alarm_id');
			var url = '{0}{1}/alarm/{2}/'.format(site_url, cc_biz_id, alarm_id);
			open_div(url);
               $('.iframe-mask').removeClass('hidden');
		});
	}).on('mouseleave', '.alert-event-item', function(){
		$(this).find('.inner-operation').remove();
	});

    //绑定最近操作事件头像鼠标hover事件
    $('#system').on('mouseenter', '.item-img', function(){
        var $this = $(this);
        var html = '<div class="item-info" data-type="item-info">'+
                            '<p class="nickname">操作人: {0}</p>'+
                        '</div>';
        $this.append(html.format($this.data('name')));
    }).on('mouseleave', '.item-img', function(){
        $(this).find('[data-type="item-info"]').remove();
    });

	// 搜索事件：
	$("button.keyword-search").on('click', function(){
		var $input = $(this).prev('input[type=text]');
		filter_keyword($input);
	});

	$('input[type=text].config__input').bind('input', function() {
		filter_keyword($(this));
	});
});

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


// 原始数据列表
var g_alarm_list = [];
var g_operation_list = [];
// 日历所需数据
var g_alarm_calendar = {};
// tab列表所需数据
var g_alarm_tab_list = {};
var g_operation_tab_list = [];
// 告警事件vue对象
var g_alarm_vue;
// 操作事件vue对象
var g_operation_vue;
// 页面打开方式，normal、outside；outside表示外部页面跳转
var flag = 'normal';
// 查询参数
var query_params;


function get_page_data() {
	// 显示loading
	$("#listLoading").removeClass('hide');
	var begin_time = get_begin_time();
	var end_time = get_end_time();
	// var get_alarm_data_url = '{0}event_center/get_alarm_data/{1}/{2}/{3}/{4}/'.format(site_url, cc_biz_id, begin_time, end_time, 1);
	var get_alarm_num_url = '{0}{1}/event_center/get_alarm_num_data/{2}/{3}/{4}/{5}/'.format(site_url, cc_biz_id, 'day', 'level',  begin_time, end_time);
	var get_operation_data_url = '{0}{1}/overview/get_event_data/{2}/{3}/{4}/{5}/'.format(site_url, cc_biz_id, 'recentOperate', begin_time, end_time, 0);
	$.when(
		$.get(get_alarm_num_url, {}, render_calendar_data, 'json'),
		$.get(get_operation_data_url, {}, render_operation_data, 'json')
	).done(function () {
		// 获取日历所需的数据
		build_alarm_calendar();
		// 渲染日历数据
		render_calendar();
		// 关闭loading
		$("#listLoading").addClass('hide');
	});
}


function get_alarm_data(page){
    if(page==1){
	    $("#alarmLoading").removeClass('hide');
    } else{
        $("#loadAlertEvent").text("正在加载...");
    }
    if (g_alarm_vue.status_list.length == 0){
        return render_alarm_vue_data({
            result: true,
            data: []
        })
    }
    var url = '{0}{1}/event_center/get_alarm_data/'.format(site_url, cc_biz_id);
    // 一页50条数据
    var params = {
        page: page,
        page_size: 50,
        ordering: '-source_time',
        // 过滤需要的状态
        user_status__in: g_alarm_vue.status_list.join(",")
    };
    if(flag=='outside'){
        // 外部跳转
        params.alarm_attr_id = query_params.monitor_id;
        if(query_params.start_time!=undefined){
            params.source_time__gte = query_params.start_time;
        }
        if(query_params.end_time!=undefined){
            params.source_time__lte = query_params.end_time;
        }
        if(query_params.alarm_level!=undefined){
            params.level = query_params.alarm_level;
        }

    } else{
        var current_date = $('#listDate').text();
        params.source_time__gte = '{0} 00:00:00'.format(current_date);
        params.source_time__lte = '{0} 23:59:59'.format(current_date);
    }

    return ajax_get(url, {params:JSON.stringify(params)}, render_alarm_vue_data);
}


function render_alarm_vue_data(res) {
	$("#alarmLoading").addClass('hide');
    $("#loadAlertEvent").text("查看更多");
	if(res.result){
		append_data_to_alarm_vue(res.data);
	} else{
		alert_topbar("请求数据失败：" + res.message, "fail");
	}
}


function append_data_to_alarm_vue(data) {
    if(data.length < 50){
        g_alarm_vue.has_more = false;
    } else{
        g_alarm_vue.has_more = true;
    }
    if(data.length > 0){
        g_alarm_vue.src_items.push.apply(g_alarm_vue.src_items, data);
    }
    if(g_alarm_vue.page==1 && data.length==0 && g_alarm_vue.status_list.length == 3){
        $("#alert").find("div.empty-item").removeClass("hide");
    }
    g_alarm_vue.page += 1;
}


function render_calendar_data(res) {
	if(res.result){
		g_alarm_list = res.data;
	} else{
		alert_topbar("请求告警列表数据失败：" + res.message, "fail");
	}
}


function ajax_get(url, params, callback) {
    $.get(url, params, callback, 'json');
}


function render_calendar() {
	// 遍历日历元素
	var item_list = $("div.calendar-date-item");
	var begin_date = get_begin_time().split(' ')[0];
	var moment_date = moment(begin_date);
	for(var i=0; i<=item_list.length; ++i){
		var $item = $(item_list[i]);
		var current_date = moment_date.format('YYYY-MM-DD');
		var data = g_alarm_calendar[current_date];
		$item.data('date', current_date);
		if (data == undefined || data.total==0){
			$item.data('allow_tooltip', false);
			// 背景是灰色，数据清空
			$item.addClass('not-available');
			$item.find('div.calendar-date-leftTop').html('');
			$item.find('div.calendar-date-leftBottom').html('');
			$item.find('div.calendar-date-rightBottom').html('');
		} else{
			$item.data('allow_tooltip', true);
			// 背景变成白色，填充告警统计数据
			$item.removeClass('not-available');
			$item.find('div.calendar-date-leftBottom').html(build_alarm_total_html(data));
		}
		moment_date = moment_date.add(1, 'days');
	}
}


function build_tooltip_html(date) {
	var data = g_alarm_calendar[date];
	if(data==undefined){
		return '';
	}
	var html = '<div class="calendar-tips" id="calendarTips">'+
					'<div class="calendar-tips-left"></div>'+
						'<div class="calendar-tips-wrapper clearfix">'+
							build_alarm_html_by_level('slight', '轻微告警', data['3'])+
							build_alarm_html_by_level('normal', '普通告警', data['2'])+
							build_alarm_html_by_level('serious', '严重告警', data['1'])+
							build_operation_html('warning', '操作事件', data['0'])+
						'</div>'+
					'<div class="calendar-tips-right"></div>'+
				'</div>';
	return html;
}


function build_alarm_html_by_level(level, level_display, data) {
    if(data['total']==0){
        return '';
    } else{
        var html = '<div class="calendar-tips-item {0}">'+
					'<p class="title">{1} [{2}]</p>'+
					'<p class="subtitle">已通知 [{3}]</p>'+
					'<p class="subtitle">被收敛 [{4}]</p>'+
					'<p class="subtitle">被屏蔽 [{5}]</p>'+
				'</div>';
	    return html.format(level, level_display, data['total'], data['notified'], data['skipped'], data['shield']);
    }
}


function build_operation_html(level, level_display, data) {
    if(data['total']==0){
        return '';
    } else{
        var html = '<div class="calendar-tips-item {0}">'+
					'<p class="title">{1}[{2}]</p>'+
					'<p class="subtitle">新增 [{3}]</p>'+
					'<p class="subtitle">修改 [{4}]</p>'+
					'<p class="subtitle">删除 [{5}]</p>'+
				'</div>';
	    return html.format(level, level_display, data['total'], data['create'], data['update'], data['delete']);
    }
}


function build_alarm_total_html(data) {
	var html = '<div class="alert-items-wrapper clearfix">{0}{1}{2}{3}</div>';
	return html.format(
        build_alert_item(data['3']['total'], 'slight'),
        build_alert_item(data['2']['total'], 'normal'),
        build_alert_item(data['1']['total'], 'serious'),
        build_alert_item(data['0']['total'], 'warning')
    );
}


function build_alert_item(total, _class){
    if(total==0){
        return '';
    } else{
        return '<div class="alert-item {0}">{1}</div>'.format(_class, total);
    }
}


function build_alarm_calendar() {
	// 统计告警事件数据
	g_alarm_calendar = {};
	for(var level in g_alarm_list){
		var data_list = g_alarm_list[level];
		for(var i in data_list){
			var data = data_list[i];
			var date = data['time_key'];
			if(g_alarm_calendar[date]==undefined){
				g_alarm_calendar[date] = init_calendar_daily_data();
			}
			// 在这里获取状态的数据
			for(var status in data.status_cnts){
				g_alarm_calendar[date][level][status] += data.status_cnts[status];
			}
			g_alarm_calendar[date][level].total += data.alarm_cnt;
			g_alarm_calendar[date].total += data.alarm_cnt;
		}
	}

	// 统计操作事件数据
	for(var i in g_operation_list){
		var item = g_operation_list[i];
		var date = extract_date(item['operate_time'], ' ');
		if(g_alarm_calendar[date]==undefined){
			g_alarm_calendar[date] = init_calendar_daily_data();
		}
		g_alarm_calendar[date]['0'][item.operate] += 1;
		g_alarm_calendar[date]['0'].total += 1;
		g_alarm_calendar[date].total += 1;
	}

	// 计算解决率：本期不做
	// for (key in g_alarm_calendar){
	// 	g_alarm_calendar[key].resolved_rate = compute_resolved_rate(g_alarm_calendar[key]);
	// }
}


function init_calendar_daily_data() {
	return {
		'0': {'total': 0, 'create': 0, 'update': 0, 'delete': 0},  // 操作事件
		'1': {'total': 0, 'skipped': 0, 'shield': 0, 'notified': 0},  // 严重告警
		'2': {'total': 0, 'skipped': 0, 'shield': 0, 'notified': 0},  // 普通告警
		'3': {'total': 0, 'skipped': 0, 'shield': 0, 'notified': 0},  // 轻微告警
		'total': 0,  // 总数，用于判断是否有事件
	};
}


function compute_resolved_rate(data) {
	// 计算规则暂定(总数-未处理)/已处理？
	var total = 0;
	var unresolved_total = 0;
	for(key in data){
		total += data[key].total;
		// 未处理的键值
		unresolved_total += data[key].unresolved;
	}
	return 100 - parseInt(unresolved_total/total * 100);
}


function extract_date(dt, delimiter) {
	return dt.split(delimiter)[0];
}


function get_begin_time() {
	var year = get_calendar_year();
	var month = get_calendar_month();
	var first_day = moment('{0}-{1}-01'.format(year, month));
	var begin_day = first_day.subtract(get_week_day(first_day) - 1, 'days').format('YYYY-MM-DD');
	return '{0} 00:00:00'.format(begin_day);
}


function get_end_time() {
	var year = get_calendar_year();
	var month = get_calendar_month();
	var last_day = moment('{0}-{1}-01'.format(year, month)).endOf('month');
	var end_day = last_day.add(7 - get_week_day(last_day), 'days').format('YYYY-MM-DD');
	return '{0} 23:59:59'.format(end_day);
}


function get_calendar_year() {
	return $("#calendarYear").text();
}


function get_calendar_month() {
	return $("#calendarMonth").text();
}


function get_week_day(moment_obj) {
	return moment_obj.days()==0 ? 7 : moment_obj.days();
}

// 告警事件列表
// time: [{
// 		title:
// 		alarm_dimension:
// 		content:
// 		status:
// 	}]
function build_alarm_tab_data() {
	var current_date = $('#listDate').text();
	g_alarm_tab_list = {};
	for(var i in g_alarm_list){
		var data = g_alarm_list[i];
		var date = data['source_time'].split('T')[0];
		if(date==current_date){
			var time = extract_alarm_time(data['source_time']);
			if(g_alarm_tab_list[time]==undefined){
				g_alarm_tab_list[time] = [];
			}
			g_alarm_tab_list[time].push(data);
		} else if(date>current_date){
			break;
		}
	}
}

// 操作事件列表
function build_operation_tab_data() {
	var current_date = $('#listDate').text();
	g_operation_tab_list = [];
	for(var i in g_operation_list){
		var data = g_operation_list[i];
		var date = extract_date(data['operate_time'], ' ');
		if(date==current_date){
			g_operation_tab_list.push(data);
		} else if(date<current_date){
			break;
		}
	}
}

// 2016-10-13T20:30:00 -> 20:30
// 2016-10-13T20:20:00 -> 20:00
function extract_alarm_time(dt) {
	var m = moment(dt);
	return '{0}:{1}'.format(m.hour(), m.minute()<30 ? '00' : '30');
}


function init_alarm_vue() {
    return new Vue({
        el: '#alert',
        data: {
            src_items: [],
            status_list: ['notified', 'skipped', 'shield'],
			keyword: '',
			has_more: false,
			page: 1,
        },
		computed: {
			// 一个计算属性的 getter
			items: function () {
				var target_data = {};
				var filter_result = filter_alarm_data(this.src_items, this.status_list, this.keyword);
				// 按时间聚合
				for(var i in filter_result){
					var data = filter_result[i];
					var time = extract_alarm_time(data['source_time']);
					if(target_data[time]==undefined){
						target_data[time] = [];
					}
					target_data[time].push(data);
				}
				return sort_dict(target_data);
			},
            no_search_items: function() {
                return this.src_items.length>0 && Object.keys(g_alarm_vue.items).length==0;
            },
            show_more_button: function(){
                return this.has_more && Object.keys(g_alarm_vue.items).length>0;
            }
		},
        methods: {
            load_more_data: function (event) {
                get_alarm_data(this.page);
            }
        },
        watch:{
            status_list: function(val, oldVal){
                this.page = 1;
                get_alarm_data(this.page);
            }
        }
    });
}


function sort_dict(dict){
    var keys = Object.keys(dict);
    keys.sort().reverse();
    var sorted_dict = {};
    for (var i=0; i<keys.length; i++) { // now lets iterate in sort order
        var key = keys[i];
        var value = dict[key];
        sorted_dict[keys[i]] = dict[key];
        /* do something with key & value here */
    }
    return sorted_dict;
}


function update_alarm_vue() {
	g_alarm_vue.src_items = [];
	g_alarm_vue.status_list = ['notified', 'skipped', 'shield'];
	g_alarm_vue.keyword = '';
	g_alarm_vue.has_more = false;
	g_alarm_vue.page = 1;
}


function filter_alarm_data(data_list, status_list, keyword) {
	return $.map(data_list, function(value, index) {
		if(status_list.indexOf(value.status) != -1 &&
			(keyword=='' || JSON.stringify(value.alarm_content).indexOf(keyword)!=-1))
        return value;
    });
}


function filter_operation_data(data_list, status_list, keyword) {
	return $.map(data_list, function(value, index) {
		if(status_list.indexOf(value.operate) != -1 &&
			(keyword=='' || value.operate_desc.indexOf(keyword)!=-1))
        return value;
    });
}


function init_operation_vue() {
    return new Vue({
        el: '#system',
        data: {
            src_items: g_operation_tab_list,
			status_list: ['create', 'update', 'delete'],
			keyword: '',
            has_more: false,
            page: 0,
        },
		computed: {
			// 一个计算属性的 getter
			items: function () {
				return filter_operation_data(this.src_items, this.status_list, this.keyword);
			},
            no_search_items: function() {
                return this.src_items.length>0 && this.items.length==0;
            }
		}
    });
}


function update_operation_vue() {
	g_operation_vue.src_items = g_operation_tab_list;
	g_operation_vue.status_list = ['create', 'update', 'delete'];
	g_operation_vue.keyword = '';
	g_operation_vue.has_more = false;
	g_operation_vue.page = 0;
}


function get_operation_data(){
    var url = '{0}{1}/overview/get_event_data/{2}/{3}/{4}/{5}/'.format(site_url, cc_biz_id, 'recentOperate', get_begin_time(), get_end_time(), 0);
    return ajax_get(url, {}, render_operation_tab);
}


function render_operation_data(res) {
	console.log('render_operation_tab');
	if(res.result){
		g_operation_list = res.data;
	} else{
		alert_topbar("请求操作事件列表数据失败：" + res.message, "fail");
	}
}


function append_data_to_operation_vue(data) {
    if(data.length < 10){
        g_operation_vue.has_more = false;
    } else{
        g_operation_vue.has_more = true;
    }
    if(data.length > 0){
        g_operation_vue.src_items.push.apply(g_operation_vue.src_items, data);
    }
    g_operation_vue.page += 1;
}

function format_two_digits(num) {
	return ('0' + num).slice(-2);
}


function filter_keyword($input) {
	var keyword = $input.val();
	switch($input.attr('name')){
		case 'alertSearch':
			g_alarm_vue.keyword = keyword;
			break;
		case 'systemSearch':
			g_operation_vue.keyword = keyword;
			break;
		default:
			break;
	}
}


/* 获取url查询参数
@return:
{
	key_1: value_1,
	key_2: value_2,
}
*/
function get_query_params() {
  var query_string = {};
  var query = window.location.search.substring(1);
  var params = query.split("&");
  for(var i=0; i<params.length; ++i) {
    var key_value = params[i].split("=");
    if(key_value.length==2){
    	query_string[key_value[0]] = decodeURIComponent(key_value[1]);
    }
  }
  return query_string;
}

// Vue 过滤器
function filter_alarm_dimension(value){
	key_values = [];
    for(key in value){
        key_values.push('{0}({1})'.format(key, value[key]));
    }
    return key_values.join(' and ');
}

Vue.filter('get_alarm_dimension_display', filter_alarm_dimension);

Vue.filter('get_operate_time_display', function (value) {
	var m = moment(value);
	return '{0}:{1}'.format(format_two_digits(m.hour()), format_two_digits(m.minute()));
});

Vue.filter('get_qq_avatar_url', function (value) {
    return 'https://q1.qlogo.cn/g?b=qq&nk={0}&s=100'.format(value);
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

// Vue自定义过滤器
Vue.filter('get_operate_display', function (value) {
    switch(value){
        case 'create':
            return '新增';
        case 'delete':
            return '删除';
        case 'update':
            return '修改';
        default:
            return value;
    }
});

// Vue自定义过滤器
Vue.filter('get_alarm_level_class', function (value) {
    switch(parseInt(value)){
        case 1:
            return 'alert-event-serious';
        case 2:
            return 'alert-event-normal';
        case 3:
            return 'alert-event-slight';
        default:
            return value;
    }
});

// Vue自定义过滤器
Vue.filter('get_alarm_status_class', function (value) {
    switch(value){
        case 'skipped':
            return 'fa-ban';
        case 'shield':
            return 'fa-bell-slash-o';
        case 'notified':
            return 'fa-check-circle-o';
        default:
            return value;
    }
});


Vue.filter('get_operate_desc', function (value) {
    return value.replace('\n', '<br/>');
});

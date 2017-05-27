/**
 * Created by willgchen on 2016/9/23.
 */
try{
// Highcharts theme
Highcharts.setOptions(Highcharts.theme_default);
}catch(e){}
Date.prototype.yyyymmdd = function() {
    var month = '' + (this.getMonth() + 1),
        day = '' + this.getDate(),
        year = this.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
};

Array.range= function(a, b, step){
    var A= [];
    if(typeof a== 'number'){
        A[0]= a;
        step= step || 1;
        while(a+step<= b){
            A[A.length]= a+= step;
        }
    }
    else{
        var s= 'abcdefghijklmnopqrstuvwxyz';
        if(a=== a.toUpperCase()){
            b=b.toUpperCase();
            s= s.toUpperCase();
        }
        s= s.substring(s.indexOf(a), s.indexOf(b)+ 1);
        A= s.split('');
    }
    return A;
};


var count_per_page_alarms = 3,
    count_per_page_graph = 4;

var hosts_view,
    need_access = false,
    hosts = [],
    sets = [],
    mods = [],
    current_page = 1,
    current_strategy_page = 1,
    sideContent = $('#sideContent'),
    hosts_paging_footer = $("#hosts-paging-footer"),
    alarms_paging_footer = $("#alarms-paging-footer"),
    alarm_strategy_paging_footer = $("#alarm_strategy_paging_footer"),
    single_graph_paging_footer = $("#single_graph_paging_footer"),
    multiple_graph_paging_footer = $("#multiple_graph_paging_footer"),
    update_time_span = $("#update_time"),
    set_selector = $("#set-select2"),
    mod_selector = $("#mod-select2"),
    property_selector = $("#property-select2"),
    ip_filter_selector = $("#ip-filter"),
    status_selector = $("#status-select2"),
    plat_info = {},
    eth_info = {};

function init(){
    init_select2();
    init_ip_filter_event();
    init_order_table();
    init_datepicker_input();
    refresh_sets_info();
    refresh_property_list();
    init_vue();
    init_host_index_info();
    refresh_host_info();
    refresh_plat_info();
    bind_event();
}

function init_datepicker_input(){
    var today = new Date();

    $('input.time-picker').kendoDatePicker({
        max: today,
        min: new Date(new Date().setDate(new Date().getDate() - 30)),
        value : today,
        format : "yyyy-MM-dd"
    });
    // 刷新性能图表
    $("#single_graph_date").change(function(){
        if (!hosts_view.checked_host) return;
        render_single_host_bp_graph()
    });

    $("#multiple_graph_date").change(function(){
        render_multiple_host_bp_graph();
    });

    // 拉取告警列表
    $("#alarm_date").change(function(){
        if (!hosts_view.checked_host) return;
        render_alarms(hosts_view.checked_host.id)
    })
}

function init_vue(){
    hosts_view = new Vue({
        el: '#bp_index',
        data: {
            first_open: true,   // 页面首次开启标识
            hosts: [],          // 主机列表
            group_by: "",       // 分类属性名，默认为空，表示不分类
            group_hosts: [],    // 按属性分类的主机列表
            checked_host: null, // 当前焦点主机
            checked_host_alarms: [], // 当前焦点主机对应的告警事件
            checked_host_alarms_table: [], // 当前焦点主机对应的告警事件分页展示
            checked_host_alarm_strategy: [], // 当前焦点主机对应的告警策略
            checked_host_alarm_strategy_table: [], // 当前焦点主机对应的告警策略分页展示
            host_index_list: [],    // 所有性能指标信息
            checked_host_index_table: [], // 当前焦点主机性能指标信息分页展示，指标信息是通用的，切换焦点主机不会引起变化
            multiple_host_index_table: []   // 多选主机的性能指标信息分页展示，指标信息是单选。
        },
        computed:{
            plat_name_display: function(){
                return this.checked_host?plat_info[this.checked_host.Source] || "空":""
            },
            selected_host_list: function(){
                // 选中的主机id列表
                var _selected_host_list = [],
                    _selected_host_id_list = [],
                // 此处引用vue的数据，确保该属性在this.hosts变更后会被更新。
                    _ = this.hosts.length;
                for (var i = 0, len = hosts.length; i < len; i++) {
                    if (hosts[i].checked && _selected_host_id_list.indexOf(hosts[i].id) < 0){
                        _selected_host_id_list.push(hosts[i].id);
                        _selected_host_list.push(hosts[i])
                    }
                }
                return _selected_host_list
            },
            host_index_info: function(){
                // 主机性能指标信息, 用于渲染多选主机后的指标span
                var category_list = [];
                var category_index_des_info = {};
                var _host_index_info = {};
                for (var i= 0, len=this.host_index_list.length; i < len; i++){
                    var host_index = this.host_index_list[i];
                    if (category_list.indexOf(host_index.category) < 0){
                        _host_index_info[host_index.category] = [];
                        category_index_des_info[host_index.category] = [];
                        category_list.push(host_index.category);
                    }
                    if (category_index_des_info[host_index.category].indexOf(host_index.description) < 0){
                        category_index_des_info[host_index.category].push(host_index.description);
                        _host_index_info[host_index.category].push(host_index);
                    }
                }
                return _host_index_info;
            },
            agent_status_display: function(){
                // 主机agent状态展示
                if (this.checked_host && ("agent_status" in this.checked_host)){
                    switch(this.checked_host.agent_status){
                        case 0:
                            return "ON";
                            break;
                        case 1:
                            return "OFF";
                            break;
                        case 2:
                            return "未安装 <a href='/o/bk_agent_setup/install/?biz_id="+cc_biz_id+"&host_id="+this.checked_host.id+"&from_app="+app_code+"' target='_blank'>点击安装</a>";
                            break;
                        case 3:
                            return "数据未上报 <a href='###' onclick='data_access_single(this)'>点击接入</a>";
                            break;
                        default:
                            return "未知";
                    }
                }
                return "loading..."
            },
            checked_host_alarms_count_info: function(){
                // 主机告警事件信息
                var count_info = {
                    1: 0, 2: 0, 3:0
                };
                for (var i= 0, len = this.checked_host_alarms.length; i < len; i++){
                    var alarm = this.checked_host_alarms[i];
                    count_info[alarm.level] += 1
                }
                return count_info
            }
        },
        methods: {
            alarm_filter: function(event, level){
                if ($(event.target).hasClass("active")){
                    $(".title-badge").removeClass("active")
                    move_page_to_alarms(1)
                }else{
                    $(".title-badge").removeClass("active")
                    $(event.target).addClass("active")
                    move_page_to_alarms(1, level)
                }
            },
            host_index_selected: function(target){
                //批量查看时指标选择
                var $this = $(target),
                    $options = $('#selectors').find('a'),
                    value = $this.attr('data-index_id');

                $options.each(function(){
                    var _this = $(this);

                    if(value != _this.attr('data-index_id')){
                        _this.removeClass('king-primary');
                    }
                    else{
                        _this.addClass('king-primary');
                    }
                });

                render_multiple_host_bp_graph();
            },
            multiple_hosts_graph_btn_click: function(event){
                // 点击批量查看按钮
                if(!$(event.target).attr('disabled')){
                    displaySideContent('multiple');
                }
                // 当前所选主机及对应指标的性能图表分页展示
                render_multiple_host_bp_graph();
            },
            alert_tooltips: function(event, host){
                //初始化告警状态tips
                var $this = $(event.target);
                //todo 在这里拉取host处理条数的信息
                //$this.tooltip({
                //    title: '<p style="margin-top:10px;">未处理：0</p><p>已处理：0</p>',
                //    html: true,
                //    container: 'body'
                //}).tooltip('show');
            },
            stick_tooltips: function(event){
                // 置顶按钮tooltip展示
                var $this = $(event.target),
                    isTop = $this.parents('tr').attr('data-type');
                $this.tooltip({
                    title: isTop ? '取消置顶' : '置顶'
                }).tooltip('show');
            },
            stick_tooltips_destroy: function(event){
                // 置顶按钮tooltip消失
                $(event.target).tooltip( "destroy" );
            },
            stick_icon_click: function(event, host){
                // 点击置顶按钮
                var $this = $(event.target),
                    isTop = $this.parents('tr').attr('data-type');
                isTop ? cancel_stick_host(host.id) : stick_host(host.id);
            },
            show_cpu_single_usage: function(event, host){
                //鼠标指向圆环进度条，显示详情
                var $this = $(event.target),
                    subHtml = '';

                for(var i = 0; i < host.cpu_single_usage.val.length; i++){
                    var item = host.cpu_single_usage.val[i],
                        type,html;
                    var key = Object.keys(item)[0];
                    var val = item[key].toFixed(2);
                    if(val < 50){
                        type = 'success';
                    }
                    else if(val < 80){
                        type = 'warning';
                    }
                    else if(val <= 100){
                        type = 'error';
                    }

                    subHtml += '<div class="clearfix">'+
                                    '<span class="title pull-left">'+ key +'</span>'+
                                    '<div class="king-progress-box clearfix pull-left">'+
                                        '<div class="progress king-progress">'+
                                            '<div class="progress-bar '+type+'" role="progressbar" style="width: '+val+'%;"></div>'+
                                        '</div>'+
                                    '</div>'+
                                '</div>'
                }

                html = '<div class="cpu-detail">'+
                            '<p>单核CPU使用率</p>'+
                                subHtml+
                            '<div class="ruler clearfix">'+
                                '<canvas data-type="indicator"></canvas>'+
                                '<div class="pull-left indicator percentage0">'+
                                    '0'+
                                '</div>'+
                                '<div class="pull-left indicator percentage25">'+
                                    '25'+
                                '</div>'+
                                '<div class="pull-left indicator percentage50">'+
                                    '50'+
                                '</div>'+
                                '<div class="pull-left indicator percentage75">'+
                                    '75'+
                                '</div>'+
                                '<div class="pull-left indicator percentage100">'+
                                    '100'+
                                '</div>'+
                            '</div>'+
                        '</div>';

                $this.tooltip({
                    html: true,
                    title: html,
                    placement: 'right'
                });
                $this.tooltip('show');
                getComputedStyle(document.querySelector('#panelBody')).display;
                var c = $this.next().find('canvas')[0],
                    context = c.getContext('2d');
                context.fillStyle = '#fff';
                context.strokeStyle = '#fff';
                context.lineWidth = 2;
                context.beginPath();
                context.moveTo(0, 10);
                context.lineTo(300, 10);
                context.moveTo(0, 10);
                context.lineTo(0, 60);
                context.moveTo(75, 10);
                context.lineTo(75, 60);
                context.moveTo(150, 10);
                context.lineTo(150, 60);
                context.moveTo(225, 10);
                context.lineTo(225, 60);
                context.moveTo(300, 10);
                context.lineTo(300, 60);
                context.stroke();
            },
            status_class: function(status){
                // 状态展示对应的class
                switch (status){
                    case 0:
                        return "normal";
                        break;
                    case 1:
                    case 2:
                    case 3:
                        return "error";
                        break;
                    default:
                        return "default";
                        break

                }
            },
            checkbox_check: function(event, host){
                // 主机checkbox点击
                var $this = $(event.target);
                host.checked = !host.checked;
                host.checked?$this.iCheck('check'):$this.iCheck('uncheck');
            },
            on_tr_click: function(event, host){
                // 查看主机详细信息
                if(!$(event.target).parents('[data-type="toTop"]').length){	//点击的不是置顶按钮才弹出侧边栏
                    host.agent_status = null;
                    delete host["agent_status"];
                    this.checked_host = Object.assign({}, host, {});
                    get_agent_status_by_hostid(host.id);
                    displaySideContent('single');
                    //// 默认渲染基础性能图表
                    //render_single_host_bp_graph();
                    render_component_graph("System");
                    // 拉取关联告警策略信息
                    render_alarm_strategy(this.checked_host.id);
                    // 拉取告警事件列表
                    var today = new Date();
                    $("#alarm_date").val(today.yyyymmdd()).trigger("change");
                }
            },
            on_component_span_click: function(event, host){
                // 主机详细信息组件span被点击
                var $this = $(event.target);
                if ($this.hasClass('selected')){
                    return;
                }
                //更新监控服务视图数据
                $this.addClass('selected').siblings().removeClass('selected');
                render_component_graph($this.text());
            },
            add_alarm_strategy: function(event, strategy){
                // 新增/编辑告警策略
                var i_icon = $(event.target);
                if (i_icon.hasClass("disabled")) return;
                i_icon.addClass("disabled");
                open_div(site_url + cc_biz_id + '/bp/config/performance/' + strategy.id + '/');
                $(".side-content").css('overflow', "hidden");
                on_div_close = function(){
                    i_icon.removeClass("disabled");
                    $("#iframe_body").css({
                        'height': 0
                    });
                    $(".side-content").css('overflow', "auto");
                };
            },
            add_monitor: function(event, multiple){
                if ($(event.target).attr("disabled") == "disabled"){
                    return
                }
                open_div(site_url + cc_biz_id + '/bp/config/performance/0/' + (multiple?"?multiple=1":""));
                // 禁用外部滚动条
                $(window).scrollTop(0);
                $("body").css({'overflow-y': 'hidden'});
                on_div_close = function(){
                    $("#iframe_body").css({
                        'height': 0
                    });
                    // 还原外部滚动条
                    $("body").css({'overflow-y': 'auto'});
                };
            },
            del_alarm_strategy: function(event, strategy){
                // 删除告警策略
                var i_icon = $(event.target);
                del_alarm_strategy(i_icon, strategy.id, 'quick', function(){
                    render_alarm_strategy(hosts_view.checked_host.id);
                });
            },
            toggle_group_hosts: function(val){
                for (var i= 0, len=this.group_hosts.length; i<len;i++){
                    var _host = this.group_hosts[i];
                    var _attr_val = _host[this.group_by];
                    _attr_val = _attr_val || "空";
                    if (_attr_val == val){
                        _host._is_show =  !_host._is_show;
                    }
                }
                move_page_to_hosts(current_page);
            },
            access_all: function(event){
                self = event.target;
                debugger
                if ($(self).prop("disabled")) return;
                $(self).attr('disabled', 'disabled');
                $(self).html("批量采集上报<i class='fa fa-spinner fa-pulse mr5'></i>");
                var host_id_list = [];
                for (var j= 0, leng=hosts_view.selected_host_list.length; j<leng;j++){
                    host_id_list.push(hosts_view.selected_host_list[j].id);
                }
                $.post(site_url+cc_biz_id+'/'+'bp/access/', {hostid_list: host_id_list.join(",")}, function(res){
                    $(self).removeAttr('disabled');
                    $(self).html("批量采集上报");
                    if(res.result){
                        alert_topbar("操作成功，10-20分钟后刷新此页面即可查看到主机数据，请耐心等待！", "success", 6000);
                    }else{
                        alert_topbar(res.message, "fail", 10000);
                    }
                }, 'json');
            }
        },
        watch: {
            'group_by': function (val, oldVal){
                for (var i= 0,len=hosts.length;i<len;i++){
                    hosts[i]._is_show = true;
                }
                move_page_to_hosts(current_page);
            },
            'host_index_info': function(val, oldVal){
                // init_host_index_info 后被调用
                if (this.host_index_list.length > 0){
                    // 初始化默认选中第一项
                    hosts_view.host_index_selected($('#selectors').find('a').first()[0]);
                }
            },
            'hosts': function(val, oldVal){
                // refresh_host_info 后被调用
                //初始化表格中的进度条
                $('[data-type="chart-error"]').easyPieChart({
                    barColor: '#ff6666',
                    scaleColor: false,
                    size: 32,
                    animate: 1000
                });
                $('[data-type="chart-normal"]').easyPieChart({
                    barColor: '#46c37b',
                    scaleColor: false,
                    size: 32,
                    animate: 1000
                });
                //init_host_checkbox();
                setTimeout(function(){init_host_checkbox();}, 1);

            },
            'multiple_host_index_table': function(val, oldVal){
                // 多选主机性能图表分页后被调用
                if (this.multiple_host_index_table.length > 0){
                    make_multiple_graphs();
                }
            },
            'checked_host_index_table': function(val, oldVal){
                // 单机性能详情页点击图表分页后被调用
                if (this.checked_host_index_table.length > 0 && this.checked_host){
                    make_single_graphs();
                }
            },
            'checked_host_alarm_strategy_table': function(val, oldVal){
                // 单机性能详情页点击关联策略分页后被调用
                $("div.switch").bootstrapSwitch('destroy');
                $("input[name=status]").wrap('<div class="switch switch-mini mr10" data-on="success" data-on-label="ON" data-off-label="OFF"/>').parent().bootstrapSwitch();
                // 事件绑定， 启用/禁用告警策略
                $("div.switch").on('switch-change', function(e, data){
                    $("#alarms_strategy_table_loading").removeClass("hidden");
                    var strategy_id = $(e.target).closest("tr").attr("data-id");
                    //console.log(strategy_id, data.value);
                    $.post(site_url + cc_biz_id + '/config/operate_alram/'+strategy_id+'/',
                        {is_enabled: data.value?1:0},
                        function(res){
                            if (res.result){
                                alert_topbar("操作成功", "success");
                                $("#alarms_strategy_table_loading").addClass("hidden");
                            }else{
                                alert_topbar("操作失败："+res.message, "fail");
                                render_alarm_strategy(hosts_view.checked_host.id);
                            }
                        }
                        , 'json')
                });
            }

        }
    });
}


function submit_strategy_data_quick(param, alram_strategy_id, is_auto){
    // 快速编辑告警策略并保存
    var url = site_url + cc_biz_id +'/config/strategy_save_quick/'+alram_strategy_id+'/';
    var s_id = $.trim($("#edit_s_id").val());
    $.post(url,{
        's_id': s_id,
        'param': JSON.stringify(param)
    }, function(feedback){
        $("#submit_stragegy").html('确定');
        if (feedback.result){
            alert_topbar(feedback.message, "success");
            // 关闭当前的 弹出框
            var d = dialog({id: 'add_alarm_strategy'});
            d.close().remove();
            render_alarm_strategy(hosts_view.checked_host.id);
        }else{
            // 提示错误信息
            $("#tip_all").text(feedback.message);
            $("#submit_stragegy").attr("disabled", false);
        }
    }, 'json');
}

function init_order_table(){
	//指向/点击可排序的列
	$(document).on('mouseover', '[data-type="condition"]', function(){
		var $this = $(this);

		$this.find('i').css('color', '#666').removeClass('visibility-hidden');
		$this.siblings().find('i').removeClass('visibility-hidden');
	}).on('mouseout', '[data-type="condition"]', function(){	//鼠标移开时
		var $this = $(this);

		if(!$this.attr('data-value')){		//若未排序，恢复样式
			$this.find('i').css('color', '#bbb').addClass('visibility-hidden');
		}
		$this.siblings().not('[data-value]').find('i').addClass('visibility-hidden');
	}).on('click', '[data-type="condition"]', function(){
		var $this = $(this),
			value = $this.attr('data-value');

		if(value){	//若已排序

			if(value == 'desc'){	//已降序
				$this.attr('data-value', 'asc');
				$this.find('i').removeClass('desc').addClass('asc');
				$this.find('i').css('color', '#666');
			}
			else{		//已升序
				$this.removeAttr('data-value');
				$this.find('i').removeClass('ordered').removeClass('desc').removeClass('asc');
				$this.siblings().find('i').removeClass('ordered').removeClass('desc').removeClass('asc');
				$this.find('i').css('color', '#bbb');
			}
		}
		else{		//若未排序
			$this.find('i').addClass('ordered').addClass('desc');
			$this.siblings().find('i').removeClass('ordered').removeClass('desc').removeClass('asc');
			$this.attr('data-value', 'desc').siblings().removeAttr('data-value');
			$this.find('i').css('color', '#666');
			$this.siblings().find('i').css('color', '#bbb');
		}
        move_page_to_hosts(current_page);
	});
}

function init_host_checkbox(){
	// 初始化 host 列表的checkbox
	$('input[name="item"][id!="select_all"]').iCheck({
		checkboxClass: 'icheckbox_minimal-blue'
	}).on('ifChecked', function(){
        var host_id = $(this).attr("data-host_id");
        update_hosts(host_id, "checked", true);
	}).on('ifUnchecked', function(){
        var host_id = $(this).attr("data-host_id");
        update_hosts(host_id, "checked", false);
	});

	// 全选
	$('#select_all').iCheck({
		checkboxClass: 'icheckbox_minimal-blue'
	}).on('ifChecked', function(){
		$('#panelBody').find('input[name="item"]').each(function(){
			$(this).iCheck('check');
		});
	}).on('ifUnchecked', function(){
		$('#panelBody').find('input[name="item"]').each(function(){
			$(this).iCheck('uncheck');
		});
	});
}

function update_check_all_checkbox(){
    var len = hosts_view.hosts.length;
    var checked_all = len!=0;
    for (var i= 0; i<len; i++){
        checked_all = hosts_view.hosts[i].checked && checked_all;
    }
    $('#select_all').prop("checked", checked_all).iCheck("update");
}


function update_host_alarm_count_info(){
    var len = hosts_view.hosts.length;
    if (len==0){return}
    var host_id_list = [];
    for (var i= 0; i<len; i++){
        host_id_list.push(hosts_view.hosts[i].id);
    }
    var host_ids = host_id_list.join(",");
    var today = new Date();
    var alarm_date = today.yyyymmdd();
    $.get(site_url + cc_biz_id + '/bp/get_alarm_count/', {host_id_list:host_ids, alarm_date:alarm_date}, function(res){
        if (res.result){
            var alarm_count_info = res.data.alarm_count_info;
            for (var i= 0; i<len; i++){
                var alarm_count = alarm_count_info[hosts_view.hosts[i].id];
                if (alarm_count){
                    var low = alarm_count["3"]?alarm_count["3"]["alarm_cnt"]:0;
                    var middle = alarm_count["2"]?alarm_count["2"]["alarm_cnt"]:0;
                    var high = alarm_count["1"]?alarm_count["1"]["alarm_cnt"]:0;
                    hosts_view.hosts[i].alarm.level = [low, middle, high];
                }
            }
        }
    }, 'json');
}


function stick_host(hostid){
    // 置顶
    $.post(site_url + cc_biz_id + '/bp/stick_host/', {host_id:hostid, action:"add"}, function(res){
        if (res.result){
            update_hosts(hostid, "is_stickied", res.data)
        }
    }, 'json');
    update_hosts(hostid, "is_stickied", 1024*1024)
}

function cancel_stick_host(hostid){
    // 取消置顶
    $.post(site_url + cc_biz_id + '/bp/stick_host/', {host_id:hostid, action:"del"}, function(res){
        if (res.result){
            update_hosts(hostid, "is_stickied", res.data)
        }
    }, 'json');
    update_hosts(hostid, "is_stickied", 0)
}

function update_hosts(hostid, key, val){
    // 更新hosts队列中的host
    for (var i= 0, host_len = hosts.length;i<host_len; i++){
        var _host = hosts[i];
        if (_host.id == hostid){
            _host[key] = val;
        }
    }
    move_page_to_hosts(current_page);
}

function init_select2(){
    set_selector.select2({
        data: sets,
        placeholder: "加载中...",
        language: "zh-CN"
    }).change(function (e) {
        // 集群选择触发事件
        // 处理当set_id='-1'，或者没有选中的情况
        var set_data = set_selector.select2("data");
        if (set_data == null || set_data.id == '-1') {
            mod_selector.select2({
                data: mods,
                placeholder: "请选择模块",
                language: "zh-CN"
            });
            return false;
        }
        // 查找SET下的模块
        var set_id = set_selector.select2("data").id;
        refresh_mods_info(set_id);
        move_page_to_hosts(current_page);
    });
    mod_selector.select2({
        data: mods,
        placeholder: "加载中...",
        language: "zh-CN"
    }).change(function (e) {
        move_page_to_hosts(current_page);
    });

    property_selector.select2({
        data: [],
        placeholder: "不分组",
        language: "zh-CN"
    });

    status_selector.select2({
        data: [{id:"", text:"全部"}, {id:0, text:"正常"}, {id:2, text:"Agent未安装"}, {id:3, text:"数据未上报"}],
        placeholder: "全部状态",
        language: "zh-CN"
    }).change(function (e) {
        move_page_to_hosts(current_page);
    });

}

function init_ip_filter_event(){
    ip_filter_selector.keyup(function(){
        move_page_to_hosts(current_page);
    })
}

function init_host_index_info(){
    // 拉取性能展示配置
    $.get(site_url + cc_biz_id + '/'+'bp/host_index_list/', {}, function(res){
        if (res.result){
            hosts_view.host_index_list = res.data;
            if (checkhost_id && hosts.length>0){
                open_host_detail(checkhost_id)
                checkhost_id = null;
            }
        }else{
            hosts_view.host_index_list = [];
        }
    }, "json");
    $.get(site_url + cc_biz_id + '/'+'get_eth_info/', {}, function(res){
        eth_info = res.data;
    }, "json");
}


function open_host_detail(host_id){
    for (var i= 0,len=hosts.length;i<len;i++){
        if (hosts[i].id == checkhost_id){
            var host = hosts[i];
            host.agent_status = null;
            delete host["agent_status"];
            hosts_view.checked_host = Object.assign({}, host, {});
            get_agent_status_by_hostid(host.id);
            displaySideContent('single');
            //// 默认渲染基础性能图表
            //render_single_host_bp_graph();
            render_component_graph("System");
            // 拉取关联告警策略信息
            render_alarm_strategy(hosts_view.checked_host.id);
            // 拉取告警事件列表
            var today = new Date();
            $("#alarm_date").val(today.yyyymmdd()).trigger("change");
            break;
        }
    }
}

function refresh_host_info(){
    // 拉取主机性能信息
    $('#hosts_table_loading').removeClass('hidden');
    $.post(site_url + cc_biz_id + '/'+'bp/', {}, function(res){
        hosts_view.first_open = false;
        $('#hosts_table_loading').addClass('hidden');
        if (res.result){
            hosts = res.data.hosts;
            update_time_span.text(res.data.update_time);
            move_page_to_hosts(current_page);
            if (checkhost_id && hosts_view.host_index_list.length > 0){
                open_host_detail(checkhost_id);
                checkhost_id = null;
            }
        }else{
            if (res.data.need_access != undefined){
                var tips = $("#tips");
                tips.removeClass("hidden").find(".main").html(res.data.access_div_message);
                tips.find("button").text(res.data.access_btn_message);
                need_access = res.data.need_access
            }else{
                app_alert("获取主机性能信息失败: " + res.message, "fail");
                update_time_span.text("加载失败");
            }
            if (res.data.hosts){
                hosts = res.data.hosts;
                update_time_span.text(res.data.update_time);
                move_page_to_hosts(current_page);
            }
        }
    }, "json");
}

function distinct_host(arr){
    var n = [];
    var new_hosts = [];
    for(var i = 0;i < arr.length; i++){
        if(n.indexOf(arr[i].id) == -1) {
            n.push(arr[i].id);
            new_hosts.push(arr[i]);
        }
    }
    return new_hosts;
}

function filter_hosts_by(arr, key_func, val, cmp){
    if (!cmp){
        cmp = function(a, b){
            return a == b;
        }
    }
    var new_hosts = [];
    for (var i= 0, host_len = arr.length;i<host_len; i++){
        var _host = arr[i];
        if (cmp(key_func(_host), val)){
            new_hosts.push(_host);
        }
    }
    return new_hosts;
}

function filter_hosts(arr){
    var newArray = arr.slice();
    // 过滤set
    var set_id = set_selector.select2("val");
    if (set_id && set_id != "0"){
        newArray = filter_hosts_by(newArray, function(_host){
            return _host.SetID;
        }, set_id)
    }
    // 过滤 mod
    var mod_id = mod_selector.select2("val");
    if (mod_id && mod_id != "0"){
        newArray = filter_hosts_by(newArray, function(_host){
            return _host.ModuleID;
        }, mod_id)
    }
    // 过滤 status
    var status = status_selector.select2("val");
    if (status){
        newArray = filter_hosts_by(newArray, function(_host){
            return _host.status;
        }, status)
    }
    // 过滤 ip
    var ip_keys = ip_filter_selector.val().trim().split("\n");

    newArray = filter_hosts_by(newArray, function(_host){
        return _host.InnerIP;
    }, ip_keys, function(host_ip, ip_keys){
        var ret = false;
        for (var i=0; i<ip_keys.length; i++){
            var ip_key = ip_keys[i].trim();
            ret = (i>0 && ip_key == "") ? ret : (host_ip.indexOf(ip_key) >= 0 || ret);
        }
        return ret;
    });

    return newArray
}

function order_hosts(arr){
    // 表头排序
    var order_tr = $("i.ordered");
    var process_arr = arr.slice();
    if (order_tr.length > 0){
        var order = order_tr.hasClass("asc")?1:-1;
        var order_key = order_tr.closest("td").attr("data-attr");
        process_arr = order_hosts_by(process_arr, function(_host){
            return _host[order_key]?(_host[order_key].val?_host[order_key].val:0):0
        }, order);
    }
    // 置顶排序
    return order_hosts_by(process_arr, function(_host){
        return _host.is_stickied?_host.is_stickied: 0
    }, -1);
}

function order_hosts_by(arr, key_func, order){
    if (!order){
        order = 1;
    }
    var newArray = arr.slice();
    newArray.sort(function(a, b){
        var keyA = key_func(a),
            keyB = key_func(b);
        // Compare
        if(keyA < keyB) {return -1 * order;}
        if(keyA > keyB) {return 1 * order;}
        var indexA = arr.indexOf(a),
            indexB = arr.indexOf(b);
        return indexA-indexB;
    });
    return newArray
}

function refresh_host_paging_footer(page, count_per_page, total_count){
    current_page = page;
    // 在这里适应过滤hosts
    var processed_hosts  = filter_hosts(hosts);
    // 去重
    processed_hosts = distinct_host(processed_hosts);
    //  排序
    processed_hosts = order_hosts(processed_hosts);

    if (hosts_view.group_by){
        // 按属性分组展示分页
        processed_hosts = make_group_hosts_list(processed_hosts);
    }
    total_count = processed_hosts.length;
    // 分页渲染
    var page_info = _refresh_paging_footer(page, count_per_page, total_count, hosts_paging_footer, "_hosts");
    var start = page_info[0],
        end = page_info[1];
    // update vue
    hosts_view.hosts = $.parseJSON(JSON.stringify(processed_hosts.slice(start-1, end)));
    update_host_alarm_count_info()
    // 更新全选框状态
    update_check_all_checkbox();
}

function get_val_display(host, key){
    if (key=="Source"){
        return get_plat_name(host[key]);
    }
    return host[key] || "空";
}

function get_plat_name(source){
    return plat_info[source]
}

function refresh_plat_info(){
    $.ajax({
        url: site_url+cc_biz_id+'/'+'get_plat_list/',
        data: {},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            if (resp.result) {
                resp.data.forEach(function(item){
                    plat_info[item["plat_id"]] = item["plat_name"];
                });
            }
        }
    });
}

function make_group_hosts_list(hosts_list){
    var processed_hosts = order_hosts_by(hosts_list, function(_host){
        return _host[hosts_view.group_by];
    }, -1);
    hosts_view.group_hosts = processed_hosts.slice();
    var attr = null;
    var _group_hosts_info = {};
    var label_list = [];
    for (var i= 0, len=hosts_view.group_hosts.length; i<len;i++){
        var _host = hosts_view.group_hosts[i];
        var attr_val = _host[hosts_view.group_by];
        attr_val = attr_val || "空";
        if (attr != attr_val){
            attr = attr_val;
            var group_val = _host[hosts_view.group_by] || '空';
            var label = {
                _is_show: true,
                is_label: true,
                label_status: _host._is_show?"expanded":"closed",
                label_icon_text: _host._is_show?"-":"+",
                group_val: group_val,
                group_host_count: 1,
                group_text: property_selector.select2('data').text+"("+ get_val_display(_host, hosts_view.group_by) +")：",
                group_hosts: []
            };
            label_list.push(label);
        }
        label.group_hosts.push(_host);
        label_list.push(_host);

        if (_group_hosts_info.hasOwnProperty(attr_val)){
            _group_hosts_info[attr_val] ++;
        }else{
            _group_hosts_info[attr_val] = 1;
        }
    }
    // 过滤掉折叠的主机
    return filter_hosts_by(label_list, function(_host){
        return _host._is_show;
    }, true)
}


function _refresh_paging_footer(page, _count_per_page, total_count, paging_footer_selector, slug){
    var show_page_list = [];
    var total_page = parseInt(total_count/_count_per_page);
    if (total_count % _count_per_page > 0){
        total_page ++;
    }
    if (page>total_page){
        page = 1;
    }
    var page_list = Array.range(1, total_page);
    if (page_list.slice(0, 3).indexOf(page) >= 0){
        show_page_list = page_list.slice(0, 5);
    }
    if (page_list.slice(-3).indexOf(page) >= 0){
        show_page_list = page_list.slice(-5);
    }else{
        if (show_page_list.length == 0){
            show_page_list = page_list.slice(page-3, page+2)
        }
    }
    var page_ul = $('<ul class="pagination" data-type="paging"></ul>');
    var prev_item = $('<li><a href="javascript:move_page_to'+slug+'(1);" aria-label="Previous"> <span aria-hidden="true">«</span></a></li>');
    page_ul.append(prev_item);
    for (i=0;i<show_page_list.length;i++){
        var page_item = $('<li><a href="javascript:move_page_to'+slug+'('+show_page_list[i]+');" class="page-item'+show_page_list[i]+'">'+show_page_list[i]+'</a></li>');
        page_ul.append(page_item);
    }
    var next_item = $('<li><a href="javascript:move_page_to'+slug+'('+(total_page>0?total_page:1)+');" aria-label="Next"> <span aria-hidden="true">»</span></a></li>');
    page_ul.append(next_item);
    if (show_page_list.indexOf(1)>=0 && page == 1){
        page_ul.find("li>a[aria-label=Previous]").attr("href", "javascript:;").closest("li").addClass('disabled');
    }
    if ((show_page_list.indexOf(total_page)>=0 && page == total_page) || total_page == 0){
        page_ul.find("li>a[aria-label=Next]").attr("href", "javascript:;").closest("li").addClass('disabled');
    }
    page_ul.find("li>a.page-item"+page).closest("li").addClass('active');
    var paging_nav = $('<nav class="pull-left"></nav>');
    paging_nav.append(page_ul);
    var start = (page - 1) * _count_per_page + 1;
    start = start > total_count ? total_count : start;
    var end = page * _count_per_page;
    end = end > total_count ? total_count : end;
    var paging_info = $(' <div class="pull-right pagination-text">显示条目 '+ start + '-'+ end +' 共'+ total_page +'页</div> ');
    if (total_count > 0 && slug == "_hosts"){
        var count_per_page_html = '<span style="color: black;">每页展示' +
            '<select id="count_per_page">' +
            '<option>5</option>' +
            '<option>10</option>' +
            '<option>20</option>' +
            '<option>50</option>' +
            '<option>100</option>' +
            '</select>' +
            '条</span>  ';
        paging_info.prepend(count_per_page_html);
    }
    paging_footer_selector.html("").append(paging_nav).append(paging_info);
    if (total_count > 0){
        $("#count_per_page").unbind("change").on("change", function(e){
            count_per_page = $(e.target).val();
            refresh_host_paging_footer(page, count_per_page, total_count);
        });
        $("#count_per_page").val(count_per_page);
    };
    return [start, end]
}

function move_page_to_hosts(page){
    current_page = page;
    refresh_host_paging_footer(current_page, count_per_page, hosts.length)
}

function refresh_sets_info(){
    // 拉取集群列表
    $.getJSON(site_url+cc_biz_id+'/'+'get_cc_set/', function (resp) {
        if (resp.result) {
            sets = resp.data;
            set_selector.select2({
                data: sets,
                placeholder: "请选择集群",
                language: "zh-CN"
            });
            //set_selector.select2('data', sets[0]);
            // 主动触发下一级
            set_selector.select2("val", "0").trigger('change');
        }
    });
}

function refresh_property_list(){
    property_selector.val("").select2({
        data: [],
        placeholder: "加载中...",
        language: "zh-CN"
    }).change(function(){
        var attr_id = property_selector.select2("val");
        if (attr_id == "0"){
            hosts_view.group_by = "";
        }else{
            hosts_view.group_by = attr_id;
        }
    });
    $.ajax({
        url: site_url+cc_biz_id+'/'+'get_host_property_list/',
        data: {},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            if (resp.result) {
                var property_list = resp.data;
                property_selector.select2({
                    data: property_list,
                    placeholder: "不分组",
                    language: "zh-CN"
                });
                property_selector.select2("val", "0");
            }
        }
    });
}

function refresh_mods_info(set_id){
    mod_selector.val("").select2({
        data: [],
        placeholder: "加载中...",
        language: "zh-CN"
    });
    $.ajax({
        url: site_url+cc_biz_id+'/'+'get_cc_module/',
        data: {"set_id": set_id},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            if (resp.result) {
                mods = resp.data;
                mod_selector.select2({
                    data: mods,
                    placeholder: "请选择模块",
                    language: "zh-CN"
                });
                mod_selector.select2("val", "0");
            }
        }
    });
}

function displaySideContent(type){
    // 侧边栏打开
    sideContent.removeClass('hidden');
    getComputedStyle(document.getElementById('panelBody')).display;
    sideContent.find('#close').addClass('open');
    sideContent.find('.side-content').addClass('open');
    if(type == 'single'){
        sideContent.find('#single').removeClass('hidden').siblings('#multiple').addClass('hidden');
    }
    else if(type == 'multiple'){
        sideContent.find('#single').addClass('hidden').siblings('#multiple').removeClass('hidden');
    }

    $('article.content').css('overflow', 'hidden');
    $('body').css('overflow', 'hidden');
}

function get_agent_status_by_hostid(hostid){
    $.get(site_url+cc_biz_id+'/'+'get_agent_status/', {"host_id": hostid}, function(res){
        if (res.result){
            hosts_view.checked_host = Object.assign({}, hosts_view.checked_host, {agent_status: res.data.status});
        }
    }, 'json');
}

function render_component_graph(component_name){
    // 渲染单机组件性能图表，基础性能图表特殊处理
    if (component_name == "System"){
        render_single_host_bp_graph();
    }else{
        console.log("组件"+component_name+"监控正在开发中...")
    }
}

function render_single_host_bp_graph(){
    // 分页渲染
    move_page_to_single_graph(1);
}

function move_page_to_single_graph(page){
    if (!hosts_view.checked_host){
        return
    }
    var host_index_list = filter_hosts_by(hosts_view.host_index_list, function(item) {
        if (item.dimension_field != "name") {
            return 1
        }else{
            var eth_name_list = eth_info[hosts_view.checked_host.id] || [];
            return eth_name_list.indexOf(item.dimension_field_value) >=0?1:-1
        }
    }, 1);
    // 分页渲染
    var page_info = _refresh_paging_footer(page, count_per_page_graph, host_index_list.length, single_graph_paging_footer, "_single_graph");
    var start = page_info[0],
        end = page_info[1];
    // update vue
    hosts_view.checked_host_index_table = host_index_list.slice(start-1, end);
}

function get_multiple_host_index(index_id){
    var multiple_host_index = [];
    // 获取该id对应的性能指标项
    for (var j= 0, leng=hosts_view.selected_host_list.length; j<leng;j++){
        for (var i = 0, len = hosts_view.host_index_list.length; i < len; i++) {
            if (hosts_view.host_index_list[i].index_id == index_id){
                var _host_index = Object.assign({}, hosts_view.host_index_list[i], {});
                // 获取主机下的网卡列表
                var eth_name_list = eth_info[hosts_view.selected_host_list[j].id] || [];
                if (_host_index.dimension_field == "name" && eth_name_list.indexOf(_host_index.dimension_field_value) < 0 ) {
                    continue
                }
                _host_index.host_id = hosts_view.selected_host_list[j].id;
                _host_index.host_ip = hosts_view.selected_host_list[j].InnerIP;
                multiple_host_index.push(_host_index)
            }
        }
    }
    return multiple_host_index;
}

function render_multiple_host_bp_graph(){
    move_page_to_multiple_graph(1);
}

function move_page_to_multiple_graph(page){
    var index_id = $('#selectors').find('a.king-primary').attr("data-index_id");
    var multiple_host_index = get_multiple_host_index(index_id);
    // 分页渲染
    var page_info = _refresh_paging_footer(page, count_per_page_graph, multiple_host_index.length, multiple_graph_paging_footer, "_multiple_graph");
    var start = page_info[0],
        end = page_info[1];
    // update vue
    hosts_view.multiple_host_index_table = multiple_host_index.slice(start-1, end);
}

function render_alarm_strategy(host_id){
    $("#alarms_strategy_table_loading").removeClass("hidden");
    $.get(site_url + cc_biz_id + '/bp/get_alarm_strategy_list/', {host_id: host_id}, function(res){
        $("#alarms_strategy_table_loading").addClass("hidden");
        if (res.result){
            hosts_view.checked_host_alarm_strategy = res.data;
            // 分页渲染
            move_page_to_alarm_strategy(current_strategy_page)
        }else{
            hosts_view.checked_host_alarm_strategy = [];
        }
    }, "json");
}

function move_page_to_alarm_strategy(page){
    current_strategy_page = page;
    // 分页渲染
    var page_info = _refresh_paging_footer(page, count_per_page_alarms, hosts_view.checked_host_alarm_strategy.length, alarm_strategy_paging_footer, "_alarm_strategy");
    var start = page_info[0],
        end = page_info[1];
    // update vue
    hosts_view.checked_host_alarm_strategy_table = hosts_view.checked_host_alarm_strategy.slice(start-1, end);
}

function render_alarms(host_id){
    var alarm_date = $("#alarm_date").val();
    $("#alarms_table_loading").removeClass("hidden");
    $.get(site_url + cc_biz_id + '/bp/get_alarm_list/', {alarm_date: alarm_date, host_id: host_id}, function(res){
        $("#alarms_table_loading").addClass("hidden");
        if (res.result){
            hosts_view.checked_host_alarms = res.data.alarm_info_list;

            // 分页渲染
            move_page_to_alarms(1)
        }else{
            hosts_view.checked_host_alarms = [];
        }
    }, "json");
}

function move_page_to_alarms(page, level){
    if (!level){
        level = $(".title-badge.active").attr("attr-level")
    }
    var alarms = level?filter_hosts_by(hosts_view.checked_host_alarms, function(alarm){return alarm.level}, level):hosts_view.checked_host_alarms;
    // 分页渲染
    var page_info = _refresh_paging_footer(page, count_per_page_alarms, alarms.length, alarms_paging_footer, "_alarms");
    var start = page_info[0],
        end = page_info[1];
    // update vue
    hosts_view.checked_host_alarms_table = alarms.slice(start-1, end);
}

function make_single_graphs(){
    $(".single-contain").each(function(){
        make_contain_graph($(this));
    });
}

function make_multiple_graphs(){
    $(".multiple-contain").each(function(){
        make_contain_graph($(this), "multiple");
    });
}

function make_contain_graph(contain, _type){
    var chart_div = contain.find(".line-chart");
    var host_id = chart_div.attr("data-host_id");
    if (!host_id){
        host_id = hosts_view.checked_host.id;
    }
    var params = {
        graph_date: _type?$("#multiple_graph_date").val():$("#single_graph_date").val(),
        host_id: host_id,
        index_id: chart_div.attr("data-index_id"),
        dimension_field_value: chart_div.attr("data-dimension_field_value")
    };

    chart_div.html('<img class="graph-loading" alt="loadding" src="'+static_url+'img/hourglass_36.gif" style="margin-top: 75px;margin-left:45%;">');
    $.get(site_url+cc_biz_id+'/'+'bp/graph/point/', params, function(res){
        chart_div.html("");
        if(res.result){
            var chart_data =res.data.data ;
            var series_info = {};
            for (var i = 0; i < chart_data.series.length; i++) {
                series_info[chart_data.series[i].name] = chart_data.series[i];
            }
            Hchart.spline(chart_data, chart_div[0], series_info);
        }else{
            var error_tips_html = '<div class="chart-error">' +
                '<span class="error-mark">' +
                '<i class="fa fa-exclamation"></i>' +
                '</span><span class="error-text">'+
                res.message + '</span></div>';
            //chart_div.html(error_tips_html);
            chart_div.html(res.message);
        }
    }, 'json');
}

function link_data_sql_query_page(){
	// 数据平台 app_code
	var target_app_code = 'data';
	// 数据接入连接
	var target_url = '/s/'+target_app_code+'/statistics/?from=ja&cc_biz_id='+cc_biz_id;
	try{
		window.top.open_app_by_other(target_app_code, target_url);
	}catch(e){
		var msg = '请在蓝鲸平台中打开该应用';
		// 提示用户必须在蓝鲸平台中打开
	    dialog({
	        width: 430,
	        title: '提示',
	        ok: function() {
	        	// 在蓝鲸平台中打开该应用
	        	window.top.location.href = 'http://o.qcloud.com/console/?app=alert';
	        },
	        okValue: '跳转到蓝鲸平台',
	        cancelValue: '取消',
	        cancel: function (){},
	        content: '<div class="king-notice-box king-notice-warning"><p class="king-notice-text">'+msg+'</p></div>'
	    }).show();
	}
}


function data_access(){

    var button = $('#tips').find("button");
    button.attr("disabled", true);
    button.html('正在开始采集...');
    $.post(site_url+cc_biz_id+'/'+'bp/access/', {}, function(res){
        button.attr("disabled", false);
        if(res.result){
            alert_topbar("操作成功，10-20分钟后刷新此页面即可查看到主机数据，请耐心等待！", "success", 6000);
            $('#tips').addClass('hidden');
        }else{
            alert_topbar(res.message, "fail", 10000);
            setTimeout(function(){
                $('#tips').addClass('hidden');
            }, 2000);
        }
        button.html('开始采集');
    }, 'json');
}

function data_access_single(self){
    if ($(self).hasClass("disabled")) return;
    $(self).addClass("disabled");
    $(self).html("<i class='fa fa-spinner fa-pulse mr5'></i>");
    $.post(site_url+cc_biz_id+'/'+'bp/access/', {hostid_list: hosts_view.checked_host.id}, function(res){
        $(self).removeClass("disabled");
        $(self).html("点击接入");
        if(res.result){
            alert_topbar("操作成功，10-20分钟后刷新此页面即可查看到主机数据，请耐心等待！", "success", 6000);
        }else{
            alert_topbar(res.message, "fail", 10000);
        }
    }, 'json');
}


function bind_event(){
    //刷新按钮
    $('#updateBtn').on('click', function(){
        refresh_host_info();
    });
	//开始采集按钮
	$('#collection').on('click', function(){
        if (need_access){
            data_access();
        }else{
            $('#tips').addClass('hidden');
        }
	});
}

var on_div_close = function(){
    try{
        if (alarm_strategy_id!=0){
            get_alarm_data(alarm_strategy_id)
        }else{
            get_config_data();
        }

    }catch(e){

    }
};

if (run_init){
    init();
}else{
    refresh_sets_info();
}

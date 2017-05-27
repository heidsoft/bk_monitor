/**
 * Created by willgchen on 2016/11/7.
 */

var today = new Date(),
    count_per_page_alarms = 3,
    alarms_paging_footer = $("#alarms-paging-footer");

var field_id_list = [];
var condition = {};

$("#strategy_detail_close").click(function(){
    close_stragety_detail_side();
});

$("#strategy_edit_close").click(function(){
    close_stragety_edit_side();
});

$("#strategy_detail_side").click( function(e){
    if ($(e.target).closest(".strategy-detail").length==0){
        close_stragety_detail_side();
    }
});


// $时间选择
$('#alarm_date').kendoDatePicker({
    max: today,
    min: new Date(new Date().setDate(new Date().getDate() - 30)),
    value : today,
    format : "yyyy-MM-dd"
}).change(function(){
    // 刷新告警页面
    if (read_strategy_vue.strategy_id){
        refresh_stragety_alarms(read_strategy_vue.strategy_id)
    }

});

function close_stragety_edit_side(){

    var sideContent = $('#strategy_edit_side');

    sideContent.find('.strategy-edit').removeClass('open').children('#strategy_edit_div').addClass('hidden');
    sideContent.find('#strategy_edit_close').removeClass('open');

    setTimeout(function(){
        sideContent.addClass('hidden');
    }, 300);


    $('article.content').css('overflow', 'auto');
    // $('body').css('overflow', 'auto');
    if (!$('#iframe_body').html() || $('.monitor-popup').css('display') == 'block'){
        $('body').css('overflow', 'auto');
    }
}

function edit_strategy(strategy_id){

    var sideContent = $('#strategy_edit_side');
    sideContent.removeClass('hidden');
    getComputedStyle(document.querySelector('body')).display;
    sideContent.find('#strategy_edit_close').addClass('open');
    sideContent.find('.strategy-edit').addClass('open');

    setTimeout(function() {
        sideContent.find('#strategy_edit_div').removeClass('hidden');
    }, 300);

    var detail_side_content = $('#strategy_detail_side');
    detail_side_content.find('.strategy-detail').removeClass('open').children('#strategy_detail_div').addClass('hidden');
    detail_side_content.find('#strategy_detail_close').removeClass('open');

    setTimeout(function(){
        detail_side_content.addClass('hidden');
        $('article.content').css('overflow', 'auto');
    }, 300);
    $('body').css('overflow', 'hidden');

    // 加载策略
    if (!strategy_id){
        strategy_id = 0
    }
    edit_strategy_vue.alarm_strategy_id = strategy_id;
    $("#strategyeditLoading").removeClass("hidden");

    // 初始化
    $(".condition-div").remove();
    $("#condition_num_id").val("0");
    // 获取策略信息
    $.ajax({
        url: site_url+cc_biz_id+'/'+'bp/get_bp_strategy/',
        data: {alarm_strategy_id: strategy_id},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            $("#strategyeditLoading").addClass("hidden");
            if (resp.result) {
                strategy_data = resp.data;
                edit_strategy_vue.display_name = strategy_data.display_name;
                edit_strategy_vue.strategy_id = strategy_data.strategy_id;
                edit_strategy_vue.converge_id = strategy_data.rules.converge_id || "0";
                edit_strategy_vue.show_nodata_alarm = strategy_data.nodata_alarm==0?"0":1;
                setTimeout(function(){
                    edit_strategy_vue.nodata_alarm = strategy_data.nodata_alarm;
                    edit_strategy_vue.converge_continuous = strategy_data.rules.continuous || "";
                    edit_strategy_vue.converge_count = strategy_data.rules.count || "";
                    edit_strategy_vue.solution_is_enable = strategy_data.solution_is_enable;
                    edit_strategy_vue.solution_type = strategy_data.solution_type;
                    edit_strategy_vue.solution_notice = strategy_data.solution_notice;
                    edit_strategy_vue.solution_task_id = strategy_data.solution_task_id;
                }, 200);
                edit_strategy_vue.method = strategy_data.strategy_option.method || "eq";
                edit_strategy_vue.threshold = strategy_data.strategy_option.threshold || "";
                edit_strategy_vue.ceil = strategy_data.strategy_option.ceil || "";
                edit_strategy_vue.floor = strategy_data.strategy_option.floor || "";
                edit_strategy_vue.floor_interval = strategy_data.strategy_option.floor_interval || "";
                edit_strategy_vue.ceil_interval = strategy_data.strategy_option.ceil_interval || "";
                edit_strategy_vue.monitor_level = strategy_data.monitor_level;
                edit_strategy_vue.responsible = strategy_data.responsible;
                edit_strategy_vue.notice_role_list = strategy_data.role_list;
                edit_strategy_vue.notice_list = isEmpty(strategy_data.notify_way)?[]:strategy_data.notify_way;
                edit_strategy_vue.phone_receiver = strategy_data.phone_receiver;
                edit_strategy_vue.notice_start_hh = strategy_data.notice_start_hh;
                edit_strategy_vue.notice_start_mm = strategy_data.notice_start_mm;
                edit_strategy_vue.notice_end_hh = strategy_data.notice_end_hh;
                edit_strategy_vue.notice_end_mm = strategy_data.notice_end_mm;
                edit_strategy_vue.condition = strategy_data.condition;
                if (strategy_id!=0){
                    init_condition_html(strategy_data.condition);
                }else{
                    var tmp_conditon = [];
                    for (var key in condition) {
                        if (condition.hasOwnProperty(key)){
                            tmp_conditon.push({
                                field: key,
                                method: "eq",
                                value: condition[key]
                            })
                        }
                    }
                    init_condition_html([tmp_conditon]);
                }

            }
        }
    });
}

function open_stragety_detail_side(strategy_id){
    read_strategy_vue.strategy_id = strategy_id;
    $("#strategyLoading").removeClass("hidden");
    // 获取策略信息
    $.ajax({
        url: site_url+cc_biz_id+'/'+'bp/get_bp_strategy/',
        data: {alarm_strategy_id: strategy_id},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            $("#strategyLoading").addClass("hidden");
            if (resp.result) {
                read_strategy_vue.strategy_obj = resp.data;
                setTimeout(function(){
                    $('.data-tip').popover();
                }, 100);
            }
        }
    });
    refresh_stragety_alarms(strategy_id);

    var sideContent = $('#strategy_detail_side');
    sideContent.removeClass('hidden');
    getComputedStyle(document.querySelector('body')).display;
    sideContent.find('#strategy_detail_close').addClass('open');
    sideContent.find('.strategy-detail').addClass('open');
    setTimeout(function() {
        sideContent.find('#strategy_detail_div').removeClass('hidden');
    }, 300);

    $('body').css('overflow', 'hidden');
}

function close_stragety_detail_side(){
    var sideContent = $('#strategy_detail_side');
    sideContent.find('.strategy-detail').removeClass('open').children('#strategy_detail_div').addClass('hidden');
    sideContent.find('#strategy_detail_close').removeClass('open');

    setTimeout(function(){
        sideContent.addClass('hidden');
        $('article.content').css('overflow', 'auto');
    }, 300);
    if (!$('#iframe_body').html() || $('.monitor-popup').css('display') == 'block'){
        $('body').css('overflow', 'auto');
    }
}

function show_strategy_alarms_table_loading(){
    $("#relevantAlertLoading").removeClass("hidden")
}

function hide_strategy_alarms_table_loading(){
    $("#relevantAlertLoading").addClass("hidden")
}

function refresh_stragety_alarms(strategy_id){
    show_strategy_alarms_table_loading();
    $.ajax({
        url: site_url+cc_biz_id+'/'+'get_strategy_alarm_list/',
        data: {strategy_id: strategy_id, alarm_date:$("#alarm_date").val()},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            hide_strategy_alarms_table_loading();
            if (resp.result) {
                read_strategy_vue.strategy_alarms = resp.data.alarm_info_list;
                // 分页渲染
                move_page_to_detail_alarms(1)
            }else{
                read_strategy_vue.strategy_alarms = [];
            }
        }
    });
}

function move_page_to_detail_alarms(page){
    // 分页渲染
    var page_info = _refresh_paging_footer(page, count_per_page_alarms, read_strategy_vue.strategy_alarms.length, alarms_paging_footer, "_detail_alarms");
    var start = page_info[0],
        end = page_info[1];
    // update vue
    read_strategy_vue.strategy_alarms_table = read_strategy_vue.strategy_alarms.slice(start-1, end);
}

function init_strategy_vue_for_read(){
    // 只读页面
    read_strategy_vue = new Vue({
        el: '#strategy_detail_div',
        data: {
            'strategy_id': null,
            'strategy_obj': {
                notify_way: [],
            },
            strategy_alarms: [], // 策略对应的告警事件
            strategy_alarms_table: [], // 策略对应的告警事件分页展示
        },
        computed:{
            nodata_alarm_display: function(){
                return this.strategy_obj && this.strategy_obj.nodata_alarm > 0?"当数据连续丢失"+this.strategy_obj.nodata_alarm+"个周期时，触发告警":"未启用";
            }
        },
        methods:{
            'monitor_level_class': function(level){
                level = level?level:"2";
                switch (level){
                    case '3':
                        return  'text-muted';
                        break;
                    case '2':
                        return  'text-info';
                        break;
                    case '1':
                        return  'text-danger';
                        break;
                }
            },
            'monitor_level_display': function(level){
                level = level?level:"2";
                switch (level){
                    case '3':
                        return  '轻微';
                        break;
                    case '2':
                        return  '普通';
                        break;
                    case '1':
                        return  '严重';
                        break;
                }
            },
            'modify_self': function(){
                close_stragety_detail_side();
                edit_strategy(this.strategy_obj.alarm_strategy_id);
            }
        }
    });
}

function _refresh_paging_footer(page, count_per_page, total_count, paging_footer_selector, slug){
    var show_page_list = [];
    var total_page = parseInt(total_count/count_per_page);
    if (total_count % count_per_page > 0){
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
    var page_ul = $('<ul class="pagination mt5 mb5" data-type="paging"></ul>');
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
    var start = (page - 1) * count_per_page + 1;
    start = start > total_count ? total_count : start;
    var end = page * count_per_page;
    end = end > total_count ? total_count : end;
    var paging_info = $('<div class="pull-right pagination-text">显示条目 '+ start + '-'+ end +' 共'+ total_page +'页</div>');
    paging_footer_selector.html("").append(paging_nav).append(paging_info);
    return [start, end]
}

function isEmpty(obj) {

    // null and undefined are "empty"
    if (obj == null) return true;

    // Assume if it has a length property with a non-zero value
    // that that property is correct.
    if (obj.length > 0)    return false;
    if (obj.length === 0)  return true;

    // If it isn't an object at this point
    // it is empty, but it can't be anything *but* empty
    // Is it empty?  Depends on your application.
    if (typeof obj !== "object") return true;

    // Otherwise, does it have any properties of its own?
    // Note that this doesn't handle
    // toString and valueOf enumeration bugs in IE < 9
    for (var key in obj) {
        if (hasOwnProperty.call(obj, key)) return false;
    }

    return true;
}

/* 编辑 */
var strategy_id_icheck = $("[name=strategy_id]"),
    converge_id_icheck = $("[name=converge_id]"),
    show_nodata_alarm_icheck = $("[name=show_nodata_alarm]");

function init_strategy_vue_for_edit(){
    // 编辑页面
    edit_strategy_vue = new Vue({
        el: '#strategy_edit_div',
        data: {
            alarm_strategy_id: 0,   // 告警策略id
            display_name: "",       // 策略名称
            strategy_id: 1000,      // 默认算法id（静态阈值）
            responsible: "",        // 额外通知人
            method: "eq",          // eq gte lte gt lt
            threshold: "",          // 静态阈值
            ceil: "",               // 上限(同比环比算法)
            floor: "",               // 下限(同比环比算法)
            converge_id: 0,        // 收敛配置id
            converge_continuous: "5",   // 收敛参数
            converge_count: "",         // 收敛参数
            monitor_level: "2",         // 告警级别
            phone_receiver: "",         // 电话通知人
            notice_start_hh: "00",      // 通知开始小时
            notice_start_mm: "00",      // 通知开始分钟
            notice_end_hh: "23",        // 通知结束小时
            notice_end_mm: "59",        // 通知结束分钟
            notice_list: [],            // 通知方式列表
            notice_role_list: [],       // 通知角色列表
            nodata_alarm: "",            // 无数据告警周期 0表示不告警
            show_nodata_alarm: "0",       // 是否启用无数据告警
            ceil_interval: "",
            floor_interval: "",
            solution_type: "job",       // 自动处理，默认作业平台
            solution_task_id: "",         // 自动处理任务id
            solution_notice: [],        // 主动处理通知
            solution_is_enable: false,  // 是否开启自动处理
        },
        computed:{
            strategy_display: function(){
                if (this.strategy_id == 1001){
                    return "较上周同一时刻值"
                }
                if (this.strategy_id == 1002){
                    return "较前一时刻值"
                }
                if (this.strategy_id == 1003){
                    return "天内同一时刻绝对值的均值"
                }
                if (this.strategy_id == 1004){
                    return "个时间点的均值"
                }
                return "较前一时刻值";
            }
        },
        methods:{

        },
        watch: {
            threshold: function(val, oldVal){
                if (parseInt(val) < 0){
                    this.threshold = "";
                }
            },
            ceil: function(val, oldVal){
                if (parseInt(val) < 0){
                    this.ceil = "";
                }
            },
            floor: function(val, oldVal){
                if (parseInt(val) < 0){
                    this.floor = "";
                }
            },
            floor_interval: function(val, oldVal){
                if (parseInt(val) < 0){
                    this.floor_interval = "";
                }
            },
            ceil_interval: function(val, oldVal){
                if (parseInt(val) < 0){
                    this.ceil_interval = "";
                }
            },
            converge_count: function(val, oldVal){
                if (parseInt(val) < 0){
                    this.converge_count = "";
                }
            },
            nodata_alarm: function(val, oldVal){
                if (parseInt(val) < 0){
                    this.nodata_alarm = "";
                }
            },
            solution_type: function(val, oldVal){
                refresh_task_list();
                this.solution_task_id = "";
            },
            solution_task_id: function(val, oldVal){
                val = val+"";
                $("#autoProcessFlowList").select2("val", val);
            },
            solution_notice: function(val, oldVal){
                $("[name=solution_notice]").prop("checked", false).iCheck('update');
                for (var i=0;i<val.length;i++){
                    $("[name=solution_notice][value="+val[i]+"]").prop("checked", true).iCheck('update');
                }
            },
            solution_is_enable: function(val, oldVal){
                var solution_switch = $('.js-switch-small')[0];
                switchery.switcher.remove();
                solution_switch.checked=Boolean(val);
                switchery = new Switchery(solution_switch, { size: 'small' });
                var i_btn = $("#auto_process").find(".icon-jiantou1");
                if (solution_switch.checked){
                    if (i_btn.hasClass("expanded")){
                        i_btn.closest(".config__panelTool").click();
                    }
                }else{
                    if (!i_btn.hasClass("expanded")){
                        i_btn.closest(".config__panelTool").click();
                    }
                }
            },
            strategy_id: function(val, oldVal){
                strategy_id_icheck.iCheck("uncheck");
                var $this = $("[name=strategy_id][value="+val+"]");
                $this.iCheck("check");
            },
            converge_id: function(val, oldVal){
                converge_id_icheck.iCheck("uncheck");
                var $this = $("[name=converge_id][value="+val+"]");
                $this.iCheck("check");
            },
            show_nodata_alarm: function(val, oldVal){
                show_nodata_alarm_icheck.iCheck("uncheck");
                var $this = $("[name=show_nodata_alarm][value="+val+"]");
                $this.iCheck("check");
            },
            method: function (val, oldVal){
                val = val+"";
                $("[name=method]").select2("val", val);
            },
            converge_continuous: function (val, oldVal){
                val = val+"";
                $("[name=converge_continuous]").select2("val", val);
            },
            notice_start_hh: function (val, oldVal){
                val = val+"";
                $("[name=notice_start_hh]").select2("val", val);
            },
            notice_start_mm: function (val, oldVal){
                val = val+"";
                $("[name=notice_start_mm]").select2("val", val);
            },
            notice_end_hh: function (val, oldVal){
                val = val+"";
                $("[name=notice_end_hh]").select2("val", val);
            },
            notice_end_mm: function (val, oldVal){
                val = val+"";
                $("[name=notice_end_mm]").select2("val", val);
            },
            notice_list: function (val, oldVal){
                $("[name=notice]").prop("checked", false).iCheck('update');
                for (var i=0;i<val.length;i++){
                    $("[name=notice][value="+val[i]+"]").prop("checked", true).iCheck('update');
                }
                if (val.indexOf("phone")>=0){
                    $('[name=phone_receiver]').removeClass('hidden').next().removeClass('hidden');
                }else{
                    $('[name=phone_receiver]').addClass('hidden').next().addClass('hidden');
                    this.phone_receiver = "";
                }
                $("#notice_list_error").text("");
            },
            notice_role_list: function (val, oldVal){
                $("[name=notice_role_list]").prop("checked", false).iCheck('update');
                for (var i=0;i<val.length;i++){
                    $("[name=notice_role_list][value="+val[i]+"]").prop("checked", true).iCheck('update');
                }
                if (val.indexOf("other")>=0){
                    $('[name=responsible]').removeClass('hidden');
                }else{
                    $('[name=responsible]').addClass('hidden');
                    this.responsible = "";
                }
                $("#notice_role_list_error").text("");
            },
            phone_receiver: function (val, oldVal){
                $("[name=phone_receiver]").select2("val", val);
                $("#notice_list_error").text("");
            },
            responsible: function (val, oldVal){
                $("[name=responsible]").select2("val", val);
                $("#notice_role_list_error").text("");
            }
        }
    });

}


$(document).ready(function(){
	//初始化插件
	function initPlugins(){
		//初始化所有iCheck插件（radio & checkbox）
		$('[data-type="icheck"]').iCheck({
		    checkboxClass: 'icheckbox_minimal-blue',
		    radioClass: 'iradio_minimal-blue',
		    increaseArea: '20%' // optional
		});

		//检测算法中下拉框
		$('#tAlgorithmSelect').select2({
			placeholder: '大于'
		});

		//收敛规则中时间下拉框
		$('#ruleASelect, #ruleBSelect').select2({
			placeholder: '15分钟'
		});

		//流程列表下拉框
		$('#autoProcessFlowList').select2({
            placeholder: '加载中...',
			data: []
		});

        $("[name=responsible]").select2({});
        $("[name=phone_receiver]").select2({});

     //select2 数据绑定
        $("[data-type=vue-select2]").change(function(){
            var $this = $(this);
            var vue_attr = $this.attr("name");
            edit_strategy_vue[vue_attr] = $this.val()||"";
        });

		//通知时间段下拉框
		$('#startHour, #startMinute, #endHour, #endMinute').select2({
			placeholder: '00'
		});

        //自动处理title中的状态开关
        solution_switch = $('.js-switch-small')[0];
        switchery = new Switchery(solution_switch, { size: 'small' });
	}

	//页面事件绑定
	function eventsBind(){
		//面板折叠/展开
		$('[data-type="slideItem"]').on('click', function(){
			var $this = $(this);
            if (!edit_strategy_vue.solution_is_enable &&
                $this.closest("section").attr("id") == "auto_process" &&
                $this.closest("section").find(".icon-jiantou1").hasClass("expanded")
            ){return}
			$this.parents('.config__panel').find('.config__panelContent').css('width', '100%').slideToggle();
			$this.find('i').toggleClass('expanded');
		});

        $(".config__panelHead").on("click", function(e){
            $(e.target).find(".config__panelTool").click();
        });


    //触发条件中监控对象、检测算法、收敛规则radio切换
    $('[name="strategy_id"], [name="converge_id"], [name="show_nodata_alarm"]').on('ifChecked', function(){
        var $this = $(this),
            target = $this.attr('data-target'),
            targetItem = $('[data-id="'+target+'"]'),
            targetParent = $('[data-type="rule-wrapper"]');
            if ($this.attr("name") == "strategy_id"){
                edit_strategy_vue.strategy_id = $this.val();
                $("#strategy_id_err").text("");
                $("#strategy_option_error").text("");
            }
            if ($this.attr("name") == "converge_id"){
                edit_strategy_vue.converge_id = $this.val();
                edit_strategy_vue.converge_count = "";
                edit_strategy_vue.converge_continuous = "5";
                $("#converge_err").text("")
            }
            if ($this.attr("name") == "show_nodata_alarm"){
                edit_strategy_vue.show_nodata_alarm = $this.val();
                $("#nodata_alarm_error").text("");
                edit_strategy_vue.show_nodata_alarm==1?$('[data-id="nodata_alarm"]').removeClass('hidden'):$('[data-id="nodata_alarm"]').addClass('hidden');
                return
            }
            if(target != 'ruleNone'){
                if ($this.attr("name")=="converge_id"){
                    targetParent.removeClass('hidden');
                }
                targetItem.removeClass('hidden').siblings().addClass('hidden');
            }
            else{
                targetParent.addClass('hidden');
            }
    });


        // 通知方式 icheck
        $('[name=notice]').on('ifChanged', function(){

            var checked_notice = $("[name=notice]:checked");
            var _notice_list = [];
            for (var i= 0,len=checked_notice.length;i<len;i++){
                var item = $(checked_notice[i]);
                _notice_list.push(item.val());
            }
            if (JSON.stringify(_notice_list.sort())!=JSON.stringify(edit_strategy_vue.notice_list.slice().sort())){
                edit_strategy_vue.notice_list = _notice_list;
            }
        });
        // 通知角色
        $('[name=notice_role_list]').on('ifChanged', function(){

            var checked_roles = $("[name=notice_role_list]:checked");
            var _notice_role_list = [];
            for (var i= 0,len=checked_roles.length;i<len;i++){
                var item = $(checked_roles[i]);
                _notice_role_list.push(item.val());
            }
            if (JSON.stringify(_notice_role_list.sort())!=JSON.stringify(edit_strategy_vue.notice_role_list.slice().sort())){
                edit_strategy_vue.notice_role_list = _notice_role_list;
            }
        });


		//保存按钮
		$('.custom_strategy_edit #save').on('click', function(){
            save_page(monitor_id)
		});

		//取消按钮
		$('.custom_strategy_edit #cancel').on('click', function(){
            $("#strategy_edit_close").click();
		});

    // 自动处理通知
        $('[name=solution_notice]').on('ifChanged', function(){

            var checked_item = $("[name=solution_notice]:checked");
            var _solution_notice = [];
            for (var i= 0,len=checked_item.length;i<len;i++){
                var item = $(checked_item[i]);
                _solution_notice.push(item.val());
            }
            if (JSON.stringify(_solution_notice.sort())!=JSON.stringify(edit_strategy_vue.solution_notice.slice().sort())){
                edit_strategy_vue.solution_notice = _solution_notice;
            }
        });
        $("#updateTaskList").on("click", function(){
            refresh_solution_task_list();
        });
        refresh_solution_task_list()
	}

	initPlugins();
	eventsBind();

    if (from_overview){
        if (alarm_strategy_id=="0"){
            open_div(site_url+cc_biz_id+'/'+'config/custom/0/');
            return
        }
        if (alarm_strategy_id == "-1"){
            app_alert("策略已被删除！", "info");
            return
        }
        if (monitor_id!="-1"){
            open_div(site_url+cc_biz_id+'/'+'config/custom/'+monitor_id+'/');
        }
        if (monitor_id == "-1"){
            app_alert("监控项已被删除！", "info");
        }

    }
});

function refresh_solution_task_list(){
    $('#autoProcessFlowList').select2({
        placeholder: '加载中...',
        data: []
    });
    var solution_type = $("[name=auto_process_method]:checked").val();
    $.ajax({
        url: site_url+cc_biz_id+'/'+'get_task_list/',
        data: {solution_type: solution_type},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            if (resp.result) {
                $('#autoProcessFlowList').select2({
                    placeholder: '请选择...',
                    data: resp.data
                }).select2("val", edit_strategy_vue.solution_task_id);
            }else{
                alert_topbar("获取任务列表失败：" + resp.message, "fail");
                $('#autoProcessFlowList').select2({
                    placeholder: '加载失败...',
                    data: []
                });
            }
        }
    });
}

function add_condition(dom){
	var condition_num = $("#condition_num_id").val();
	try{
		condition_num = parseInt(condition_num);
		condition_num += 1;
		$("#condition_num_id").val(condition_num);
	}catch(e){
		console.log(e)
	}
    var td = $(dom).parent().parent();
    var condition_id = "condition-config-"+condition_num;
    var html = "";
    if (condition_num == 1){
        html = '<span class="pre-span">where</span>';
    }
    html =      "<div class='mb5 condition-div' id='"+condition_id+"' >"+ html +
    			'<label for="" class="control-label control-label-style">' +
                '<select class="logic select2_box side_select"><option>and</option><option>or</option></select>' +
                '</label>' +
        		td.children("#condition-config-0").html()+
        		"</div>";
    td.append(html)
    $("#"+condition_id).show();
    // 初始化 select2
    $("#"+condition_id+" .condition_select2").select2();
    $('#'+condition_id+' .logic').select2();
    dimension_data = get_condition_fileds();


    $("#"+condition_id+" .dimension_condition_select2").select2({data:dimension_data, dropdownAutoWidth:"true"});
    // 删除范围条件
    $("#"+condition_id+" .del_condition_a").on("click", function(){
    	// 判断是否为最后一个删除，是则清空  选择条件即可，不删除元素
    	if($(".del_condition_a:visible").length > 1){
	        $(this).parent().remove();
    	}else{
    		$("#"+condition_id+" #condition_field").select2("val", "");
	        $("#"+condition_id+" #condition_method").select2("val", "");
    		$("#"+condition_id+" #condition_value").val("");
    	}
    	if($(".del_condition_a:visible").length == 1){
    		$(".condition-div .control-label").remove();
    	}
        if ($("#strategy_edit_side  .pre-span").length == 0){
            $($(".condition-div")[0]).prepend($('<span class="pre-span">where</span>'));
            $($(".condition-div")[0]).find(".control-label").remove();
        }
    })
}


function get_condition_fileds(){
    // 初始化维度, 维度暂时不需要 timestamp
    // var dimension_data = [{id: "timestamp", text: "timestamp"}];
    var dimension_data = []
    var dimension_fields = $("#dimension_field").val() || $(".iframe-div #dimension_field").val();
    if(dimension_fields){
    	dimension_fields = dimension_fields.split(",");
	    for (var i = 0; i < dimension_fields.length; i++){
	        dimension_data.push({id: dimension_fields[i], text: dimension_fields[i]});
	    }
    }else{
        // 自定义监控图表详情页面进来获取维度字段
        for (i = 0; i < field_id_list.length; i++){
	        dimension_data.push({id: field_id_list[i], text: field_id_list[i]});
	    }
    }
    return dimension_data;
}


function init_condition_html(condition){
    // 初始化
    $(".condition-div").remove();
    $("#condition_num_id").val("0");
    // 新增第一行
    $("#condition-config-0 .add_condition_a").click();
    // 第一行不需要logic
    $("#condition-config-1 .control-label").remove();
    $("#condition-config-1").css("display", "inline");
    var index = 0;
    for (var i=0; i<condition.length; i++){
        var conf_list = condition[i];
        for (var j=0; j<conf_list.length; j++){
            var conf = conf_list[j];
            if (i!=0 || j!=0){
                $("#condition-config-"+index+" .add_condition_a").click();
            }
            index ++;
            if (j!=0){
                $("#condition-config-"+index+" .logic").val("and");
            }else{
                if (i!=0){
                    $("#condition-config-"+index+" .logic").val("or");
                }
            }
            $("#condition-config-"+index+" #condition_field").select2("val", conf["field"]);
            $("#condition-config-"+index+" #condition_method").select2("val", conf["method"]);
            $("#condition-config-"+index+" #condition_value").val(conf["value"]);
        }
    }
}

function get_monitor_condition(){
    var condition_list = [];
    var sub_condition_list = [];
    $(".condition-div").each(function(){
        var condition_id = $(this).attr("id");
        var condition_item = {};
        var logic = $(this).find("select.logic").val();
        logic = logic?logic:null;
        condition_item.field = $.trim($("#" + condition_id + " #condition_field").val());
        condition_item.method = $.trim($("#" + condition_id + " #condition_method").val());
        condition_item.value = $.trim($("#" + condition_id + " #condition_value").val()).split(",");
        if (condition_item.value.length == 1){
            condition_item.value = condition_item.value[0];
        }
        if(condition_item.field && condition_item.method && condition_item.value){
            if (logic == "or"){
                condition_list.push(sub_condition_list);
                sub_condition_list = []
            }
            sub_condition_list.push(condition_item);
        }
    });
    condition_list.push(sub_condition_list);
    return condition_list
}

function save_page(monitor_id){
    var save_button = $('.custom_strategy_edit #save');
    make_saving_button(save_button);
    if (!monitor_id){
        return
    }
    if (!check_params()){
        make_saved_button(save_button);
        return
    }
    var rules = JSON.stringify({
        converge_id: edit_strategy_vue.converge_id,
        continuous: edit_strategy_vue.converge_continuous,
        count: edit_strategy_vue.converge_count
    });
    var strategy_option = JSON.stringify({
        method: edit_strategy_vue.method,
        threshold: edit_strategy_vue.threshold,
        ceil: edit_strategy_vue.ceil,
        floor: edit_strategy_vue.floor,
        ceil_interval: edit_strategy_vue.ceil_interval,
        floor_interval: edit_strategy_vue.floor_interval
    });
    var param = {
        monitor_id: monitor_id,
        alarm_strategy_id: edit_strategy_vue.alarm_strategy_id,
        s_id: $(".iframe-div #s_id").val()?$(".iframe-div #s_id").val():$("#s_id").val(),
        rules: rules,
        strategy_id: edit_strategy_vue.strategy_id,
        strategy_option: strategy_option,
        monitor_level: edit_strategy_vue.monitor_level,
        responsible: edit_strategy_vue.responsible?edit_strategy_vue.responsible.join(","):"",
        phone_receiver: edit_strategy_vue.phone_receiver?edit_strategy_vue.phone_receiver.join(","):"",
        role_list: edit_strategy_vue.notice_role_list,
        notify_way: edit_strategy_vue.notice_list,
        alarm_start_time: edit_strategy_vue.notice_start_hh + ":" + edit_strategy_vue.notice_start_mm,
        alarm_end_time: edit_strategy_vue.notice_end_hh + ":" + edit_strategy_vue.notice_end_mm,
        nodata_alarm: edit_strategy_vue.show_nodata_alarm==1?edit_strategy_vue.nodata_alarm:"0",
        condition: JSON.stringify(get_monitor_condition()),
        display_name: edit_strategy_vue.display_name,
        solution_type: edit_strategy_vue.solution_type,
        solution_task_id: edit_strategy_vue.solution_task_id,
        solution_is_enable: edit_strategy_vue.solution_is_enable,
        solution_notice: edit_strategy_vue.solution_notice,
        };
    $.ajax({
        url: site_url+cc_biz_id+'/'+'bp/save_custom_strategy/',
        data: param,
        type: "POST",
        dataType: "json",
        success: function (resp) {
            make_saved_button(save_button);
            if (resp.result) {
                alert_topbar("操作成功", "success");
                close_stragety_edit_side();
                try{get_strategy("");}catch(e){}
                try{get_alarm_data(edit_strategy_vue.alarm_strategy_id);}catch(e){}
            }else{
                alert_topbar(resp.message, "fail");
            }
        }
    });
}

function check_params(){

    if (!edit_strategy_vue.display_name){
        $("#strategyTitle").closest("div.config__panelHead").css("border", "1px solid #ff0008");
        $("#strategyTitle").unbind("click").on("click", function(){
            $("#strategyTitle").closest("div.config__panelHead").css("border", "1px solid #ddd");
        });
        $(".strategy-edit").scrollTop(0)
        return false
    }


    if (edit_strategy_vue.strategy_id+"" == "1000"){
        if (!parseInt(edit_strategy_vue.threshold) && parseInt(edit_strategy_vue.threshold)!=0){
            $("#strategy_option_error").text("阈值必须填数字");
            $("#tAlgorithmInput").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
        if (!edit_strategy_vue.threshold){
            $("#strategy_option_error").text("请填写阈值");
            $("#tAlgorithmInput").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
    }else{
        if ((edit_strategy_vue.ceil && !parseInt(edit_strategy_vue.ceil)) && parseInt(edit_strategy_vue.ceil)!=0){
            $("#strategy_option_error").text("指标必须填数字");
            $("#tAlgorithmInput").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
        if ((edit_strategy_vue.floor && !parseInt(edit_strategy_vue.floor)) && parseInt(edit_strategy_vue.floor)!=0){
            $("#strategy_option_error").text("指标必须填数字");
            $("#tAlgorithmInput").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
        if (!edit_strategy_vue.ceil && !edit_strategy_vue.floor){
            $("#strategy_option_error").text("请填写至少一项指标");
            $("#strategy_up, #strategy_down").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
        if (((edit_strategy_vue.ceil_interval && !parseInt(edit_strategy_vue.ceil_interval)) && parseInt(edit_strategy_vue.ceil_interval)!=0)
            || ((edit_strategy_vue.floor_interval && !parseInt(edit_strategy_vue.floor_interval)) && parseInt(edit_strategy_vue.floor_interval)!=0)){
            $("#strategy_option_error").text("时间周期必须填数字");
            $("#strategy_up_interval, #strategy_down_interval").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
        if ((edit_strategy_vue.strategy_id==1003||edit_strategy_vue.strategy_id==1004)&&((edit_strategy_vue.ceil_interval && !edit_strategy_vue.ceil) || (edit_strategy_vue.floor_interval && !edit_strategy_vue.floor))){
            $("#strategy_option_error").text("指标项必填");
            $("#strategy_up_interval, #strategy_down_interval,#strategy_up, #strategy_down").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
        if ((edit_strategy_vue.strategy_id==1003||edit_strategy_vue.strategy_id==1004)&&((!edit_strategy_vue.ceil_interval && edit_strategy_vue.ceil) || (!edit_strategy_vue.floor_interval && edit_strategy_vue.floor))){
            $("#strategy_option_error").text("时间周期必填");
            $("#strategy_up_interval, #strategy_down_interval,#strategy_up, #strategy_down").unbind("click").on("click", function(){
                $("#strategy_option_error").text("")
            });
            return false
        }
    }

    if (edit_strategy_vue.converge_id != 0){
        if (!edit_strategy_vue.converge_count){
            $("#converge_err").text("请填写告警条数").removeClass("hidden");
            $("#ruleAInput, #ruleBInput").unbind("click").on("click", function(){
                $("#converge_err").text("")
            });
            return false
        }
        if (!parseInt(edit_strategy_vue.converge_count)&& parseInt(edit_strategy_vue.converge_count)!=0){
            $("#converge_err").text("告警条数必须填数字").removeClass("hidden");
            $("#ruleAInput, #ruleBInput").unbind("click").on("click", function(){
                $("#converge_err").text("")
            });
            return false
        }
        if (edit_strategy_vue.converge_count<=0){
            $("#converge_err").text("告警条数必须大于0").removeClass("hidden");
            $("#ruleAInput, #ruleBInput").unbind("click").on("click", function(){
                $("#converge_err").text("")
            });
            return false
        }
    }

    if ((edit_strategy_vue.show_nodata_alarm && !parseInt(edit_strategy_vue.nodata_alarm))&& parseInt(edit_strategy_vue.nodata_alarm)!=0){
        $("#nodata_alarm_error").text("周期值必须填数字");
        $("input[name=nodata_alarm]").unbind("click").on("click", function(){
            $("#nodata_alarm_error").text("");
        });
        return false
    }
    if (edit_strategy_vue.show_nodata_alarm==1 && edit_strategy_vue.nodata_alarm<=0){
        $("#nodata_alarm_error").text("周期值必须大于0");
        $("input[name=nodata_alarm]").unbind("click").on("click", function(){
            $("#nodata_alarm_error").text("");
        });
        return false
    }
    // 通知方式和通知角色必填
    if (edit_strategy_vue.notice_list.length == 0){
        $("#notice_list_error").text("请勾选至少一种通知方式");
        return false
    }else{
        if (edit_strategy_vue.notice_list.length==1 && edit_strategy_vue.notice_list[0] == "phone" && !edit_strategy_vue.phone_receiver){
            $("#notice_list_error").text("请选择至少一个电话联系人");
            return false
        }
    }
    if (edit_strategy_vue.notice_role_list.length == 0){
        $("#notice_role_list_error").text("请选择至少一个通知角色");
        return false
    }else{
        if (edit_strategy_vue.notice_role_list.indexOf("other") >=0 && !edit_strategy_vue.responsible){
            $("#notice_role_list_error").text("请选择至少一个其他通知人");
            return false
        }
    }
    return true
}

function make_saving_button(button){
    button.attr("disabled", true);
    button.html('保存中...')
}

function make_saved_button(button){
    button.attr("disabled", false);
    button.html('保存')
}

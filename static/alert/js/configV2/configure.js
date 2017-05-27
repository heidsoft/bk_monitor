var s_id="",
    index_category = "",
    host_index_selector = $("#main-content  #host_index"),
    // #main-content
    index_ickeck = $("#main-content [name=index_category]"),
    prform_cate_icheck = $("#main-content [name=prform_cate]"),
    strategy_id_icheck = $("#main-content [name=strategy_id]"),
    converge_id_icheck = $("#main-content [name=converge_id]"),
    save_button = $('#main-content  .bp_strategy_edit #save'),
    show_nodata_alarm_icheck = $("#main-content [name=show_nodata_alarm]"),
    solution_switch = $('#main-content .js-switch-small')[0];


function init_host_index_selector(){
    index_category = get_index_category();
    for (var i= 0,len=host_list.length;i<len;i++){
        var item = host_list[i];
        if (index_category == item.category){
            host_index_selector.select2({
                dropdownAutoWidth : true,
                data: item.children,
                placeholder: "请选择指标...",
                language: "zh-CN"
            }).off("change").change(function(){
                s_id = get_sid();
                // 展示单位
                stragety_view.host_index_unit_display = get_unit_display();
                // 判断是否是基础告警
                if (index_category=="base_alarm"){
                    make_base_alarm_view();
                }else{
                    recover_view();
                }

            });
            host_index_selector.select2("val", host_index_selector.attr("data-value")).trigger("change");
        }
    }
    if (monitor_id != 0 || args_hostindex_id!= 0){
        index_ickeck.iCheck("disable");
        host_index_selector.prop("disabled", true);
    }
}

function make_base_alarm_view(){
    // 选中基础告警时页面展示
    $("#main-content  #strategy_option_row").addClass("hidden");
    $("#main-content  #nodata_alarm_row").addClass("hidden");

}

function recover_view(){
    // 恢复正常页面展示
    $("#main-content  #strategy_option_row").removeClass("hidden");
    $("#main-content  #nodata_alarm_row").removeClass("hidden");
}

index_ickeck.on('ifChecked', function(){
    init_host_index_selector();
});


$("#back_btn_id, #main-content  #cancel").on("click", function(){
    close_div(on_div_close);
});


save_button.on('click', function(){
    duplication_strategy();
});

$("#main-content  .config__panelHead").on("click", function(e){
    $(e.target).find(".config__panelTool").click();
});

function arrary_distinct(a) {
    var temp = {};
    for (var i = 0; i < a.length; i++)
        temp[a[i]] = true;
    var r = [];
    for (var k in temp)
        r.push(k);
    return r;
}

function refresh_stragety(){
    // ajax get stragety detail and init vue
    if (alarm_strategy_id == 0) {
        if (hosts_view && multiple == 1){
            var selected_hosts = hosts_view.selected_host_list;
            var ip_list = [];
            for (var i=0; i<selected_hosts.length; i++){
                ip_list.push(selected_hosts[i].InnerIP)
            }
            ip_list = arrary_distinct(ip_list);
            stragety_view.ip = ip_list.join(" , ");
        }
        return
    }
    $.ajax({
        url: site_url+cc_biz_id+'/'+'bp/get_bp_strategy/',
        data: {alarm_strategy_id: alarm_strategy_id},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            if (resp.result) {
                strategy_data = resp.data;
                stragety_view.prform_cate = strategy_data.prform_cate;
                stragety_view.cc_set = strategy_data.cc_set;
                stragety_view.cc_module = strategy_data.cc_module;
                stragety_view.ip = strategy_data.ip;
                stragety_view.strategy_id = strategy_data.strategy_id;
                stragety_view.converge_id = strategy_data.rules.converge_id || "0";
                setTimeout(function(){
                    stragety_view.nodata_alarm = strategy_data.nodata_alarm;
                    stragety_view.converge_continuous = strategy_data.rules.continuous || "";
                    stragety_view.converge_count = strategy_data.rules.count || "";
                    stragety_view.notice_start_hh = strategy_data.notice_start_hh;
                    stragety_view.notice_start_mm = strategy_data.notice_start_mm;
                    stragety_view.notice_end_hh = strategy_data.notice_end_hh;
                    stragety_view.notice_end_mm = strategy_data.notice_end_mm;
                    stragety_view.solution_is_enable = strategy_data.solution_is_enable;
                    stragety_view.solution_type = strategy_data.solution_type;
                    stragety_view.solution_notice = strategy_data.solution_notice;
                    stragety_view.solution_task_id = strategy_data.solution_task_id;
                    stragety_view.solution_params_replace = strategy_data.solution_params_replace;
                }, 200);
                stragety_view.method = strategy_data.strategy_option.method || "eq";
                stragety_view.threshold = strategy_data.strategy_option.threshold || "";
                stragety_view.ceil = strategy_data.strategy_option.ceil || "";
                stragety_view.floor = strategy_data.strategy_option.floor || "";
                stragety_view.monitor_level = strategy_data.monitor_level;
                stragety_view.responsible = strategy_data.responsible;
                stragety_view.notice_role_list = strategy_data.role_list;
                stragety_view.notice_list = isEmpty(strategy_data.notify_way)?[]:strategy_data.notify_way;
                stragety_view.phone_receiver = strategy_data.phone_receiver;
                stragety_view.show_nodata_alarm = strategy_data.nodata_alarm==0?"0":1;
            }
        }
    });
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

function init_stragety_vue() {
    stragety_view = new Vue({
            el: '#main-content',
            data: {
                host_index_unit_display: "",    // 选中的基础性能对应的单位
                prform_cate: "ip",
                ip: "",
                cc_set: "",
                cc_module: "",
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
                nodata_alarm: "0",            // 无数据告警周期 0表示不告警
                show_nodata_alarm: "0",       // 是否启用无数据告警
                solution_type: "job",       // 自动处理，默认作业平台
                solution_task_id: "",         // 自动处理任务id
                solution_notice: [],        // 主动处理通知
                solution_is_enable: false,  // 是否开启自动处理
                solution_params_replace: ""  // 是否自动替换ip参数
            },
            computed:{
                strategy_display: function(){
                    if (this.strategy_id == 1001){
                        return "较上周同一时刻值"
                    }
                    if (this.strategy_id == 1002){
                        return "较前一时刻值"
                    }
                    return "较前一时刻值";
                }
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
                converge_count: function(val, oldVal){
                    if (parseInt(val) < 0){
                        this.converge_count = "";
                    }
                },
                nodata_alarm: function(val, oldVal){
                    if (parseInt(val) < 0){
                        this.nodata_alarm = 0;
                    }
                },
                solution_type: function(val, oldVal){
                    refresh_task_list();
                    this.solution_task_id = "";
                },
                prform_cate: function(val, oldVal){
                    prform_cate_icheck.iCheck("uncheck");
                    var $this = $("#main-content [name=prform_cate][value="+val+"]");
                    $this.iCheck("check");
                },
                strategy_id: function(val, oldVal){
                    strategy_id_icheck.iCheck("uncheck");
                    var $this = $("#main-content [name=strategy_id][value="+val+"]");
                    $this.iCheck("check");
                },
                converge_id: function(val, oldVal){
                    converge_id_icheck.iCheck("uncheck");
                    var $this = $("#main-content [name=converge_id][value="+val+"]");
                    $this.iCheck("check");
                },
                cc_set: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=cc_set]").select2("val", val).trigger("change");
                },
                solution_task_id: function(val, oldVal){
                    val = val+"";
                    $("#main-content #autoProcessFlowList").select2("val", val);
                },
                cc_module: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=cc_module]").select2("val", val);
                },
                method: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=method]").select2("val", val);
                },
                converge_continuous: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=converge_continuous]").select2("val", val);
                },
                notice_start_hh: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=notice_start_hh]").select2("val", val);
                },
                notice_start_mm: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=notice_start_mm]").select2("val", val);
                },
                notice_end_hh: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=notice_end_hh]").select2("val", val);
                },
                notice_end_mm: function (val, oldVal){
                    val = val+"";
                    $("#main-content [name=notice_end_mm]").select2("val", val);
                },
                notice_list: function (val, oldVal){
                    $("#main-content [name=notice]").prop("checked", false).iCheck('update');
                    for (var i=0;i<val.length;i++){
                        $("#main-content [name=notice][value="+val[i]+"]").prop("checked", true).iCheck('update');
                    }
                    if (val.indexOf("phone")>=0){
                        $('#main-content [name=phone_receiver]').removeClass('hidden').next().removeClass('hidden');
                    }else{
                        $('#main-content [name=phone_receiver]').addClass('hidden').next().addClass('hidden');
                        this.phone_receiver = "";
                    }
                    $("#main-content #notice_list_error").text("");
                },
                notice_role_list: function (val, oldVal){
                    $("#main-content [name=notice_role_list]").prop("checked", false).iCheck('update');
                    for (var i=0;i<val.length;i++){
                        $("#main-content [name=notice_role_list][value="+val[i]+"]").prop("checked", true).iCheck('update');
                    }
                    if (val.indexOf("other")>=0){
                        $('#main-content [name=responsible]').removeClass('hidden');
                    }else{
                        $('#main-content [name=responsible]').addClass('hidden');
                        this.responsible = "";
                    }
                    $("#main-content #notice_role_list_error").text("");
                },
                solution_params_replace: function(val, oldVal){
                    $("#main-content [name=solution_params_replace]").prop("checked", false).iCheck('update');
                    $("#main-content [name=solution_params_replace][value="+val+"]").prop("checked", true).iCheck('update');
                },
                solution_notice: function(val, oldVal){
                    $("#main-content [name=solution_notice]").prop("checked", false).iCheck('update');
                    for (var i=0;i<val.length;i++){
                        $("#main-content [name=solution_notice][value="+val[i]+"]").prop("checked", true).iCheck('update');
                    }
                },
                solution_is_enable: function(val, oldVal){
                    switchery.switcher.remove();
                    solution_switch.checked=Boolean(val);
                    switchery = new Switchery(solution_switch, { size: 'small' });
                    var i_btn = $("#main-content #auto_process").find(".icon-jiantou1");
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
                phone_receiver: function (val, oldVal){
                    $("#main-content [name=phone_receiver]").select2("val", val);
                    $("#main-content #notice_list_error").text("");
                },
                responsible: function (val, oldVal){
                    $("#main-content [name=responsible]").select2("val", val);
                    $("#main-content #notice_role_list_error").text("");
                },
                show_nodata_alarm: function(val, oldVal){
                    show_nodata_alarm_icheck.iCheck("uncheck");
                    var $this = $("#main-content [name=show_nodata_alarm][value="+val+"]");
                    $this.iCheck("check");
                },
            }
        }
    );




    //触发条件中监控对象、检测算法、收敛规则radio切换
    $('#main-content [name="prform_cate"], #main-content [name="strategy_id"], #main-content [name="converge_id"], #main-content [name="show_nodata_alarm"]').on('ifChecked', function(){
        var $this = $(this),
            target = $this.attr('data-target'),
            targetItem = $('#main-content [data-id="'+target+'"]'),
            targetParent = $('#main-content [data-type="rule-wrapper"]');
            if ($this.attr("name") == "prform_cate"){
                stragety_view.prform_cate = $this.val();
                $("#main-content  #prform_cate_err").text("");
                $("#main-content  #ip_err").text("");
            }
            if ($this.attr("name") == "strategy_id"){
                stragety_view.strategy_id = $this.val();
                $("#main-content  #strategy_id_err").text("");
                $("#main-content  #strategy_option_error").text("");
            }
            if ($this.attr("name") == "converge_id"){
                stragety_view.converge_id = $this.val();
                stragety_view.converge_count = "";
                stragety_view.converge_continuous = "5";
                $("#main-content  #converge_err").text("")
            }
            if ($this.attr("name") == "show_nodata_alarm"){
                stragety_view.show_nodata_alarm = $this.val();
                $("#main-content  #nodata_alarm_error").text("");
                stragety_view.show_nodata_alarm==1?$('#main-content  [data-id="nodata_alarm"]').removeClass('hidden'):$('#main-content  [data-id="nodata_alarm"]').addClass('hidden');
                return
            }
        targetItem.removeClass('hidden').siblings().addClass('hidden');
        if(target != 'ruleNone'){
            if ($this.attr("name") == "converge_id"){
                targetParent.removeClass('hidden');
            }
        }
        else{
            if ($this.attr("name") == "converge_id"){
                targetParent.removeClass('hidden');
            }
        }
    });

    //select2 数据绑定
    $("#main-content  [data-type=vue-select2]").change(function(){
        var $this = $(this);
        var vue_attr = $this.attr("name");
        stragety_view[vue_attr] = $this.val()||"";
    });

    // 通知方式 icheck
    $('#main-content [name=notice]').on('ifChanged', function(){

        var checked_notice = $("#main-content [name=notice]:checked");
        var _notice_list = [];
        for (var i= 0,len=checked_notice.length;i<len;i++){
            var item = $(checked_notice[i]);
            _notice_list.push(item.val());
        }
        if (JSON.stringify(_notice_list.sort())!=JSON.stringify(stragety_view.notice_list.slice().sort())){
            stragety_view.notice_list = _notice_list;
        }
    });
    // 通知角色
    $('#main-content [name=notice_role_list]').on('ifChanged', function(){

        var checked_roles = $("#main-content [name=notice_role_list]:checked");
        var _notice_role_list = [];
        for (var i= 0,len=checked_roles.length;i<len;i++){
            var item = $(checked_roles[i]);
            _notice_role_list.push(item.val());
        }
        if (JSON.stringify(_notice_role_list.sort())!=JSON.stringify(stragety_view.notice_role_list.slice().sort())){
            stragety_view.notice_role_list = _notice_role_list;
        }
    });
    // 自动处理通知
    $('#main-content [name=solution_notice]').on('ifChanged', function(){

        var checked_item = $("#main-content [name=solution_notice]:checked");
        var _solution_notice = [];
        for (var i= 0,len=checked_item.length;i<len;i++){
            var item = $(checked_item[i]);
            _solution_notice.push(item.val());
        }
        if (JSON.stringify(_solution_notice.sort())!=JSON.stringify(stragety_view.solution_notice.slice().sort())){
            stragety_view.solution_notice = _solution_notice;
        }
    });
    // 自动处理参数替换故障ip
    $('#main-content [name=solution_params_replace]').on('ifChanged', function(){
        var checked_item = $("#main-content [name=solution_params_replace]:checked");
        stragety_view.solution_params_replace = checked_item.length > 0?"replace":""
    });
    //自动处理title中的状态开关
    switchery = new Switchery(solution_switch, { size: 'small' });

    refresh_task_list()
}

function get_sid(){
    if (host_index_selector.select2("data")){
        return host_index_selector.select2("data").s_id;
    }
    return ""
}

function get_unit_display(){
    if (host_index_selector.select2("data")){
        return host_index_selector.select2("data").unit;
    }
    return ""
}

function get_hostindex_id(){
    if (host_index_selector.select2("data")){
        return host_index_selector.select2("data").id;
    }
    return ""
}

function get_index_category(){
    return $("#main-content [name=index_category]:checked").val();
}
$(function(){
    init_stragety_vue();
    init_host_index_selector();
    refresh_stragety();

});

function refresh_task_list(){
    $('#main-content #autoProcessFlowList').select2({
        placeholder: '加载中...',
        data: []
    });
    var solution_type = $("#main-content [name=auto_process_method]:checked").val();
    $.ajax({
        url: site_url+cc_biz_id+'/'+'get_task_list/',
        data: {solution_type: solution_type},
        type: "GET",
        dataType: "json",
        success: function (resp) {
            if (resp.result) {
                $('#main-content #autoProcessFlowList').select2({
                    placeholder: '请选择...',
                    data: resp.data
                }).select2("val", stragety_view.solution_task_id);
            }else{
                alert_topbar("获取任务列表失败：" + resp.message, "fail");
                $('#main-content #autoProcessFlowList').select2({
                    placeholder: '加载失败...',
                    data: []
                });
            }
        }
    });
}

function check_bp_params(){
    if (!get_hostindex_id()){
        var error_span = host_index_selector.closest(".config__rowContent").find(".config__errorMsg").text("请选择性能指标");
        host_index_selector.on("select2-opening", function(){
            error_span.text("");
        });
        return false
    }
    if (!stragety_view.prform_cate){
        $("#main-content  #prform_cate_err").text("请选择性能指标");
        return false
    }
    if (stragety_view.prform_cate=="ip"){
        var new_ip_list = [];
        var ip_rex = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/;
        var ip_list = stragety_view.ip.split(",");
        for (var i= 0,len=ip_list.length;i<len;i++){
            var ip = ip_list[i].trim();
            if (ip.match(ip_rex)){
                new_ip_list.push(ip)
            }
        }
        stragety_view.ip = new_ip_list.join(",");
        if(!stragety_view.ip){
            $("#main-content  #ip_err").text("请填写正确的ip信息");
            $("#main-content  #monitorIP").click(function(){
                $("#main-content  #ip_err").text("");
            });
            return false
        }
    }
    if (!$("#main-content #strategy_option_row").hasClass("hidden")){
        if (!stragety_view.strategy_id){
            $("#main-content  #strategy_id_err").text("请选择检测算法");
            return false
        }
        if (stragety_view.strategy_id+"" == "1000"){
            if (!stragety_view.threshold){
                $("#main-content  #strategy_option_error").text("请填写阈值");
                $("#main-content  #tAlgorithmInput").unbind("click").on("click", function(){
                    $("#main-content  #strategy_option_error").text("")
                });
                return false
            }
        }else{
            if (!stragety_view.ceil && !stragety_view.floor){
                $("#main-content  #strategy_option_error").text("请填写至少一项指标");
                $("#main-content  #strategy_up, #main-content  #strategy_down").unbind("click").on("click", function(){
                    $("#main-content  #strategy_option_error").text("")
                });
                return false
            }
        }
    }

    if (stragety_view.converge_id != 0){
        if (!stragety_view.converge_count){
            $("#main-content  #converge_err").text("请填写告警条数").removeClass("hidden");
            $("#main-content  #ruleAInput, #main-content  #ruleBInput").unbind("click").on("click", function(){
                $("#main-content  #converge_err").text("")
            });
            return false
        }
    }
    if (!$("#main-content #nodata_alarm_row").hasClass("hidden")){
        if ((stragety_view.show_nodata_alarm && !parseInt(stragety_view.nodata_alarm))&& parseInt(stragety_view.nodata_alarm)!=0){
            $("#main-content  #nodata_alarm_error").text("周期值必须填数字");
            $("#main-content [name=nodata_alarm]").unbind("click").on("click", function(){
                $("#main-content  #nodata_alarm_error").text("");
            });
            return false
        }
        if (stragety_view.show_nodata_alarm==1 && stragety_view.nodata_alarm<=0){
            $("#main-content  #nodata_alarm_error").text("周期值必须大于0");
            $("#main-content [name=nodata_alarm]").unbind("click").on("click", function(){
                $("#main-content  #nodata_alarm_error").text("");
            });
            return false
        }
    }
    // 通知方式和通知角色必填
    if (stragety_view.notice_list.length == 0){
        $("#main-content #notice_list_error").text("请勾选至少一种通知方式");
        return false
    }else{
        if (stragety_view.notice_list.length==1 && stragety_view.notice_list[0] == "phone" && !stragety_view.phone_receiver){
            $("#main-content #notice_list_error").text("请选择至少一个电话联系人");
            return false
        }
    }
    if (stragety_view.notice_role_list.length == 0){
        $("#main-content #notice_role_list_error").text("请选择至少一个通知角色");
        return false
    }else{
        if (stragety_view.notice_role_list.indexOf("other") >=0 && !stragety_view.responsible){
            $("#main-content #notice_role_list_error").text("请选择至少一个其他通知人");
            return false
        }
    }

    return true
}

function _duplication_strategy(){
    make_saving_button(save_button);
    $.ajax({
    url: site_url+cc_biz_id+'/'+'bp/duplication_strategy/',
    data: {
        hostindex_id: get_hostindex_id(),
        prform_cate: stragety_view.prform_cate,
        ip: stragety_view.ip,
        cc_set: stragety_view.cc_set,
        cc_module: stragety_view.cc_module,
        alarm_strategy_id: alarm_strategy_id
    },
    type: "POST",
    dataType: "json",
    success: function (resp) {
        make_saved_button(save_button);
        if (resp.result) {
            save_bp_page();
        }else{
            var old_alarm_strategy_id = resp.data;
            app_confirm(resp.message, function(){
                save_bp_page();
            })
        }
    }
});
}

function duplication_strategy(){
    // 保存基础性能监控
    if (!check_bp_params()){
        $("#main-content  .config__panel").find("i.expanded").click();
        return
    }
    // 检测当前ip是否仍然包含在策略范围内
    if (hosts_view && alarm_strategy_id != 0 && hosts_view.checked_host){
        if (!host_in_monitor_range(hosts_view.checked_host.InnerIP)){
            app_confirm("策略保存后，主机:"+ hosts_view.checked_host.InnerIP + "将不再关联该策略，确认是否继续。", function(){
                // 检测重复的告警策略
                _duplication_strategy()
            });
            return
        }
    }
    _duplication_strategy()

}


function host_in_monitor_range(ip){
    if (stragety_view.prform_cate == "set"){
        var set_id = stragety_view.cc_set;
        var newArray = hosts.slice();
        if (set_id && set_id != "0"){
            newArray = filter_hosts_by(hosts, function(_host){
                return _host.SetID;
            }, set_id)
        }
        // 过滤 mod
        var mod_id = stragety_view.cc_module;
        if (mod_id && mod_id != "0"){
            newArray = filter_hosts_by(newArray, function(_host){
                return _host.ModuleID;
            }, mod_id)
        }
        var exists = filter_hosts_by(newArray, function(_host){
                return _host.InnerIP;
            }, ip);
        if (exists.length == 0 ){
            return false
        }
    }
    if (stragety_view.prform_cate == "ip"){
        var ips = stragety_view.ip.split(",");
        return ips.indexOf(ip) >= 0;
    }
    return true

}

function save_bp_page(){
    make_saving_button(save_button);
    var rules = JSON.stringify({
        converge_id: stragety_view.converge_id,
        continuous: stragety_view.converge_continuous,
        count: stragety_view.converge_count
    });
    var strategy_option = JSON.stringify({
        method: stragety_view.method,
        threshold: stragety_view.threshold,
        ceil: stragety_view.ceil,
        floor: stragety_view.floor
    });
    var param = {
        alarm_strategy_id: alarm_strategy_id,
        s_id: get_sid(),
        hostindex_id: get_hostindex_id(),
        prform_cate: stragety_view.prform_cate,
        cc_set: stragety_view.cc_set,
        cc_module: stragety_view.cc_module,
        ip: stragety_view.ip,
        rules: rules,
        strategy_id: stragety_view.strategy_id,
        strategy_option: strategy_option,
        monitor_level: stragety_view.monitor_level,
        responsible: stragety_view.responsible?stragety_view.responsible.join(","):"",
        phone_receiver: stragety_view.phone_receiver?stragety_view.phone_receiver.join(","):"",
        role_list: stragety_view.notice_role_list,
        notify_way: stragety_view.notice_list,
        alarm_start_time: stragety_view.notice_start_hh + ":" + stragety_view.notice_start_mm,
        alarm_end_time: stragety_view.notice_end_hh + ":" + stragety_view.notice_end_mm,
        nodata_alarm: stragety_view.show_nodata_alarm==1?stragety_view.nodata_alarm:"0",
        solution_type: stragety_view.solution_type,
        solution_task_id: stragety_view.solution_task_id,
        solution_is_enable: stragety_view.solution_is_enable,
        solution_notice: stragety_view.solution_notice,
        solution_params_replace: stragety_view.solution_params_replace,
        };
    $.ajax({
        url: site_url+cc_biz_id+'/'+'bp/save_bp_strategy/',
        data: param,
        type: "POST",
        dataType: "json",
        success: function (resp) {
            make_saved_button(save_button);
            if (resp.result) {
                alert_topbar("操作成功", "success");
                close_div(on_div_close);
                if (hosts_view && hosts_view.checked_host){
                    render_alarm_strategy(hosts_view.checked_host.id);
                }
            }else{
                alert_topbar("保存失败：" + resp.message, "fail");
            }
        }
    });
}

function make_saving_button(button){
    button.attr("disabled", true);
    button.html('保存中...')
}

function make_saved_button(button){
    button.attr("disabled", false);
    button.html('保存')
}

// 告警策略配置页面js
function add_alarm_strategy(alram_strategy_id, scenario, edit_type, callback){
	if(alram_strategy_id == '0'){
		var title = '新增监控策略';
	}else{
		var title = '编辑监控策略';
	}
    var monitor_field = $("#monitor_field").val()
    if(scenario == "performance" && monitor_field == ""){
        $("#tip_config").text("请选择监控指标")
        return false;
    } else {
        $("#tip_config").text("")
    }
	var url = site_url+cc_biz_id+'/config/strategy_add/'+alram_strategy_id+'/';
	$.get(url,{
		'scenario': scenario,
		'edit_type': edit_type
	}, function(data){
	    var d = dialog({
	    	id: 'add_alarm_strategy',
		    width: 910,
		    height: 300,
		    padding: 0,
		    title: title,
		    content: data.data
		});
		d.showModal();
        if (callback){
            callback();
        }
	}, 'json')
}
function del_alarm_strategy(obj, alram_strategy_id, edit_type, callback){
	if($(obj).attr("disabled")){
		return false;
	}
	$(obj).attr("disabled", true);
	
	var confirm_content = "确认删除该监控策略?";
    _app_confirm(confirm_content, function(){
        $("#alarms_strategy_table_loading").removeClass("hidden");
        $.ajax({
            type: 'POST',
            dataType: "json",
            url: site_url+cc_biz_id+'/config/strategy_del/'+alram_strategy_id+'/',
            data: {
            	'edit_type': edit_type
            },
            success: function(data){
                if(data.result){
                	// 列表页面快捷删除成功提示 TOCHANGE
                	if(edit_type == 'quick'){
                		alert_topbar(data.message, "success");
                        var status = $(obj).closest("td").prev().find("span").attr("class");
                        var enable_cnt = parseInt($(obj).closest("tr.k-detail-row").prev().find(".text-success").text());
                        var disable_cnt = parseInt($(obj).closest("tr.k-detail-row").prev().find(".text-danger").text());
                        enable_cnt = (status == "text-success")?(enable_cnt - 1) :(enable_cnt);
                        disable_cnt = (status == "text-danger")?(disable_cnt - 1) :(disable_cnt);
                        $(obj).closest("tr.k-detail-row").prev().find(".text-success").text(enable_cnt);
                        $(obj).closest("tr.k-detail-row").prev().find(".text-danger").text(disable_cnt);
                	}
                  // 刷新数据
			      callback(alram_strategy_id);
			      // 记录告警策略操作动作
			      $("#is_alarm_strategy_edit").val('1');
                }
                else{
                	$(obj).attr("disabled", false);
                	d = app_alert(data.message, "fail");
                }
            }
        })
    }, function(){
    	$(obj).attr("disabled", false);
    });
}
function isInteger(obj) {
    return (obj | 0) === obj
}
//多选项验证不为空
function check_not_empty_checkbox(obj){
	var flag = true;
	var cur_name = $(obj).attr('name');
	var length = $("input[name="+cur_name+"]:checked").length;
	if(length == 0 ){
		$("#tip_"+cur_name).html('必选');
		//$(obj).focus();
		$(obj).parents('.form-group').addClass('has-error');
		flag = false;
	}else{
		$("#tip_"+cur_name).html('');
		$(obj).parents('.form-group').removeClass('has-error');
	}
	return flag;
}
//验证不为空的元素
function check_not_empty_element(obj){
	var flag = true;
	var cur_val = $.trim($(obj).val());
	var cur_id = $(obj).attr('id');
	var r =  /^[0-9\.,]*$/;   //判断字符串是否为数字 . ,  
    var test_input = cur_id=='static_ip' ? r.test(cur_val) : true;
	if(cur_val == '' || !test_input){
		var text = cur_id=='static_ip' ? '请输入IP，多个 IP 以英文逗号(,)分隔' : '必填';
		$("#tip_"+cur_id).html(text);
		//$(obj).focus();
		$(obj).parents('.form-group').addClass('has-error');
		flag = false;
	}else{
		$("#tip_"+cur_id).html('');
		$(obj).parents('.form-group').removeClass('has-e rror');
	}
	return flag;
}
//验证数字元素
function check_number_element(obj){
	var flag = true;
	var cur_val = $.trim($(obj).val());
	var cur_id = $(obj).attr('id');
	var cur_name = $(obj).attr('name');
	if(cur_val == '' || isInteger(cur_val) ){
		$("#tip_"+cur_id).html('请输入一个整数');
		//$(obj).focus();
		$(obj).parents('.form-group').addClass('has-error');
		flag = false;
	}else{
		$("#tip_"+cur_id).html('');
		$(obj).parents('.form-group').removeClass('has-error');
	}
	return flag;
}
// 验证浮点数
function check_decimal_element(obj){
	var flag = true;
	var cur_val = $.trim($(obj).val());
	var cur_id = $(obj).attr('id');
	var cur_name = $(obj).attr('name');
	var r =  /^[-+]?[0-9]*\.?[0-9]+$/;   //判断字符串是否为数字  
    var test_input = r.test(cur_val);
	if(cur_val == '' || !test_input ){
		$("#tip_"+cur_id).html('请输入一个数字');
		//$(obj).focus();
		$(obj).parents('.form-group').addClass('has-error');
		flag = false;
	}else{
		$("#tip_"+cur_id).html('');
		$(obj).parents('.form-group').removeClass('has-error');
	}
	return flag;
	
}
//算法参数, 同时验证参数
function get_strategy_option(config_type){
    var strategy_option = {}
    if(config_type == "8" || config_type == "16"){
    	return {'result':true, 'data':{}}
    }
    var r =  /^[-+]?[0-9]*\.?[0-9]+$/;   //判断字符串是否为数字 
    if(config_type == "2" || config_type == "32"){
        strategy_option.continuous = $.trim($("#" + config_type + "_continuous").val());
        if(!strategy_option.continuous){
        	$("#tip_"+ config_type + "_continuous").html('必填');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_continuous").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_continuous").focus();
    		return {'result':false, 'data':{}}
        }
        
        strategy_option.trend = $.trim($("input[name="+ config_type +"_trend]:checked").val());
        if(!strategy_option.trend ){
        	strategy_option.trend =  $.trim($("#" + config_type + "_trend").val());
        }
        if(!strategy_option.trend){
        	$("#tip_"+ config_type + "_trend").html('必填');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_trend").parents('.form-group').addClass('has-error');
    		return {'result':false, 'data':{}}
        }
        strategy_option.threshold = $.trim($("#" + config_type + "_threshold").val());
        var test_input = r.test(strategy_option.threshold);
        if(!test_input){
        	$("#tip_"+ config_type + "_threshold").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_threshold").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_threshold").focus();
    		return {'result':false, 'data':{}}
        }
    }
    else if(config_type == "99"){
        strategy_option.continuous = $.trim($("#" + config_type + "_continuous").val());
        if(!strategy_option.continuous){
            $("#tip_"+ config_type + "_continuous").html('必填');
            $("#base_config_a").click();
            $("#tip_"+ config_type + "_continuous").parents('.form-group').addClass('has-error');
            $("#" + config_type + "_continuous").focus();
            return {'result':false, 'data':{}}
        }
    }
    else if(config_type == "30"){        
        strategy_option.ratio = $.trim($("#" + config_type + "_ratio").val());
        var test_ratio = r.test(strategy_option.ratio);
        if(!test_ratio){
            $("#tip_"+ config_type + "_ratio").html('请输入一个数字');
            $("#base_config_a").click();
            $("#tip_"+ config_type + "_ratio").parents('.form-group').addClass('has-error');
            $("#" + config_type + "_ratio").focus();
            return {'result':false, 'data':{}}
        }
        strategy_option.trend = $.trim($("input[name="+ config_type +"_trend]:checked").val());
        strategy_option.back_days = "7"
        if(!strategy_option.trend ){
            strategy_option.trend =  $.trim($("#" + config_type + "_trend").val());
        }
        if(!strategy_option.trend){
            $("#tip_"+ config_type + "_trend").html('必填');
            $("#base_config_a").click();
            $("#tip_"+ config_type + "_trend").parents('.form-group').addClass('has-error');
            return {'result':false, 'data':{}}
        }
    }
    else if(config_type == "31"){        
        strategy_option.ratio = $.trim($("#" + config_type + "_ratio").val());
        var test_ratio = r.test(strategy_option.ratio);
        if(!test_ratio){
            $("#tip_"+ config_type + "_ratio").html('请输入一个数字');
            $("#base_config_a").click();
            $("#tip_"+ config_type + "_ratio").parents('.form-group').addClass('has-error');
            $("#" + config_type + "_ratio").focus();
            return {'result':false, 'data':{}}
        }
        strategy_option.trend = $.trim($("input[name="+ config_type +"_trend]:checked").val());
        strategy_option.back_days = "1"
        if(!strategy_option.trend ){
            strategy_option.trend =  $.trim($("#" + config_type + "_trend").val());
        }
        if(!strategy_option.trend){
            $("#tip_"+ config_type + "_trend").html('必填');
            $("#base_config_a").click();
            $("#tip_"+ config_type + "_trend").parents('.form-group').addClass('has-error');
            return {'result':false, 'data':{}}
        }
    }
    else if(config_type == "10"){        
        strategy_option.ratio = $.trim($("#" + config_type + "_ratio").val());
        var test_ratio = r.test(strategy_option.ratio);
        if(!test_ratio){
        	$("#tip_"+ config_type + "_ratio").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_ratio").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_ratio").focus();
    		return {'result':false, 'data':{}}
        }
        strategy_option.shock = $.trim($("#" + config_type + "_shock").val());
        var test_shock = r.test(strategy_option.shock);
        if(!test_shock){
        	$("#tip_"+ config_type + "_shock").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_shock").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_shock").focus();
    		return {'result':false, 'data':{}}
        }
        strategy_option.baseline = $.trim($("#" + config_type + "_baseline").val());
        var test_baseline = r.test(strategy_option.baseline);
        if(!test_baseline){
        	$("#tip_"+ config_type + "_baseline").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_baseline").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_baseline").focus();
    		return {'result':false, 'data':{}}
        }
        strategy_option.continuous = $.trim($("#" + config_type + "_continuous").val());
        if(!strategy_option.continuous){
        	$("#tip_"+ config_type + "_continuous").html('必填');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_continuous").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_continuous").focus();
    		return {'result':false, 'data':{}}
        }
    }
    else if(config_type == "11"){
        strategy_option.times = $.trim($("#" + config_type + "_times").val());
        var test_times = r.test(strategy_option.times);
        if(!test_times){
        	$("#tip_"+ config_type + "_times").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_times").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_times").focus();
    		return {'result':false, 'data':{}}
        }
        strategy_option.baseline = $.trim($("#" + config_type + "_baseline").val());
        var test_baseline = r.test(strategy_option.baseline);
        if(!test_baseline){
        	$("#tip_"+ config_type + "_baseline").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_baseline").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_baseline").focus();
    		return {'result':false, 'data':{}}
        }
        strategy_option.trend = $.trim($("input[name="+ config_type +"_trend]:checked").val());
        if(!strategy_option.trend){
        	$("#tip_"+ config_type + "_trend").html('必填');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_trend").parents('.form-group').addClass('has-error');
    		return {'result':false, 'data':{}}
        }
        strategy_option.back_days = $.trim($("#" + config_type + "_back_days").val());
        if(!strategy_option.back_days){
        	$("#tip_"+ config_type + "_back_days").html('必填');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_back_days").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_back_days").focus();
    		return {'result':false, 'data':{}}
        }

    }
    else if(config_type == "12"){
        strategy_option.ratio = $.trim($("#" + config_type + "_ratio").val());
        var test_ratio = r.test(strategy_option.ratio);
        if(!test_ratio){
        	$("#tip_"+ config_type + "_ratio").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_ratio").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_ratio").focus();
    		return {'result':false, 'data':{}}
        } 
        strategy_option.baseline = $.trim($("#" + config_type + "_baseline").val());
        var test_baseline = r.test(strategy_option.baseline);
        if(!test_baseline){
        	$("#tip_"+ config_type + "_baseline").html('请输入一个数字');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_baseline").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_baseline").focus();
    		return {'result':false, 'data':{}}
        }
        strategy_option.trend = $.trim($("input[name="+ config_type +"_trend]:checked").val());
        if(!strategy_option.trend){
        	$("#tip_"+ config_type + "_trend").html('必填');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_trend").parents('.form-group').addClass('has-error');
    		return {'result':false, 'data':{}}
        }
        strategy_option.back_days = $.trim($("#" + config_type + "_back_days").val());
        if(!strategy_option.back_days){
        	$("#tip_"+ config_type + "_back_days").html('必填');
        	$("#base_config_a").click();
    		$("#tip_"+ config_type + "_back_days").parents('.form-group').addClass('has-error');
    		$("#" + config_type + "_back_days").focus();
    		return {'result':false, 'data':{}}
        }
    }
    
    return {'result':true, 'data':strategy_option};
}

//筛选条件，非必填，不验证参数
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

//通知处理参数， 验证参数
function get_alarm_def_config(){
    var alarm_def_config = {}
    alarm_def_config.notify = {"role_list": [], "notify_way":[]};
    var notify_length = $("input[name='notify']:checked").length;
    if (notify_length==0){
    	$("#tip_notify").html('必选');
    	$("#notify_a").click();
		$("#tip_notify").parents('.form-group').addClass('has-error');
		return {'result':false, 'data':{}}
    }
    var notify_length = $("input[name='role']:checked").length;
    if (notify_length==0){
    	$("#tip_notify").html('必选');
    	$("#notify_a").click();
		$("#tip_role").parents('.form-group').addClass('has-error');
		return {'result':false, 'data':{}}
    }
    // 通知方式拼接
    $("input[name='notify']:checked").each(function () {
    	alarm_def_config.notify["notify_way"].push(this.value);
//        if(this.value == "phone_failure"){
//            alarm_def_config.notify["failure_notify_phone"] = true
//        }
//        else{
//            alarm_def_config.notify["begin_notify_" + this.value] = true
//            alarm_def_config.notify["success_notify_" + this.value] = true
//            alarm_def_config.notify["failure_notify_" + this.value] = true
//        }
    })
    $("input[name='role']:checked").each(function () {
        alarm_def_config.notify["role_list"].push(this.value);
        if(this.value == "PmpDBAMajor"){
            alarm_def_config.notify["role_list"].push("PmpDBABackup")
        }
    })
    alarm_def_config.responsible = $("#member").val();
    alarm_def_config.solution_id = $("#solution_id").val();
    return {'result':true, 'data':alarm_def_config}
}

//收敛规则，验证参数
function get_rules(){
	var rules = {};

    rules.is_converge = $("input[name=is_converge]:checked").val()

	rules.converge_count = $.trim($("#converge_count").val());
	if(!rules.converge_count && rules.is_converge == "1"){
		$("#tip_converge_count").html('请收入一个整数');
		$("#rule_a").click();
		$("#converge_count").parents('.form-group').addClass('has-error');
		$("#converge_count").focus();
		return {'result':false, 'data':{}}
	}

	rules.converge_period = $.trim($("#converge_period").val());
	if(!rules.converge_period && rules.is_converge == "1"){
		$("#tip_converge_period").html('请收入一个整数');
		$("#rule_a").click();
		$("#converge_period").parents('.form-group').addClass('has-error');
		$("#converge_period").focus();
		return {'result':false, 'data':{}}
	}
	return {'result':true, 'data':rules}
}

function get_perform_param(scenario){
	var perform = {};
    if(scenario == "keyword"){
        form_class = "keyword-form"
    } else if(scenario == "performance" || scenario == "basic"){
        form_class = "performance-form"
    } else if(scenario == "shield"){
        form_class = "shield-form"
    } else {
        return {'result':true, 'data':perform}
    }
	perform.cate = $("." + form_class + " input[name=prform_cate]:checked").val();
	
	if(perform.cate == 'ip'){
		var r =  /^[0-9\.,]*$/;   //判断字符串是否为数字 . ,  
		perform.ip = $.trim($("." + form_class + " #static_ip").val());
        perform.plat_id = $("." + form_class + " #dynamic_plat_id").val()
		if((!perform.ip || !r.test(perform.ip))){
            if(scenario == "shield"){
                $(".shield-form #error_message").html("请输入IP，多个 IP 以英文逗号(,)分隔");
            } else {
                $("." + form_class + " #tip_static_ip").html('请输入IP，多个 IP 以英文逗号(,)分隔');
                $("#base_config_a").click();
                $("." + form_class + " #tip_static_ip").parents('.form-group').addClass('has-error');
            }
			return {'result':false, 'data':{}}
		}
	}else if(perform.cate == 'set'){
		perform.cc_set = $("." + form_class + " #dynamic_cc_set").val() ? $("." + form_class + " #dynamic_cc_set").val().join() : '';
		perform.cc_module = $("." + form_class + " #dynamic_cc_module").val() ? $("." + form_class + " #dynamic_cc_module").val().join() : '';
	}
	
	return {'result':true, 'data':perform}
}

function get_keyword_param(scenario){
    var keyword = {};
    keyword.log_path = $("#log_path").val();

    keyword.keywords = []
    $(".keyword-div").each(function(){
        var keyword_id = $(this).attr("id")
        keyword_item = $.trim($("#" + keyword_id + " #keyword").val());
        if(keyword_item){
            keyword.keywords.push(keyword_item)
        }
    })

    if(keyword.keywords.length == 0 && scenario == "keyword"){
        // $("#tip_keyword").html('必填');
        $("#base_config_a").click();
        $("#tip_keyword").parents('.form-group').addClass('has-error');
        return {'result':false, 'data':{}}
    }

    return {'result': true, 'data': keyword}
}

// 组装参数，并验证
function get_submit_param(){
	var param = {};
	// 场景参数
	var scenario = $("#strategy_scenario_id").val();
	param.scenario = scenario;
	// 基础性能参数判断
	perform_data = get_perform_param(scenario);

    keyword_data = get_keyword_param(scenario);
	
	if(!perform_data.result){return false;}
	param.perform = perform_data.data;

	if(!keyword_data.result){return false;}
    param.keyword = keyword_data.data;

	// 告警级别
	param.monitor_level = $("#monitor_level").val();
	if(!param.monitor_level){
		$("#tip_monitor_level").html('请填写告警级别');
		$("#base_config_a").click();
		$("#monitor_level").parents('.form-group').addClass('has-error');
		return false;
	}
	console.log(param)
	// 算法
    if(param.scenario == "basic"){
        param.strategy_id = -1
        param.strategy_option = {}
    } else {
        param.strategy_id = $("#config_type").val();
        strategy_data = get_strategy_option(param.strategy_id);
        if(!strategy_data.result){return false;}
        param.strategy_option = strategy_data.data;
    }
	
	//筛选条件，非必填，不验证参数
	param.condition = get_monitor_condition();
	
	// 通知处理参数， 验证参数
	notiry_data = get_alarm_def_config();
	console.log(notiry_data);
	if(!notiry_data.result){return false;}
	param.monitor_config = notiry_data.data;
	
	// 收敛规则，验证参数
	rules_data = get_rules();
	if(!rules_data.result){return false;}
	param.rules = rules_data.data;
	
	return param;
}
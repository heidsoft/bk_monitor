$(document).ready(function(){
	//初始化插件
	function initPlugins(){
		//初始化所有iCheck插件（radio & checkbox）
		$('#main-content [data-type="icheck"]').iCheck({
		    checkboxClass: 'icheckbox_minimal-blue',
		    radioClass: 'iradio_minimal-blue',
		    increaseArea: '20%' // optional
		});

		////指标名称下拉框
		//$('#indexName').select2({
		//	placeholder: '5分钟平均负载（乘以100）'
		//});

		//监控对象中SET下拉框
		$('#main-content #monitorSET').select2({
            placeholder: '默认全选',
			data: sets,
		}).change(function(){
            $('#main-content #monitorModule').val("").select2({
                data: [],
                placeholder: "加载中...",
                language: "zh-CN"
            });
            $.ajax({
                url: site_url+cc_biz_id+'/'+'get_cc_module/',
                data: {"set_id": $('#main-content #monitorSET').select2("val")},
                type: "GET",
                dataType: "json",
                success: function (resp) {
                    if (resp.result) {
                        var mods = resp.data;
                        var init = filter_hosts_by(mods, function(mod){
                            return mod.id
                        }, stragety_view.cc_module||"0").length;
                        if (init == 0 ){
                            stragety_view.cc_module = "0"
                        }
                        $('#main-content #monitorModule').select2({
                            data: mods,
                            placeholder: "请选择模块",
                            language: "zh-CN"
                        }).select2("val", stragety_view.cc_module||"0");
                    }
                }
            });
        });

		//监控对象中模块下拉框
		$('#main-content #monitorModule').select2({
            placeholder: '请选择集群...',
			data: [],
		});

        $("#main-content #plat_id").select2({});

        $("#main-content [name=responsible]").select2({});
        $("#main-content [name=phone_receiver]").select2({});

		//检测算法中下拉框
		$('#main-content #tAlgorithmSelect').select2({
			placeholder: '大于'
		});

		//收敛规则中时间下拉框
		$('#main-content #ruleASelect, #ruleBSelect').select2({
			placeholder: '15分钟'
		});

		//流程列表下拉框
		$('#main-content #autoProcessFlowList').select2({
            placeholder: '加载中...',
			data: []
		});

		//通知时间段下拉框
		$('#main-content #startHour, #main-content #startMinute, #main-content #endHour, #main-content #endMinute').select2({
			placeholder: '00'
		});
	}

	//页面事件绑定
	function eventsBind(){
		//面板折叠/展开
		$('#main-content [data-type="slideItem"]').on('click', function(){
			var $this = $(this);
            if (!stragety_view.solution_is_enable &&
                $this.closest("section").attr("id") == "auto_process" &&
                $this.closest("section").find(".icon-jiantou1").hasClass("expanded")
            ){return}
			$this.parents('section').find('.config__panelContent').css('width', '100%').slideToggle();
			$this.find('i').toggleClass('expanded');
		});

        $("#main-content #updateTaskList").on("click", function(){
            refresh_task_list();
        });
		////触发条件中监控对象、检测算法、收敛规则radio切换
		//$('[name="monitor-object"], [name="test-algorithm"], [name="convergence"]').on('ifChecked', function(){
		//	var $this = $(this),
		//		target = $this.attr('data-target');
        //
		//	$('[data-id="'+target+'"]').removeClass('hidden').siblings().addClass('hidden');
		//});

		//自动处理title上的状态开关事件
		$('#main-content #auto_process_btn').on('change', function(){
			var $this = $(this),
				status = $this.children('input').prop('checked');

			if(status){	//on

			}
			else{	//off

			}
		});

		//通知方式checkbox选择
		$('#main-content [data-id="phone_receiver"]').on('ifChanged', function(){
			$('#main-content [name=phone_receiver]').toggleClass('hidden');
		});

		//通知角色checkbox选择
		$('#main-content [data-id="responsible"]').on('ifChanged', function(){
			$('#main-content [name=responsible]').toggleClass('hidden');
		});

        $("[name=converge_id]")

	}

	initPlugins();
	eventsBind();
    $('.data-tip').popover();
});
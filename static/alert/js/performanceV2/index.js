(function(){

	//开始采集按钮
	//$('#collection').on('click', function(){
	//	$('#tips').addClass('hidden');
	//});

	//初始化条件过滤输入框宽度
	var initConditions = function(){
		var windowWidth = $(window).width();
		var width = $('#panelContent').width();
		var items = $('[data-type="condition-row"] > .condition-item'),
			length = items.length;

		if(windowWidth > 1280 && windowWidth < 1544){
			items.each(function(i){
				if(i != length - 1){
					$(this).width((width - 215) / 3 - 49);
				}

				if(i >= 3){
					$(this).addClass('hidden');
				}
			});
			$('#filterMore').removeAttr('expanded').children('span').text('更多').siblings('i').removeClass('expanded');
		}
		else if(windowWidth >= 1544){			
			items.each(function(i){
				if(i != length - 1){
					$(this).width((width - 215) / 4 - 49);
				}

				if(i < 4){
					$(this).removeClass('hidden');
				}
			});
		}
		else{
			items.each(function(i){
				if(i != length - 1){
					$(this).width(215);
				}

				if(i >= 3){
					$(this).addClass('hidden');
				}
			});
		}
	};

	initConditions();

	$(window).resize(function(){
		initConditions();
	});

	//给条件过滤中更多按钮绑定事件
	$('#filterMore').on('click', function(){
		var $this = $(this),
			expanded = $this.attr('expanded');

		if(!expanded){
			$('[data-type="condition-row"] > .condition-item').removeClass('hidden');
			$this.attr('expanded', 'expanded').children('span').text('收起').siblings('i').addClass('expanded');
		}
		else{
			if($(window).width() < 1656){
				$('[data-type="condition-row"] > .condition-item').each(function(i){
					if(i > 2){
						$(this).addClass('hidden');
					}
				});
			}			
			$this.removeAttr('expanded').children('span').text('更多').siblings('i').removeClass('expanded');
		}
	});
    

	//按属性分组展示下表格的展开和收起
	$(document).on('click', '[data-type="group"]', function(){
		var $this = $(this);

		if($this.attr('data-status') == 'expanded'){	//若已展开
			var _this = $this,
				next = null;
			while(_this.next().length != 0 && _this.next().attr('data-group') == 'tr'){
				next = _this.next();
				next.addClass('hidden');
				_this = next;
			}
			$this.attr('data-status', 'closed').find('[data-type="group-mark"]').text('+');
		}
		else{						//若已收起
			var _this = $this,
				next = null;
			while(_this.next().length != 0 && _this.next().attr('data-group') == 'tr'){
				next = _this.next();
				next.removeClass('hidden');
				_this = next;
			}
			$this.attr('data-status', 'expanded').find('[data-type="group-mark"]').text('-');	
		}
	});

	//初始化checkbox
	//$('input[name="item"]').iCheck({
	//	checkboxClass: 'icheckbox_minimal-blue'
	//});
    //
	////点击全选
	//$('#select_all').on('ifChecked', function(){
	//	$('#panelBody').find('input[name="item"]').each(function(){
	//		$(this).iCheck('check');
	//	});
	//}).on('ifUnchecked', function(){
	//	$('#panelBody').find('input[name="item"]').each(function(){
	//		$(this).iCheck('uncheck');
	//	});
	//});

	//表格中checkbox选择
	$('#panelBody').on('ifChanged', 'input[name="item"]', function(){
		var $this = $(this),
			wrapper = $('#panelBody'),
			inputs = wrapper.find('input[name="item"]'),
			count = 0;

		inputs.each(function(){
			if($(this).prop('checked')){
				count++;
			}
		});
		
		if(count > 0){
			$('#batchCheck').removeAttr('disabled');
			$('#batchAdd').removeAttr('disabled');
            $('#batchAccess').removeAttr('disabled');

		}
		else{
			$('#batchCheck').attr('disabled', 'disabled');
			$('#batchAdd').attr('disabled', 'disabled');
            $('#batchAccess').attr('disabled', 'disabled');
		}
	});

	//初始化“批量查看”和“批量增加策略”按钮的提示框
	$('#batchCheck, #batchAdd, #batchAccess').on('mouseover', function(){
		var $this = $(this);

		if($this.attr('disabled')){
			$this.tooltip({
				title: '请先勾选主机/IP'
			});
			$this.tooltip('show');
		}
	}).on('mouseout', function(){
		$(this).tooltip('destroy');
	});

	//初始化置顶tips
	//$(document).on('mouseover', '[data-type="toTop"]', function(){
	//	var $this = $(this),
	//		isTop = $this.parents('tr').attr('data-type');
    //
	//	$this.tooltip({
	//		title: isTop ? '取消置顶' : '置顶'
	//	});
	//	$this.tooltip('show');
	//}).on('click', '[data-type="toTop"]', function(){		//绑定置顶功能
	//	var $this = $(this),
	//		$tr = $this.parents('tr'),
	//		$tbody = $this.parents('tbody'),
	//		$temp = null,
	//		oldCanvasArr = [];
    //
	//	$tr.find('[data-chart="pie"]').each(function(){		//保存canvas
	//		oldCanvasArr.push($(this).find('canvas')[0]);
	//	});
    //
	//	$this.tooltip('destroy');
	//	$tr.find('[name="item"]').iCheck('destroy');
    //
	//	setTimeout(function(){
	//		var isTop = $tr.attr('data-type'),
	//			newTop = null;
    //
	//		$temp = $tr.clone(true, true);
	//		if(!isTop){	//置顶
	//			var $cur = $tr,
	//				grouped = false,
	//				$target = null;
    //
	//			do{		//判断是否有分组
	//				$cur = $cur.prev();
	//				if($cur.attr('data-type') == 'group'){
	//					grouped = true;
	//					$target = $cur;
	//					break;
	//				}
	//			}while($cur.length != 0)
    //
	//			if(grouped){	//有分组
	//				$target.after($temp);
	//				$tr.remove();
    //
	//				newTop = $target.next();
	//			}
	//			else{		//无分组
	//				$tr.remove();
	//				$tbody.prepend($temp);
	//				newTop = $($tbody.find('tr')[0]);
	//			}
    //
	//			var chartError = newTop.find('[data-type="chart-error"]'),
	//				chartNormal = newTop.find('[data-type="chart-normal"]');
    //
	//			newTop.attr('data-type', 'isTop');
	//			chartError.find('canvas').remove();
	//			chartNormal.find('canvas').remove();
    //
	//			newTop.find('[data-chart="pie"]').each(function(i){
	//				var _this = $(this),
	//					newCanvas = document.createElement('canvas'),
	//					newContext = newCanvas.getContext('2d');
    //
	//				newCanvas.setAttribute('height', 32);
	//				newCanvas.setAttribute('width', 32);
	//				_this[0].appendChild(newCanvas);
	//				newContext.drawImage(oldCanvasArr[i], 0, 0);
	//			});
    //
	//			newTop.find('[data-type="toTop"]').addClass('toped');
	//		}
	//		else{	//取消置顶
	//			var isTop = $tbody.find('[data-type="isTop"]'),
	//				topLength = isTop.length;
    //
	//			if(topLength != 1){
	//				$tr.remove();
	//				var last = $tbody.find('[data-type="isTop"]').last();
	//				last.after($temp);
	//				newTop = last.next();
    //
	//				var chartError = newTop.find('[data-type="chart-error"]'),
	//					chartNormal = newTop.find('[data-type="chart-normal"]');
    //
	//				chartError.find('canvas').remove();
	//				chartNormal.find('canvas').remove();
    //
	//				newTop.find('[data-chart="pie"]').each(function(i){
	//					var _this = $(this),
	//						newCanvas = document.createElement('canvas'),
	//						newContext = newCanvas.getContext('2d');
    //
	//					newCanvas.setAttribute('height', 50);
	//					newCanvas.setAttribute('width', 50);
	//					_this[0].appendChild(newCanvas);
	//					newContext.drawImage(oldCanvasArr[i], 0, 0);
	//				});
    //
	//				newTop.removeAttr('data-type');
	//				newTop.find('[data-type="toTop"]').removeClass('toped');
	//			}
	//			else{			//取消最后一个置顶
	//				$tr.removeAttr('data-type');
	//				$tr.find('[data-type="toTop"]').removeClass('toped');
	//			}
	//		}
	//
	//		//恢复checkbox样式
	//		if(newTop){
	//			newTop.find('[name="item"]').iCheck({
	//				checkboxClass: 'icheckbox_minimal-blue'
	//			});
	//		}
	//		else{
	//			$tr.find('[name="item"]').iCheck({
	//				checkboxClass: 'icheckbox_minimal-blue'
	//			});
	//		}
	//	}, 150);
	//});
	
	//鼠标指向圆环进度条，显示详情
	//$('#panelBody').on('mouseenter', '[data-row="cpu"] span', function(){
	//	var $this = $(this),
	//		subHtml = '',
	//		html = '';
    //
	//	for(var i = 0; i < 24; i++){
	//		var random = Math.random() * 100,
	//			type = '';
	//		if(random < 50){
	//			type = 'success';
	//		}
	//		else if(random < 80){
	//			type = 'warning';
	//		}
	//		else if(random <= 100){
	//			type = 'error';
	//		}
    //
	//		subHtml += '<div class="clearfix">'+
	//						'<span class="title pull-left">'+(i+1)+'</span>'+
	//						'<div class="king-progress-box clearfix pull-left">'+
	//						    '<div class="progress king-progress">'+
	//						        '<div class="progress-bar '+type+'" role="progressbar" style="width: '+random+'%;"></div>'+
	//						    '</div>'+
	//						'</div>'+
	//					'</div>'
	//	}
    //
	//	html = '<div class="cpu-detail">'+
	//				'<p>单核CPU使用率</p>'+
	//					subHtml+
	//				'<div class="ruler clearfix">'+
	//					'<canvas data-type="indicator"></canvas>'+
	//					'<div class="pull-left indicator percentage0">'+
	//						'0'+
	//					'</div>'+
	//					'<div class="pull-left indicator percentage25">'+
	//						'25'+
	//					'</div>'+
	//					'<div class="pull-left indicator percentage50">'+
	//						'50'+
	//					'</div>'+
	//					'<div class="pull-left indicator percentage75">'+
	//						'75'+
	//					'</div>'+
	//					'<div class="pull-left indicator percentage100">'+
	//						'100'+
	//					'</div>'+
	//				'</div>'+
	//			'</div>';
    //
	//	$this.tooltip({
	//		html: true,
	//		title: html,
	//		placement: 'right'
	//	});
	//	$this.tooltip('show');
	//	getComputedStyle(document.querySelector('#panelBody')).display;
	//	var c = $this.next().find('canvas')[0],
	//		context = c.getContext('2d');
	//	context.fillStyle = '#fff';
	//	context.strokeStyle = '#fff';
	//	context.lineWidth = 2;
	//	context.beginPath();
	//	context.moveTo(0, 10);
	//	context.lineTo(300, 10);
	//	context.moveTo(0, 10);
	//	context.lineTo(0, 60);
	//	context.moveTo(75, 10);
	//	context.lineTo(75, 60);
	//	context.moveTo(150, 10);
	//	context.lineTo(150, 60);
	//	context.moveTo(225, 10);
	//	context.lineTo(225, 60);
	//	context.moveTo(300, 10);
	//	context.lineTo(300, 60);
	//	context.stroke();
	//});

	//指向/点击可排序的列
	//$(document).on('mouseover', '[data-type="condition"]', function(){
	//	var $this = $(this);
    //
	//	$this.find('i').css('color', '#666').removeClass('visibility-hidden');
	//	$this.siblings().find('i').removeClass('visibility-hidden');
	//}).on('mouseout', '[data-type="condition"]', function(){	//鼠标移开时
	//	var $this = $(this);
    //
	//	if(!$this.attr('data-value')){		//若未排序，恢复样式
	//		$this.find('i').css('color', '#bbb').addClass('visibility-hidden');
	//	}
	//	$this.siblings().not('[data-value]').find('i').addClass('visibility-hidden');
	//}).on('click', '[data-type="condition"]', function(){
	//	var $this = $(this),
	//		value = $this.attr('data-value');
    //
	//	if(value){	//若已排序
    //
	//		if(value == 'desc'){	//已降序
	//			$this.attr('data-value', 'asc');
	//			$this.find('i').removeClass('desc').addClass('asc');
	//			$this.find('i').css('color', '#666');
	//		}
	//		else{		//已升序
	//			$this.removeAttr('data-value');
	//			$this.find('i').removeClass('ordered').removeClass('desc').removeClass('asc');
	//			$this.siblings().find('i').removeClass('ordered').removeClass('desc').removeClass('asc');
	//			$this.find('i').css('color', '#bbb');
	//		}
	//	}
	//	else{		//若未排序
	//		$this.find('i').addClass('ordered').addClass('desc');
	//		$this.siblings().find('i').removeClass('ordered').removeClass('desc').removeClass('asc');
	//		$this.attr('data-value', 'desc').siblings().removeAttr('data-value');
	//		$this.find('i').css('color', '#666');
	//		$this.siblings().find('i').css('color', '#bbb');
	//	}
	//});

	////初始化告警状态tips
	//$('[data-type="alert-tip"]').on('mouseover', function(){
	//	var $this = $(this);
	//
	//	//可以在这里拉取处理条数的信息
    //
	//	$this.tooltip({
	//		title: '<p style="margin-top:10px;">未处理：1</p><p>处理中：5</p><p>已处理：5</p>',
	//		html: true,
	//		container: 'body'
	//	});
	//	$this.tooltip('show');
	//});

	////初始化表格中的进度条
	//$('[data-type="chart-error"]').easyPieChart({
	//	barColor: '#ff6666',
	//	scaleColor: false,
	//	size: 32,
	//	animate: 1000
	//});
	//$('[data-type="chart-normal"]').easyPieChart({
	//	barColor: '#46c37b',
	//	scaleColor: false,
	//	size: 32,
	//	animate: 1000
	//});

	//翻页回调函数
	//$('[data-type="paging"]').on('click', 'li', function(){
	//	//请求数据部分...
    //
	//	$('input[name="item"]').iCheck('uncheck');
	//});


	//侧栏日期选择
    //$('#monitorDate, #multipleDate').kendoDatePicker({
     //   value : new Date(),
     //   format : "yyyy-MM-dd"
    //});

    //显示侧栏共用函数
    //var displaySideContent = function(type){
    //	var sideContent = $('#sideContent');
    //
		//sideContent.removeClass('hidden');
		//getComputedStyle(document.getElementById('panelBody')).display;
		//sideContent.find('#close').addClass('open');
		//sideContent.find('.side-content').addClass('open');
    //	if(type == 'single'){
    //		sideContent.find('#single').removeClass('hidden').siblings('#multiple').addClass('hidden');
    //	}
    //	else if(type == 'multiple'){
    //		sideContent.find('#single').addClass('hidden').siblings('#multiple').removeClass('hidden');
    //	}
    //
    //	$('article.content').css('overflow', 'hidden');
    //	$('body').css('overflow', 'hidden');
    //}

    //引入echarts


    //初始化查看单个主机/IP详情
    //var initSingle = function(){
    //	var cpuChart, memChart, ioChart, inodesChart;
    //	//初始化监控选择
    //	$('#monitorSelector').children('span').on('click', function(){
    //		var $this = $(this);
    //
    //		//更新监控服务视图数据
    //
    //		$this.addClass('selected').siblings().removeClass('selected');
    //	});
    //
    //	//初始化图表
    //
    //
		////初始化侧栏中的checkbox
		//$('input[name="status"]').on('switch-change', function(e, data){
		//
		//});
    //$('input[name=status]').wrap('<div class="switch switch-mini mr10" data-on="success" data-on-label="ON" data-off-label="OFF">').parent().bootstrapSwitch();
    //}

    //初始化批量查看主机/IP详情


	//点击表格行弹出侧边栏
	//$('#panelBody').on('click', 'tr.list-row', function(event){
	//	if(!$(event.target).parents('[data-type="toTop"]').length){	//点击的不是置顶按钮才弹出侧边栏
	//		displaySideContent('single');
	//		initSingle();
	//	}
	//});

	//点击批量查看弹出侧边栏
	//$('#batchCheck').on('click', function(){
	//	if(!$(this).attr('disabled')){
	//		displaySideContent('multiple');
    //
	//	}
	//});

	//关闭侧边栏
	$('#close, #sideContent').on('click', function(event){
		if($(event.target).attr('data-type') == 'close'){
			var sideContent = $('#sideContent');
			sideContent.find('.side-content').removeClass('open').children('#single').addClass('hidden').siblings('#multiple').addClass('hidden');
			sideContent.find('#close').removeClass('open');
            $(".title-badge").removeClass("active")
			setTimeout(function(){
				sideContent.addClass('hidden');
    			$('article.content').css('overflow', 'auto');	
    			$('body').css('overflow', 'auto');				
			}, 100);
		}		
	});

    // 过滤section 展开/关闭
    $("section.filter").find(".panel-heading").click(function(){
        $("section.filter").find("i.icon-jiantou1").toggleClass("expanded");
        $("section.filter").find(".panel-body").slideToggle();
        initConditions()
    });

	//批量查看时指标选择
	//$('#selectors').on('click', 'a', function(){
	//	var $this = $(this),
	//		$options = $('#selectors').find('a'),
	//		value = $this.attr('value');
    //
	//	$options.each(function(){
	//		var _this = $(this);
    //
	//		if(value != _this.attr('value')){
	//			_this.removeClass('king-primary');
	//		}
	//		else{
	//			_this.addClass('king-primary');
	//		}
	//	});
	//});
})();

$(function(){ 
	/* #57378495 进程列表 */
	
	$('#chart1_demo').highcharts({
	    title: {
	        text: '',
	        x: -20 //center
	    },
	    subtitle: {
	        text: '源自heightchart',
	        x: -20
	    },
	    xAxis: {
	        categories: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
	    },
	    series: [{
	        name: '蒸发量',
	        type: 'line',
	        data: [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
	    },
	    {
	        name: '降水量',
	        type: 'line',
	        data: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
	    }]
	});
	
	
	
	

	$("#open_chart1").click(function(){ 
	  $("#chart_demo").children('div').each(function(){ 
	    if (!$(this).hasClass('king-display-none')) {
	    	$(this).addClass('king-display-none'); 
	    }
	    $("#chart1_demo").removeClass('king-display-none');
	  });
	});
	$("#open_chart2").click(function(){ 
	  $("#chart_demo").children('div').each(function(){ 
	    if (!$(this).hasClass('king-display-none')) {
	    	$(this).addClass('king-display-none'); 
	    }
	    $("#chart2_demo").removeClass('king-display-none');
	  });

	  $('#chart2_demo').highcharts({
		    title: {
		        text: '',
		        x: -20 //center
		    },
		    subtitle: {
		        text: '源自heightchart',
		        x: -20
		    },
		    xAxis: {
		        categories: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
		    },
		    series: [{
		        name: '蒸发量',
		        type: 'line',
		        data: [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
		    },
		    {
		        name: '降水量',
		        type: 'line',
		        data: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
		    }]
		});
	});
	$("#open_chart3").click(function(){ 
	  $("#chart_demo").children('div').each(function(){ 
	    if (!$(this).hasClass('king-display-none')) {
	    	$(this).addClass('king-display-none'); 
	    }
	    $("#chart3_demo").removeClass('king-display-none');
	    
	  });
	  $('#chart3_demo').highcharts({
		    title: {
		        text: '',
		        x: -20 //center
		    },
		    subtitle: {
		        text: '源自heightchart',
		        x: -20
		    },
		    xAxis: {
		        categories: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
		    },
		    series: [{
		        name: '蒸发量',
		        type: 'line',
		        data: [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
		    },
		    {
		        name: '降水量',
		        type: 'line',
		        data: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
		    }]
		});
	});
	$("#open_chart4").click(function(){ 
	  $("#chart_demo").children('div').each(function(){ 
	    if (!$(this).hasClass('king-display-none')) {
	    	$(this).addClass('king-display-none'); 
	    }
	    $("#chart4_demo").removeClass('king-display-none');
	    
	  });
	  $('#chart4_demo').highcharts({
		    title: {
		        text: '',
		        x: -20 //center
		    },
		    subtitle: {
		        text: '源自heightchart',
		        x: -20
		    },
		    xAxis: {
		        categories: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
		    },
		    series: [{
		        name: '蒸发量',
		        type: 'line',
		        data: [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
		    },
		    {
		        name: '降水量',
		        type: 'line',
		        data: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
		    }]
		});
	});
	$("#open_chart5").click(function(){ 
	  $("#chart_demo").children('div').each(function(){ 
	    if (!$(this).hasClass('king-display-none')) {
	    	$(this).addClass('king-display-none'); 
	    }
	    $("#chart5_demo").removeClass('king-display-none');
	    
	  });
	  $('#chart5_demo').highcharts({
		    title: {
		        text: '',
		        x: -20 //center
		    },
		    subtitle: {
		        text: '源自heightchart',
		        x: -20
		    },
		    xAxis: {
		        categories: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
		    },
		    series: [{
		        name: '蒸发量',
		        type: 'line',
		        data: [2.0, 4.9, 7.0, 23.2, 25.6, 76.7, 135.6, 162.2, 32.6, 20.0, 6.4, 3.3]
		    },
		    {
		        name: '降水量',
		        type: 'line',
		        data: [2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3]
		    }]
		});
	});


    /*
    $("#plugin3_demo2 .select2_box").on('change',function(e){
    	if (e.val==0) {
    		self.location='index.html';
    	}
    	if (e.val==1) {
    		self.location='accessConfig.html';
    	}
    	if (e.val==2) {
    		self.location='accessConfig.html';
    	}
    });
	*/
    $(".sidebar-toggle").click(function(){ 
    	if (!$("#plugin3_demo2").hasClass('king-display-none')) {
    		$("#plugin3_demo2").addClass('king-display-none');
    	}
    	else{
    		$("#plugin3_demo2").removeClass('king-display-none');
    	} 
    });

    $('#tab1_demo1 .nav-tabs>li>a').on('mouseover',function(){
    	$(this).trigger('click');
    });

 	//时间日期选择
    $("#plugin16_demo1_3").kendoDateTimePicker({
        value:new Date()
    });


	$(".content-wrapper .box-body .king-monitor-middle>i").click(function(){
		if (!$(".king-monitor-left").hasClass("king-display-none")) {
			$(".king-monitor-left").addClass("king-display-none");
			$(".king-monitor-middle .fa-chevron-left").addClass("king-display-none");
			$(".king-monitor-middle .fa-chevron-right").removeClass("king-display-none"); 
		}else{
			$(".king-monitor-left").removeClass("king-display-none");
			$(".king-monitor-middle .fa-chevron-left").removeClass("king-display-none");
			$(".king-monitor-middle .fa-chevron-right").addClass("king-display-none"); 
		}
	});

	$(".exchange-view").click(function(){
		$(this).addClass("king-back-gray");
	});

    $(".main-sidebar > .sidebar .treeview > .treeview-menu > li").click(function(){
        $(this).parent().children('li').each(function(){
            $(this).removeClass("active");
        });
        $(this).addClass('active');
    });
});

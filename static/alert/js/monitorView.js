$(function() {
    Highcharts.setOptions({global: { useUTC: false } });
    //全局图表配置
    var config_timelabelformats = {
        //时间格式配置
        second: '%H:%M',
        minute: '%H:%M',
        hour: '%H:%M',
        day: '%m-%d',
        week: '%m-%d',
        month: '%y-%m',
        year: '%Y年'
    };
    var highchart_config_chip = {
        color_list: [],
        series_base: { //数据的基本配置
            name: '',
            data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        },
        series_interval_by_time: {
            name: '',
            data: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            pointStart: Date.UTC(2014, 0, 1),
            pointInterval: 60 * 5 * 1000,
        },
        yAxis_base: { //完全没有y轴
            title: {
                text: ""
            },
            gridLineWidth: 0, //默认是0，即在图上没有纵轴间隔线
            gridLineColor: '#eee',
            minorGridLineWidth: 0,
            minorGridLineColor: '#fff',
            minorTickWidth: 0,
            showFirstLabel: false,
            showLastLabel: false,
            lineWidth: 0,
            min: 0
        },
        yAxis_line: { //y轴有轴配置
            title: {
                text: ""
            },
            gridLineWidth: 1, //默认是0，即在图上没有纵轴间隔线
            gridLineColor: '#EEE',
            minorGridLineWidth: 10,
            minorGridLineColor: '#eee',
            minorTickWidth: 0,
            showFirstLabel: true,
            showLastLabel: true,
            lineWidth: 0,
            labels: {
                overflow: 'justify',
                distance: 0,
                enable: true,
                style: {
                    color: '#A2B3C3',
                    width: "80px"
                },
                formatter: function() {
                    var v = this.value
                    if (v > 1000000) {
                        return (this.value / 1000000) + "m"
                    } else if (v > 10000) {
                        return (this.value / 10000) + "w"
                    } else if (v > 1000) {
                        return (this.value / 1000) + "k"
                    }
                    return this.value
                }
            },
            min: 0
        },
        legend_float: { //浮动图示的配置
            enabled: true,
            align: 'left',
            verticalAlign: 'top',
            floating: true,
            y: 0,
            x: 0,
            borderWidth: 1,
            backgroundColor: '#fff',
            borderColor: '#eee'
        },
        legend_float_bottom: { //浮动图示的配置
            enabled: true,
            align: 'right',
            verticalAlign: 'bottom',
            floating: true,
            width: 200,
            y: 0,
            x: 0,
            borderWidth: 1,
            backgroundColor: null,
            borderColor: null,
            itemStyle: {
                color: "#fff"
            },
            itemHoverStyle: {
                color: "#fff"
            }
        },
        legend_bottom: { //普通的legend
            align: 'center',
            floating: false,
            verticalAlign: 'bottom',
            backgroundColor: null,
            borderColor: null,
            itemStyle: {
                color: "#A2B3C3"
            },
            itemHoverStyle: {
                color: "#fff"
            },
            borderWidth: 1,
            shadow: false
        },
        legend_top: {
            align: 'right',
            floating: true,
            verticalAlign: 'top',
            backgroundColor: null,
            borderColor: null,
            itemStyle: {
                color: "#A2B3C3"
            },
            itemHoverStyle: {
                color: "#fff"
            },
            borderWidth: 1,
            shadow: false
        },
        xAxis_datetime_interval_day: { //按天间隔模式
            type: 'datetime',
            dateTimeLabelFormats: {
                day: config_timelabelformats.day
            }
        },
        xAxis_datetime_interval_hour: { //按小时间隔模式
            type: 'datetime',
            maxPadding: 0.05,
            minPadding: 0.05,
            tickPixelInterval: 160,
            dateTimeLabelFormats: {
                hour: config_timelabelformats.hour
            }
        },
        xAxis_datetime_full: { //非间隔模式
            enable: true,
            type: 'datetime',
            maxPadding: 0.05,
            minPadding: 0.05,
            endOnTick: true,
            startOnTick: true,
            min: null,
            max: null,
            showFirstLabel: false,
            showLastLabel: false,
            tickPixelInterval: 60,
            tickLength: 4,
            tickPosition: 'inside',
            tickColor: '#EEE',
            lineWidth: 1,
            lineColor: '#EEE',
            minorTickWidth: 0,
            minorGridLineWidth: 0,
            minorGridLineColor: '#EEE',
            gridLineWidth: 1, //默认是0，即在图上没有纵轴间隔线
            gridLineColor: '#EEE',
            dateTimeLabelFormats: config_timelabelformats,
            labels: {
                color: '#4B6986',
                fontWeight: 'bold',
                overflow: 'justify'
            }
        },
        plot_option: {
            spline: {
                lineWidth: 1,
                shadow: false,
                marker: {
                    enabled: true,
                    lineWidth: 0,
                    radius: 0
                }
            },
            line: {
                animation: false,
                lineWidth: 1,
                shadow: false,
                marker: {
                    enabled: false
                },
                connectNulls: false
            },
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: false
                },
                showInLegend: true
            },
            area: {
                marker: {
                    enabled: false
                },
                lineWidth: 1,
                shadow: false
            },
            scatter: {
                enableMouseTracking: true,
                showInLegend: false,
                marker: {
                    radius: 5,
                    states: {
                        hover: {
                            enabled: false,
                            lineColor: 'rgb(100,100,100)'
                        }
                    },
                    symbol: "circle",
                },
                states: {
                    hover: {
                        marker: {
                            enabled: false
                        }
                    }
                },
                tooltip: {
                    headerFormat: '<b>{series.name}</b><br>',
                    pointFormat: '{point.x}: {point.y}'
                },

            }
        }
    };

    var Page = {};
    //线性图配置
    var line_chart_config = {
        colors: highchart_config_chip.color_list,
        chart: {
            type: 'line',
            backgroundColor: null,
            borderWidth: 0,
            borderColor: 'red',
            borderRadius: 0,
            plotBorderColor: 'red',
            plotBorderWidth: 0,
            animation: false,
            zoomType: 'x',
            resetZoomButton: {
                position: {
                    align: 'right', // by default
                    verticalAlign: 'bottom', // by default
                    y: -40,
                }
            },
            events: {
                selection: null
            }
        },
        plotOptions: highchart_config_chip.plot_option,
        tooltip: {
            useHTML: true,
            crosshairs: [{
                width: 1,
                color: "#EEE"
            }],
            shared: true,
            valueSuffix: "",
            pointFormat: '<span style="color:{series.color}">\u25CF</span> {series.name}: <b>{point.y}</b><br/>',
            xDateFormat: '%H:%M',
            formatter: function() {
                var currentTime=formatTime(this.x);
                var _current_point = currentTime ;
                var s = '<b>' + _current_point + '</b>';
                if (this.series && this.series.name == "告警") {
                    //查找符合条件的告警第一条,显示告警详情

                    var _alarm_list = global_value.alarm_dict[global_value.current_alarm_type]
                    for (var k in _alarm_list) {
                        var _alarm = _alarm_list[k]
                        var _alarm_time = _alarm.begin_time.substring(0, 17) + "00"
                        if (_alarm_time == _current_point) {
                            var desc = _alarm.raw.split(",")

                            s += "<br/><span class='red'>发现告警</span><br/>"
                            s += desc.join("<br/>")
                            break
                        }

                    }
                } else if (this.points) {
                    $.each(this.points, function() {

                        s += '<br/>' + this.series.name + ': ' +
                            this.y;
                    });
                }

                return s;
            },
        },
        title: {
            text: "",
            align: "right"
        },
        subtitle: {
            text: null
        },
        credits: {
            enabled: false
        },
        xAxis: highchart_config_chip.xAxis_datetime_full,
        yAxis: highchart_config_chip.yAxis_line,
        legend: highchart_config_chip.legend_top,
        series: [],
        loading: {
            style: {
                backgroundColor: '#000',
                opacity: 0.2
            }
        }
    };

    // 把时间戳转换格式
    function formatTime(timestamp){
        var nowDate=new Date(timestamp);
        var nTime=(nowDate.getHours()<10?"0"+nowDate.getHours():nowDate.getHours())+":"+(nowDate.getMinutes()<10?"0"+nowDate.getMinutes():nowDate.getMinutes());
        var nYear=nowDate.getFullYear();
        var nMonth=(nowDate.getMonth()+1)<10?"0"+(nowDate.getMonth()+1):nowDate.getMonth()+1;
        var nDate= (nowDate.getDate()+1)<10?"0"+nowDate.getDate():nowDate.getDate();
        return nYear+"-"+nMonth+"-"+nDate+" "+nTime;
    }

    //绘图，传入boxId（浸染的id）、url（接口）、params（参数）
    function makeChart(conf) {
        var begin_timestamp = new Date().getTime();
        $("#"+conf.boxId+"-time").toggle();
        $("#"+conf.boxId+"-load").toggle();
        $.getJSON(conf.url, conf.params,
           function(feedback) {
            var end_timestamp = new Date().getTime();
            $("#"+conf.boxId+"-time").html("[耗时:"+(end_timestamp-begin_timestamp)+"毫秒]");
            $("#"+conf.boxId+"-time").toggle();
            $("#"+conf.boxId+"-load").toggle();
            console.log($("#"+conf.boxId+"time"), "#"+conf.boxId+"time");
            if (feedback.result) {
                var _chart_config = clone_obj(line_chart_config)
                _chart_config.series = feedback.data.series
                _chart_config.legend = clone_obj(highchart_config_chip.legend_top)

                _chart_config.xAxis.plotLines = [];
                for (var i = 0; i < feedback.data.points.length; i ++){
                    // for (var j = 0; j < feedback.data.series[0].data.length; j ++){
                    //     if (feedback.data.series[0].data[j][0] > feedback.data.points[i].timestamp){
                    //         var value = j;
                    //         break
                    //     }
                    // }
                    _chart_config.xAxis.plotLines.push({
                        color: 'red',
                        width: 2,
                        value: feedback.data.points[i].timestamp,
                    })
                }
                console.log(_chart_config.xAxis.plotLines);
                _chart_config.chart.renderTo = conf.boxId;
                Page.alert_chart_obj = new Highcharts.Chart(_chart_config)
            } else {
                console.log(feedback);
                console.log($("#"+conf.boxId));
                $("#"+conf.boxId).html("加载数据异常，请联系开发者："+feedback.message);
            }
        });
    }

    //获取绘图参数
    function getParams(i, default_params){
        var dimensions = {};
        $(".dimension-"+i).each(function(index, value){
            if ($(this).val()){
                dimensions[$(this).attr("data")] = $(this).val();
            }
        })
        var params = {
            dimensions: JSON.stringify(dimensions),
            method: $("#sql-func-"+i).val(),
            date: $("#daterangepicker").val(),
        }
        for (key in default_params){
            params[key] = default_params[key];
        }
        var monitor_id = $("#chart"+i).attr("monitor-id");
        console.log(i, monitor_id, params);
        return params
    }

    $(".re-make-chart").on("click", function(){
        var i = Number($(this).attr("data"));
        console.log(i);
        makeChart({
            boxId: 'king-chart-'+i,
            url: CHART_DATA_URL[i-1],
            params: getParams(i, {}),
        });
    })

    var monitorView = {
        //入口 
        init: function() {
            this.sceneList();
            this.sortChartBox();
            this.drawMonitorView();
            this.initSortTime();
            this.initChartFilter();
            this.initLeft();
            this.setRightHeight();
            $('.layout-left .scene-section-box').mCustomScrollbar({
                theme: "minimal-dark"
            });
        },
        //画图，传入开始和结束时间
        drawMonitorView: function(params) {
            for (var i=1; i<=CHART_DATA_URL.length; i++){
                makeChart({
                    boxId: 'king-chart-'+i,
                    url: CHART_DATA_URL[i-1],
                    params: getParams(i, params),
                });
            }
        },
        //初始化表格过滤条件框
        initChartFilter: function() {
            $('.chart-filter-btn').on('click', function() {
                var chart = $(this).closest('.chart');
                if ($(this).hasClass('expand')) {
                    $(this).removeClass('expand')
                    chart.find('.chart-filter-box').hide();
                } else {
                    $(this).addClass('expand')
                    chart.find('.chart-filter-box').show();
                }
            });
        },
        //图表块拖拉排序
        sortChartBox: function() {
            $("#charts_box").sortable({
                items: ">div",
                handle: ".king-block-header",
                placeholder: "ui-state-highlight col-lg-6 col-md-12",
                update: function() {
                    var sortId = [];
                    var charts = $('#charts_box .chart');
                    charts.each(function() {
                        var chartId = $(this).attr('id');
                        var smonitorId = $(this).attr('s-monitor-id');
                        sortId.push(smonitorId);
                    });
                    console.log(sortId); //获取顺序
                    //发送ajax到接口保存
                    $.ajax({
                        url: site_url + "update_scenario_sort/",
                        dataType: "json",
                        method: "POST",
                        data: {
                            sm_ids: JSON.stringify(sortId),
                        },
                        success: function(result){
                            if (!result.result){
                                console.log(result.message);
                            }
                        }
                    })
                }
            });
            $("#charts_box").disableSelection();
        },
        //初始化时间拖拉选择器
        initSortTime: function() {
            //生成时间组件
            var container = $(".timeline")
            time_start = '00:00:00'
            time_end = '23:59:59'


            //时间变化事件
            $(".timeline").selectable({
                stop: function() {
                    var min = 24
                    var max = 0
                    $(".ui-selected", this).each(function() {
                        var _this = $(this)
                            //var _val  = _this.attr("value")
                        var _val = new Number(_this.attr("value"))
                        if (_val < min) {
                            min = _val
                        }
                        if (_val > max) {
                            max = _val
                        }
                    });
                    if (min < 10) {
                        min = "0" + min
                    }
                    if (max < 10) {
                        max = "0" + max
                    }
                    time_start = min + ":00:00"
                    time_end = max + ":59:59"
                        //重新画图
                    monitorView.drawMonitorView({
                        time_start: time_start,
                        time_end: time_end,
                    });
                }
            });

            // 选择单个日期
            $('#daterangepicker').daterangepicker({
                locale: {
                    format: 'YYYY-MM-DD'
                },
                autoApply: true,
                singleDatePicker: true,
                timePicker: false
            });
            $('#daterangepicker').on('apply.daterangepicker', function(ev, picker) {
                var date = $(this).val();
                //重新画图
                monitorView.drawMonitorView({
                    date: date,
                });
            });

            //全选时间
            $(".icon-time").bind("click", function() {
                if ($(".timeblock.ui-selected").length != 24) {
                    $(".timeblock").addClass('ui-selected')
                    time_start = "00:00:00"
                    time_end = "23:59:59"
                    console.log(time_start, time_end);
                    //重新画图
                    monitorView.drawMonitorView({
                        time_start: time_start,
                        time_end: time_end,
                    });
                }

            })
        },
        sceneList: function() {
            var leftBox = $('#layoutLeft');
            // 点击编辑按钮
            leftBox.on('click', '.fa-edit', function() {
                var $thisLi = $(this).closest('li');
                if ($thisLi.hasClass('editing')) {
                    return false;
                } else {
                    $('.scene-list').find('li.editing').find('.fa-close').trigger('click');
                    $thisLi.addClass('editing');
                }

            });
            // 点击确定
            leftBox.on('click', '.fa-check', function(event) {
                var $input = $(this).parent().siblings('input');
                var $a = $(this).parent().siblings('a');
                var $inputVal = $input.val();
                var $thisLi = $(this).closest('li');

                if ($inputVal == '') {
                    $input.focus().attr('title', '不能为空').trigger('mouseover');
                    var t = setTimeout(function() {
                        $input.trigger('mouseout').attr('title', '');
                        clearTimeout(t);
                    }, 1000)
                } else {
                    $input.attr('title', '');
                    $thisLi.removeClass('editing').removeClass('adding');
                    $a.text($inputVal);
                    $.ajax({
                        url: site_url+cc_biz_id+"/scenario/",
                        method: "POST",
                        data: {
                            scenario_id: $input.attr("data-id"),
                            name: $input.val(),
                        },
                        dataType: "json",
                        success: function(result){
                            if (!result.result){
                                app_alert("保存场景失败，请联系管理员:"+result.message, "fail")
                            }
                        }
                    })
                }
            });
            // 点击取消按钮
            leftBox.on('click', '.fa-close', function(event) {
                    var $input = $(this).parent().siblings('input');
                    var $a = $(this).parent().siblings('a');
                    var $aText = $a.text();
                    var $thisLi = $(this).closest('li');

                    if ($thisLi.hasClass('editing')) {
                        $input.val($aText);
                        $thisLi.removeClass('editing');
                    } else {
                        app_confirm("确认删除?", function(){
                            $('.scene-list').find('li.editing').find('.fa-close').trigger('click');
                            $thisLi.remove();
                            $.ajax({
                                url: site_url+"delete_scenario/",
                                method: "POST",
                                data: {
                                    scenario_id: $input.attr("data-id"),
                                },
                                dataType: "json",
                                success: function(result){
                                    if (!result.result){
                                        app_alert("删除场景失败，请联系管理员:"+result.message, "fail")
                                    }
                                }
                            })
                        });
                    }

                })
                // 点击增加场景
            leftBox.on('click', '.add-one', function(event) {

                var $h5 = $(this).closest('h5');
                var $ul = $h5.next('ul');
                leftBox.find('.editing').find('.fa-close').trigger('click');
                var $newLi = $('<li class="editing adding">' +
                    '<a class="text-over" href="javascript:;"></a>' +
                    '<input type="text" class="form-control" data-text="" data-placement="bottom" title="" value="">' +
                    '<span class="edit-icon">' +
                    '<i class="fa fa-edit ml5"></i> ' +
                    '<i class="fa fa-check ml5"></i> ' +
                    '<i class="fa fa-close ml5"></i> ' +
                    '</span>' +
                    '</li>');

                $newLi.prependTo($ul).find('input').focus();

            });
            leftBox.on('click', '.adding .fa-close', function(event) {
                $('.adding').remove();
            });
            // 点击其他区域取消操作
            $(document).on('click', function(event) {
                var sceneTarget = $(event.target).closest('.scene-section');
                if (!sceneTarget.length > 0) {
                    $('.scene-section').find('.editing').find('.fa-close').trigger('click');
                }
            });
        },
        initLeft: function() {
            var data = {
                dataList: [{
                    title: '默认视图',
                    url: 'javascript:include_open("dashboard", "");',
                    list: SCENARIO_LIST,
                }]
            };
            var html = template('leftTemp', data);
            //把生成的html字符串放到指定的容器里
            document.getElementById('content').innerHTML = html;
        },
        setRightHeight:function (){
            function setRightHeight(){
              var H=$(window).height();
              $('.charts-container').height(H-200);
            }
            setRightHeight();
            $(window).resize(function (){ setRightHeight() });
            $(".charts-container").mCustomScrollbar({
                theme: "minimal-dark"
            });
        }
    }

    monitorView.init();

});

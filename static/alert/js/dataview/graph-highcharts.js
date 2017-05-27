/**
 * Created by willgchen on 2015/10/27. for JA
 */

//Highcharts主题
Highcharts.theme_default = {
    lang:{
        resetZoom: "重置",
        resetZoomTitle: "重置缩放"
    },
	colors: ["#f6bb42","#4a89dc", "#3bafda", "#fc695e","#967adc","#64c256"],
	chart: {
		//backgroundColor: null,
		style: {
			fontFamily: "Arial, sans-serif, SimSun"
		}
	},
	title :{
		text:""
	},
	credits:{
		enabled:false
	},
	xAxis: {
		gridLineColor: '#ebebeb',
		gridLineWidth: 0,
		tickWidth: 0,
		lineColor: '#ebebeb'
	},
	yAxis: {
		floor: "",
        ceiling: "",
		gridLineColor: '#ebebeb',

	},
	tooltip: {
		borderWidth: 0,
		backgroundColor: 'rgba(0,0,0,0.7)',
		shadow: false,
		style: {
			color: '#ffffff'
		}
        //positioner: function(boxWidth, boxHeight, point) {
        //    return {
        //        x: point.plotX,
        //        y: point.plotY-100
        //    };
        //}
	},
	plotOptions: {
		line: {
			marker: {
				symbol: 'circle',
				radius: 2,
			}
		}
	},
    series:{
        cropThreshold: 1500
    }
};

var Hchart = {
    make_graph: function (chart_data, selector, monitor_id) {
        var func = $(this).attr(chart_data.chart_type);
        func(chart_data, selector, monitor_id);
        Hchart.after_graphed(chart_data, selector);
    },

    after_graphed: function(chart_data, selector){
        var chart_obj = $(selector).highcharts();
    },

    line: function(chart_data, selector, monitor_id){

		$(selector).highcharts(get_line_chart_opt(chart_data, monitor_id));
    },

    spline: function(chart_data, selector, monitor_id){
        Hchart.line(chart_data, selector, monitor_id);
    }

};
ready_info = {};
function get_line_chart_opt(chart_data, monitor_id){
    var defaultOptions = {
        colors: ['#27C24C', '#CAE1FF', '#CDCDB4', '#FE0000', '#C3017C'],
        title:{},
        chart: {
            type: chart_data.chart_type,
            zoomType: "x"
        },
        plotOptions: {
            spline: {
                marker: {
                    threshold: 0,
                    symbol: 'circle',
                    radius: 1,
                    enabled: true
                }
            },
            line: {
                marker: {
                    symbol: 'circle',
                    radius: 1
                }
            },
            series : {

            }
        },
        credits:{
            enabled: true,
            text: "",
            href: "###"
        },
        xAxis: chart_data.x_axis,
        yAxis: [{
            title: {
                enabled: false
            },
            min: 0,
            gridLineDashStyle: "LongDash",
            allowDecimals: true,
            plotLines: [],
            opposite: false
            }],
        tooltip: {
            xDateFormat: '%Y-%m-%d %H:%M:%S',
            followPointer: true,
            followTouchMove: true,
            crosshairs:  {
                width: 1,
                color: "#e2e2e2"
            },
            shared: true,
            useHTML: true,
            headerFormat: '<small>{point.key}</small><table>',
            pointFormatter: function(){
                var delay_info = "";
                if (this.series.zoneAxis){
                    var key = this.x / 1000;
                    if (this.series.userOptions.delay_info[key]){
                        delay_info = '<font color="#f3b760">(数据延时)</font>'
                    }
                }
                return '<tr><td style="color: '+this.series.color+'">'+this.series.name+': </td>' +
                    '<td style="color: #FFFFFF;"><b>'+this.y+delay_info+'</b></td></tr>';
            },
            footerFormat: '</table>'
            //valueDecimals: 2
        },
            series: chart_data.series
    };

    //实时图
    defaultOptions.plotOptions.pointInterval = chart_data.pointInterval;
    defaultOptions.plotOptions.pointStart = chart_data.pointStart;
    if (chart_data.pointInterval == 3600000){
        defaultOptions.xAxis.labels = {
                    formatter: function() {
                        return Highcharts.dateFormat('%m/%d', this.value);
                    }
                }
    }
    defaultOptions.rangeSelector = {
        buttons: [{
            count: 1,
            type: 'minute',
            text: '1M'
        }, {
            count: 5,
            type: 'minute',
            text: '5M'
        }, {
            type: 'all',
            text: 'All'
        }],
        inputEnabled: false,
        selected: 0
    };
    if (chart_data.plot_line_range){
        var line_range = chart_data.plot_line_range.split("-");
        var min = line_range[0] == ""?0:parseInt(line_range[0]);
        var max = line_range[1] == ""?0:parseInt(line_range[1]);
        if (!max){
            defaultOptions.yAxis[0].max = min + min /10 > chart_data.max_y?min + min /10 : chart_data.max_y;
            defaultOptions.yAxis[0].plotLines = [{
                    value: min,
                    color: 'red',
                    dashStyle: 'shortdash',
                    width: 2,
                    label: {
                        text: min
                    }
                }];
        }else{
            defaultOptions.yAxis[0].max = max + max /10 > chart_data.max_y?max + max /10 : chart_data.max_y;
            defaultOptions.yAxis[0].plotLines = [{
                    value: min,
                    color: 'green',
                    dashStyle: 'shortdash',
                    width: 2,
                    label: {
                        text: min
                    }
                }, {
                    value: max,
                    color: 'red',
                    dashStyle: 'shortdash',
                    width: 2,
                    label: {
                        text: max
                    }
                }];
        }
    }
    if (chart_data.yaxis_range) {
        //设置y轴数值范围
        var yaxis_range = chart_data.yaxis_range.split(":");
        var floor = isNaN(parseInt(yaxis_range[0]))?"":parseInt(yaxis_range[0]);
        var ceiling = isNaN(parseInt(yaxis_range[1]))?"":parseInt(yaxis_range[1]);
        if (floor){
            defaultOptions.yAxis[0].min = floor;
        }
        if (ceiling){
            defaultOptions.yAxis[0].max = ceiling;
        }

    }
    if (chart_data.unit){
        defaultOptions.yAxis[0].labels = {
             format: '{value}'+chart_data.unit
         };
        defaultOptions.tooltip.pointFormatter = function(){
            var delay_info = "";
            if (this.series.zoneAxis){
                var key = this.x / 1000;
                if (this.series.userOptions.delay_info[key]){
                    delay_info = '<font color="#f3b760">(数据延时)</font>'
                }
            }
            return '<tr><td style="color: '+this.series.color+'">'+this.series.name+': </td>' +
                '<td style="color: #FFFFFF;"><b>'+this.y+chart_data.unit+delay_info+'</b></td></tr>';
        };
    }
    if (!chart_data.show_label){
        defaultOptions.labels ={
            enabled: false
        }
    }
    if (monitor_id){
        ready_info[monitor_id] = false;
        defaultOptions.plotOptions.spline.animation = {
            complete: function () {
                ready_info[monitor_id] = true;
            }
        }
    }
    return defaultOptions
}
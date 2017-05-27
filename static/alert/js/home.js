$(function() {
    var homePage = {
        init: function() {
            var that=this;
            $('.toggle-icon').click(function (){
                $('#wrapper').toggleClass('toLeft');
            })
            $('.sidebar-toggle').click(function(event) {
                var timer=setInterval(function (){
                    $('[id^=home_chart]').each(function(index, el) {
                        $(this).highcharts().reflow();
                    });
                },10);
                setTimeout(function (){
                    clearInterval(timer);
                },400);
            });
            // 在线分析的圆环图
            $('.chart-progress').easyPieChart({
                onStep: function(from, to, percent) {
                    $(this.el).find('.king-easy-pie-chart-percent').text(Math.round(percent));
                },
                scaleColor: false,
                trackColor: $(this).attr("data-bar-color"),
                animate: 2000,
                lineWidth: 5,
                size: 60
            });
            // 图表1
            this.chart1();
            this.chart2();
        },
        chart1: function() {
            solidgauge('#home_chart1', gaugeData);
        },
        chart2: function() {
            areaChart("#home_chart2", areaData);
        },
    }
    homePage.init();
})

Highcharts.setOptions({global: { useUTC: false } });
function solidgauge(selector, json) {
    var gaugeOptions = {

        chart: $.extend({},
            json.chart
        ),
        title: null,
        pane: {
            center: ['50%', '77%'],
            size: '150%',
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || '#EEE',
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
            }
        },

        tooltip: {
            enabled: false
        },

        // the value axis
        yAxis: {
            stops: $.extend([
                [0.1, '#DF5353'], // green
                [0.8, '#fbb04b'], // yellow
                [0.9, '#78DCDA'] // red
            ], json.stops || false),
            lineWidth: json.stops || 0,
            minorTickInterval: json.minorTickInterval || null,
            tickPixelInterval: json.tickPixelInterval || 400,
            tickWidth: 0,
            title: {
                y: -70
            },
            labels: {
                y: 16
            }
        },
        credits: {
            enabled: false
        },
        plotOptions: {
            solidgauge: {
                dataLabels: {
                    y: 5,
                    borderWidth: 0,
                    useHTML: true
                }
            }
        }
    };
    // The speed gauge
    $(selector).highcharts(Highcharts.merge(gaugeOptions, {
        yAxis: {
            min: json.min,
            max: json.max,
            title: {
                text: json.title
            }
        },
        credits: {
            enabled: false
        },
        series: [
            $.extend({
                    dataLabels: {
                        format: '<div style="text-align:center"><span style="font-size:25px;color:' +
                            ((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black') + '">{y}</span><br/>' +
                            '</div>'
                    }
                },
                json["series"]

            )

        ]

    }));
}

function areaChart(selector, json) {
    $(selector).highcharts({
        chart: {
            zoomType: 'x'
        },
        title: {
            text: json.title
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: null
            }
        },
        legend: {
            enabled: false
        },
        plotOptions: {
            area: {
                fillColor: {
                    linearGradient: {
                        x1: 0,
                        y1: 0,
                        x2: 0,
                        y2: 1
                    },
                    stops: [
                        [0, Highcharts.getOptions().colors[0]],
                        [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                    ]
                },
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            }
        },

        credits: {
            enabled: false
        },
        series: [{
            name: json.name,
            type: 'area',
            pointInterval: 24 * 3600 * 1000,
            pointStart: Date.UTC(2006, 0, 1),
            data: json.dataArray
        }]
    });
}

function lineChart(selector,json) {
    $(selector).highcharts({
        chart: {
            type: 'line'
        },
        title: {
            text: json.title
        },

        xAxis: {
            type: 'datetime',
            plotLines: json.point || [],
        },

        yAxis: {
            title: {
                text: null
            }
        },

        tooltip: {
            crosshairs: true,
            shared: true,
        },

        legend: {
            enabled: false
        },
        credits: {
            enabled: false
        },

        series: [{
            name: json.name,
            data: json.dataArray,
            zIndex: 1,
            marker: {
                fillColor: 'white',
                lineWidth: 2,
                lineColor: Highcharts.getOptions().colors[0]
            }
        }]
    });
}

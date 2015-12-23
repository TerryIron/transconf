/**
 *
 * Created by terry on 15-12-17.
 */

angular.module('myApp', [
    'ngRoute',
    'myApp.stock'
]).config(['$routeProvider', function($routeProvider){
    $routeProvider.otherwise('/stock')
}]);

function GetHttpRequest()
{
    if ( window.XMLHttpRequest ) // Gecko
        return new XMLHttpRequest() ;
    else if ( window.ActiveXObject ) // IE
        return new ActiveXObject("MsXml2.XmlHttp") ;
}

function loadJS(sId, url){
    ajaxPage(sId, url);
}

function ajaxPage(sId, url){
    var oXmlHttp = GetHttpRequest() ;
    oXmlHttp.open('GET', url, false);//同步操作
    oXmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    oXmlHttp.send(null);
    includeJS(sId, oXmlHttp.responseText);
}

function includeJS(sId, source)
{
    if ( ( source != null ) && ( !document.getElementById( sId ) ) ){
        var oHead = document.getElementsByTagName('HEAD').item(0);
        var oScript = document.createElement( "script" );
        oScript.type = "text/javascript";
        oScript.id = sId;
        oScript.text = source;
        oHead.appendChild( oScript );
    }
}

function diffLines(a, b) {
    while (a.length > b.length) {
        a.pop();
    }
    b = b.slice(0, a.length - 1);
    return [a, b]
}

function buildKLineOptions(name, datelines, datalines)
{
    return {
        title: {
            text: name
        },
        tooltip: {
            trigger: 'axis',
            showDelay: 0,  // 显示延迟，添加显示延迟可以避免频繁切换，单位ms
            formatter: function (params) {
                var res = params[0].name;
                res += '<br/>' + params[0].seriesName;
                res += '<br/>  开盘 : ' + params[0].value[0] + '  最高 : ' + params[0].value[3];
                res += '<br/>  收盘 : ' + params[0].value[1] + '  最低 : ' + params[0].value[2];
                return res;
            }
        },
        legend: {
            data: []
        },
        toolbox: {
            show: true,
            feature: {
                mark: {show: true},
                dataZoom: {show: true},
                magicType: {show: true, type: ['line', 'bar']},
                restore: {show: true},
                saveAsImage: {show: true}
            }
        },
        dataZoom: {
            y: 250,
            show: true,
            realtime: true,
            start: 50,
            end: 100
        },
        grid: {
            x: 80,
            y: 40,
            x2: 20,
            y2: 25
        },
        xAxis: [
            {
                type: 'category',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data: datelines
            }
        ],
        yAxis: [
            {
                type: 'value',
                scale: true,
                boundaryGap: [0.05, 0.05],
                splitArea: {show : true}
            }
        ],
        series: [
            {
                name: name,
                type: 'k',// 开盘，收盘，最低，最高
                data: datalines
            }
        ]
    };
}

function pluginAverageOptions(datelines, datalines)
{
    return {
        tooltip : {
            trigger: 'axis',
            showDelay: 0   // 显示延迟，添加显示延迟可以避免频繁切换，单位ms
        },
        legend: {
            y : -30,
            data:[]
        },
        toolbox: {
            y : -30,
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : {
            show : true,
            realtime: true,
            start : 50,
            end : 100
        },
        grid: {
            x: 80,
            y:5,
            x2:20,
            y2:40
        },
        xAxis : [
            {
                type : 'category',
                position:'top',
                boundaryGap : true,
                axisLabel:{show:false},
                axisTick: {onGap:false},
                splitLine: {show:false},
                data : datelines
            }
        ],
        yAxis : [
            {
                type : 'value',
                scale:true,
                splitNumber: 3,
                boundaryGap: [0.05, 0.05],
                axisLabel: {
                    formatter: function (v) {
                        return Math.round(v/10000) + ' 万'
                    }
                },
                splitArea : {show : true}
            }
        ],
        series : [
            {
                name:'成交金额(万)',
                type:'line',
                symbol: 'none',
                data: datalines,
                markLine : {
                    symbol : 'none',
                    itemStyle : {
                        normal : {
                            color:'#1e90ff',
                            label : {
                                show:false
                            }
                        }
                    },
                    data : [
                        {type : 'average', name: '平均值'}
                    ]
                }
            }
        ]
    };
}

function pluginSizeOptions(datelines, datalines)
{
    return {
        tooltip : {
            trigger: 'axis',
            showDelay: 0   // 显示延迟，添加显示延迟可以避免频繁切换，单位ms
        },
        legend: {
            y : -30,
            data:[]
        },
        toolbox: {
            y : -30,
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : {
            y:200,
            show : true,
            realtime: true,
            start : 50,
            end : 100
        },
        grid: {
            x: 80,
            y:5,
            x2:20,
            y2:30
        },
        xAxis : [
            {
                type : 'category',
                position:'bottom',
                boundaryGap : true,
                axisTick: {onGap:false},
                splitLine: {show:false},
                data: datelines
            }
        ],
        yAxis : [
            {
                type : 'value',
                scale:true,
                splitNumber:3,
                boundaryGap: [0.05, 0.05],
                axisLabel: {
                    formatter: function (v) {
                        return Math.round(v/10000) + ' 万'
                    }
                },
                splitArea : {show : true}
            }
        ],
        series : [
            {
                name:'虚拟数据',
                type:'bar',
                symbol: 'none',
                data: datalines,
                markLine : {
                    symbol : 'none',
                    itemStyle : {
                        normal : {
                            color:'#1e90ff',
                            label : {
                                show:false
                            }
                        }
                    },
                    data : [
                        {type : 'average', name: '平均值'}
                    ]
                }
            }
        ]
    };
}

function parseStockCode() {
    var cd = code.concat();

    if (cd.substring(0, 1) == '0') {
        cd = cd + '.SZ'
    } else if (cd.substring(0, 1) == '6') {
        cd = cd + '.SS'
    }

    return cd
}

function parseDateFormat(y, m, d) {
    return y + '-' + m + '-' + d
}

function getStockCurData(code)
{
    var cd = parseStockCode(code);
    var json_url = 'http://query.yahooapis.com/v1/public/yql?q=' + 'select%20*%20from%20yahoo.finance.quotes' +
        '%20where%20symbol%20in%20(%22' + cd + '%22)&format=json&env=store://datatables.org/alltableswithkeys'
}

function getStockHistoryData(code, sy, sm, sd, ey, em, ed)
{
    var cd = parseStockCode(code);
    var sdate = parseDateFormat(sy, sm, sd);
    var edate = parseDateFormat(ey, em, ed);
    var json_url = 'http://query.yahooapis.com/v1/public/yql?q=' + 'select%20*%20from%20yahoo.finance.historicaldata' +
        '%20where%20symbol%20in%20(%22' + cd + '%22)%20' +
        'and%20startDate%3d%22' + sdate + '%22%20and%20endDate%20%3d%20%22' +
         edate + '%22&format=json&env=store://datatables.org/alltableswithkeys'

}
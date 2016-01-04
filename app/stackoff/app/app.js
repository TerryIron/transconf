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

function GetHttpRequest() {
    if ( window.XMLHttpRequest ) // Gecko
        return new XMLHttpRequest() ;
    else if ( window.ActiveXObject ) // IE
        return new ActiveXObject("MsXml2.XmlHttp") ;
}

function loadJS(sId, url) {
    ajaxPage(sId, url);
}

function ajaxPage(sId, url) {
    var oXmlHttp = GetHttpRequest() ;
    oXmlHttp.open('GET', url, false);//同步操作
    oXmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
    oXmlHttp.send(null);
    includeJS(sId, oXmlHttp.responseText);
}

function includeJS(sId, source) {
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

function buildKLineOptions(name, datelines, datalines) {
    return {
        title: {
            text: name
        },
        tooltip: {
            trigger: 'axis',
            showDelay: 0,  // 显示延迟，添加显示延迟可以避免频繁切换，单位ms
            formatter: function (params) {
                var res = params[0].name;
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

function pluginAverageOptions(datelines, datalines) {
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

function pluginVolumeOptions(datelines, datalines) {
    return {
        tooltip : {
            trigger: 'axis',
            showDelay: 0,   // 显示延迟，添加显示延迟可以避免频繁切换，单位ms
            formatter: function(params) {
                return '<br/>  量值 : ' + Math.round(params[0].value/10000) + '万';
            }
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
                name:'量值',
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

function CurrentTime() {
    var cur_date = new Date();
    return {
        'year': cur_date.getFullYear(),
        'month': cur_date.getMonth() + 1,
        'date': cur_date.getDate(),
        'hour': cur_date.getHours(),
        'minute': cur_date.getMinutes(),
        'second': cur_date.getSeconds()
    };
}

function parseStockCode(code) {
    code = String(code);
    var cd = code.concat();
    if (cd.substring(0, 1) == '0') {
        cd = cd + '.SZ';
    } else if (cd.substring(0, 1) == '6') {
        cd = cd + '.SS';
    }
    return cd
}

function parseDateFormat(y, m, d) {
    return y + '-' + m + '-' + d
}

function parseStockData(data){
    if (angular.isObject(data)) {
        return data['query']['results']['quote'];
    } else {
        var json_obj = JSON.parse(data);
        return json_obj['query']['results']['quote'];
    }
}

function StockStructure() {
    return {
        'name': [],
        'datelines': [],
        'cline': {},
        'kline': [],
        'volume': []
    }
}

function getStockCurDataURLfromSina(code) {
    var cd = code.concat();
    if (cd.substring(0, 1) == '0') {
        return 'http://hq.sinajs.cn/list=' + 'sz' + cd;
    } else if (cd.substring(0, 1) == '6') {
        return 'http://hq.sinajs.cn/list=' + 'sh' + cd;
    }
}

function getStockCurDataURLfromLocal(code) {
    var cd = code.concat();
    return '//v1/stackoff/get?code=' + cd
}

function getStockCurDataURL(code) {
    var cd = parseStockCode(code);
    return 'http://query.yahooapis.com/v1/public/yql?q=' + 'select%20*%20from%20yahoo.finance.quotes' +
        '%20where%20symbol%20in%20(%22' + cd + '%22)&format=json&env=store://datatables.org/alltableswithkeys';
}

function parseSinaData(data) {
    console.log(data);
}

function processStockCurDatafromLocal(data) {
    console.log(data);
}

function processStockCurDatafromSina(data) {
    var new_data = data.split('=')[1].split(',');
    var stock_data = StockStructure();
    stock_data['name'] = new_data[0];
    stock_data['cline']['open'] = new_data[1];
    stock_data['cline']['preclose'] = new_data[2];
    stock_data['cline']['current'] = new_data[3];
    stock_data['cline']['high'] = new_data[4];
    stock_data['cline']['low'] = new_data[5];
    stock_data['cline']['volume'] = new_data[8];

    return stock_data;
}

function processStockCurData(data) {
    var elements = parseStockData(data);
    var stock_data = StockStructure();
    stock_data['name'] = elements['Name'];
    stock_data['cline']['preclose'] = elements['PreviousClose'];
    stock_data['cline']['open'] = elements['Open'];
    stock_data['cline']['current'] = elements['Bid'];
    stock_data['cline']['average'] = elements['Ask'];
    stock_data['cline']['high'] = elements['DaysHigh'];
    stock_data['cline']['low'] = elements['DaysLow'];
    stock_data['cline']['changerange'] = elements['Change'];
    stock_data['cline']['changeperrange'] = elements['PercentChange'];
    stock_data['cline']['yearchangerange'] = elements['ChangeFromYearLow'];
    stock_data['cline']['yearchangeperrange'] = elements['PercentChangeFromYearLow'];
    stock_data['cline']['volume'] = elements['Volume'];
    return stock_data;
}

function getStockHistoryDataURL(code, sy, sm, sd, ey, em, ed) {
    var cd = parseStockCode(code);
    var sdate = parseDateFormat(sy, sm, sd);
    var edate = parseDateFormat(ey, em, ed);
    return 'http://query.yahooapis.com/v1/public/yql?q=' + 'select%20*%20from%20yahoo.finance.historicaldata' +
        '%20where%20symbol%20in%20(%22' + cd + '%22)%20' +
        'and%20startDate%3d%22' + sdate + '%22%20and%20endDate%20%3d%20%22' +
         edate + '%22&format=json&env=store://datatables.org/alltableswithkeys';
}

function processStockHistoryData(data){
    var elements = parseStockData(data);
    var stock_data = StockStructure();
    for (var i=0;i<elements.length;i++) {
        var j = elements.length - i -1;
        stock_data['datelines'].push(elements[j]['Date']);
        stock_data['kline'].push([elements[j]['Open'], elements[j]['Close'], elements[j]['Low'], elements[j]['High']]);
        stock_data['volume'].push(elements[j]['Volume'])
    }
    return stock_data;
}

'use strict';

angular.module('myApp.stock', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/stock', {
    templateUrl: 'stock/stock.html',
    controller: 'StockCtrl'
  });
}])

.controller('StockCtrl', ['$scope', function($scope) {// 路径配置

    loadJS('echarts', 'echarts.js');

    var cur_time = CurrentTime();
    $scope.code = '000001';
    $scope.name = null;

    require.config({
        paths: {
            echarts: 'http://echarts.baidu.com/build/dist'
        }
    });

    function DrawAll(code, cur_time) {
        function needMap() {
            var href = location.href;
                return href.indexOf('map') != -1
                || href.indexOf('mix3') != -1
                || href.indexOf('mix5') != -1
                || href.indexOf('dataRange') != -1;
        }
        // 使用
        require(
        [
            'echarts',
            'echarts/chart/line',
            'echarts/chart/bar',
            'echarts/chart/scatter',
            'echarts/chart/k',
            'echarts/chart/pie',
            'echarts/chart/radar',
            'echarts/chart/force',
            'echarts/chart/chord',
            'echarts/chart/gauge',
            'echarts/chart/funnel',
            'echarts/chart/eventRiver',
            'echarts/chart/venn',
            'echarts/chart/treemap',
            'echarts/chart/tree',
            'echarts/chart/wordCloud',
            'echarts/chart/heatmap',
            needMap() ? 'echarts/chart/map' : 'echarts'
        ],
        function (ec) {
            var current_url = getStockCurDataURL(code);
            var current_httpcli = GetHttpRequest();
            current_httpcli.onreadystatechange = function () {
                if (current_httpcli.readyState == 4 && current_httpcli.status == 200) {
                    var result = processStockCurData(current_httpcli.responseText);
                    $scope.name = result['name']
                }

            };
            current_httpcli.open('GET', current_url, true);
            current_httpcli.send(null);

            var history_url = getStockHistoryDataURL(code,
                                                     cur_time['year']-1,
                                                     cur_time['month'],
                                                     cur_time['date'],
                                                     cur_time['year'],
                                                     cur_time['month'],
                                                     cur_time['date']);
            var history_httpcli = GetHttpRequest();
            history_httpcli.onreadystatechange = function () {
                if (history_httpcli.readyState == 4 && history_httpcli.status == 200) {
                    var result = processStockHistoryData(history_httpcli.responseText);
                    var myChart_k = ec.init(document.getElementById('stock_k'));
                    var option_k = buildKLineOptions($scope.name, result['datelines'], result['kline']);
                    myChart_k.setOption(option_k);
                    var myChart_v = ec.init(document.getElementById('stock_v'));
                    var option_v = pluginVolumeOptions(result['datelines'], result['volume']);
                    myChart_v.setOption(option_v);
                }
            };
            history_httpcli.open('GET', history_url, true);
            history_httpcli.send(null);


        }
        );
    }

    $scope.Search = function(e) {
        var keycode = window.event?e.keyCode:e.which;
        if (keycode == 13) {
            $scope.code = $scope.search;
            DrawAll($scope.code, cur_time);
        }
    };

    DrawAll($scope.code, cur_time);
}]);
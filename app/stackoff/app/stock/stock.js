'use strict';

angular.module('myApp.stock', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/stock', {
    templateUrl: 'stock/stock.html',
    controller: 'StockCtrl'
  });
}])

.controller('StockCtrl', ['$scope', '$http', '$timeout', function($scope, $http, $timeout) {// 路径配置

    loadJS('echarts', 'echarts.js');

    var cur_time = CurrentTime();

    function reset_stock_info($scope) {
        $scope.code = '000001';
        $scope.name = null;
        $scope.current = null;
        $scope.high = null;
        $scope.low = null;
        $scope.volume = null;
        $scope.average = null;
        $scope.preclose = null;
        $scope.open = null;
        $scope.changerange = null;
        $scope.changeperrange = null;
    }

    reset_stock_info($scope);

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
            $timeout(function() {
                $http.get(current_url).success(function (data, status, headers, config) {
                    var result = processStockCurData(data);
                    $scope.name = result['name'];
                    $scope.current = result['cline']['current'];
                    $scope.high = result['cline']['high'];
                    $scope.low = result['cline']['low'];
                    $scope.volume = Math.round(result['cline']['volume']/ 1000) + '万';
                    $scope.average = result['cline']['average'];
                    $scope.preclose = result['cline']['preclose'];
                    $scope.open = result['cline']['open'];
                    $scope.changerange = result['cline']['changerange'];
                    $scope.changeperrange = result['cline']['changeperrange'];
                }, 3000);
            });

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
                    var title = $scope.name;
                    var option_k = buildKLineOptions(title, result['datelines'], result['kline']);
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
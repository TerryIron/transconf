'use strict';

angular.module('myApp.stock', ['ngRoute'])

.config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider) {
    $routeProvider.when('/stock', {
        templateUrl: 'stock/stock.html',
        controller: 'StockCtrl'
    });
}])

.controller('StockCtrl', ['$scope', '$http', function($scope, $http) {// 路径配置

    loadJS('echarts', 'echarts.js');

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
            //var current_url = getStockCurDataURL(code);
            var current_url = getStockCurDataURLfromSina(code);

            function updateStockInfo() {
                $http.jsonp(current_url + '?callback=parseSinaData').success(function (data) {
                    //var result = processStockCurData(data);
                    var result = processStockCurDatafromSina(data);
                    $scope.data.current = result['cline']['current'];
                    $scope.data.high = result['cline']['high'];
                    $scope.data.low = result['cline']['low'];
                    $scope.data.volume = Math.round(result['cline']['volume'] / 1000) + '万';
                    $scope.data.average = result['cline']['average'];
                    $scope.data.preclose = result['cline']['preclose'];
                    $scope.data.open = result['cline']['open'];
                    $scope.data.changerange = result['cline']['changerange'];
                    $scope.data.changeperrange = result['cline']['changeperrange'];
                    $scope.data.yearchangerange = result['cline']['yearchangerange'];
                    $scope.data.yearchangeperrange = result['cline']['yearchangeperrange'];
                    $scope.data.name = result['name'];
                    console.log($scope.data);
                });
            }
            updateStockInfo();
            $scope.stocktimer = setInterval(updateStockInfo, 4 * 1000);
            console.log('set timer:' + $scope.stocktimer);

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
                    var title = $scope.data.name;
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


    $scope.data = {};

    $scope.Search = function(e) {
        var keycode = window.event?e.keyCode:e.which;
        if (keycode == 13) {
            console.log('clear timer:' + $scope.stocktimer);
            clearInterval($scope.stocktimer);
            $scope.code = $scope.search;
            DrawAll($scope.code, CurrentTime());
        }
    };

    $scope.code = '000001';
    console.log('main drawall');
    DrawAll($scope.code, CurrentTime());
}]);
'use strict';

angular.module('myApp.stock', ['ngRoute'])

.config(['$routeProvider', '$httpProvider', function($routeProvider) {
    $routeProvider.when('/stock', {
        templateUrl: 'stock/stock.html',
        controller: 'StockCtrl'
    });
    loadJS('stock_lib', 'stock/stock_lib.js');
    loadJS('echarts', 'echarts.js');
}])

.controller('StockCtrl', ['$scope', '$http', function($scope, $http) {// 路径配置

    require.config({
        paths: {
            echarts: 'http://echarts.baidu.com/build/dist'
        }
    });

    function needMap() {
        var href = location.href;
            return href.indexOf('map') != -1
            || href.indexOf('mix3') != -1
            || href.indexOf('mix5') != -1
            || href.indexOf('dataRange') != -1;
    }

    $scope.display = {};
    $scope.data = {};
    $scope.code = {};
    $scope.code.items = ['000001', '601106', '002269', '600023'];

    $scope.DrawAll = function(code) {
        if ($scope.data[code] != null) {
            return;
        }
        $scope.display[code] = false;
        $scope.data[code] = {};
        console.log('call drawall:' + code);
        var cur_time = CurrentTime();
        var history_url = getStockHistoryDataURL(code,
                                                 cur_time['year']-1,
                                                 (cur_time['month']+9) % 12,
                                                 cur_time['date'],
                                                 cur_time['year'],
                                                 cur_time['month'],
                                                 cur_time['date']);
        var current_url = getStockCurDataURLfromLocal(code);
        var history_httpcli = GetHttpRequest();
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


            function updateStockInfo() {
                $http.get(current_url).success(function (data) {
                    var result = processStockCurDatafromLocal(data);
                    $scope.data[code].current = result['cline']['current'];
                    $scope.data[code].high = result['cline']['high'];
                    $scope.data[code].low = result['cline']['low'];
                    $scope.data[code].volumeper = result['cline']['volumeper'];
                    $scope.data[code].preclose = result['cline']['preclose'];
                    $scope.data[code].open = result['cline']['open'];
                    $scope.data[code].change = result['cline']['change'];
                    $scope.data[code].changeper = result['cline']['changeper'];
                    $scope.data[code].tradechange = result['cline']['tradechange'];
                    $scope.data[code].tradeper = result['cline']['tradeper'];
                    $scope.data[code].marketprice = result['cline']['marketprice'];
                    $scope.data[code].name = result['name'];
                    $scope.data[code].tradein1 = result['cline']['tradein_1'];
                    $scope.data[code].tradein2 = result['cline']['tradein_2'];
                    $scope.data[code].tradein3 = result['cline']['tradein_3'];
                    $scope.data[code].tradein4 = result['cline']['tradein_4'];
                    $scope.data[code].tradein5 = result['cline']['tradein_5'];
                    $scope.data[code].tradeout1 = result['cline']['tradeout_1'];
                    $scope.data[code].tradeout2 = result['cline']['tradeout_2'];
                    $scope.data[code].tradeout3 = result['cline']['tradeout_3'];
                    $scope.data[code].tradeout4 = result['cline']['tradeout_4'];
                    $scope.data[code].tradeout5 = result['cline']['tradeout_5'];
                    console.log($scope.data);

                    if (history_httpcli != null) {
                        history_httpcli.onreadystatechange = function () {
                            if (history_httpcli.readyState == 4 && history_httpcli.status == 200) {
                                var result = processStockHistoryData(history_httpcli.responseText);
                                var myChart_k = ec.init(document.getElementById('stock_k' + code));
                                var option_k = buildKLineOptions(result['datelines'], result['kline']);
                                myChart_k.setOption(option_k);
                                var myChart_v = ec.init(document.getElementById('stock_v' + code));
                                var option_v = pluginVolumeOptions(result['datelines'], result['volume']);
                                myChart_v.setOption(option_v);
                                history_httpcli = null;
                                document.getElementById(code).style.display = 'block';
                                //$scope.display[code] = true;
                                //$scope.$apply();
                            }
                        };
                        history_httpcli.open('GET', history_url, false);
                        history_httpcli.send(null);
                    }
                });

            }
            $scope.stocktimer = setInterval(updateStockInfo, 10 * 1000);
        }
        );
    };



    $scope.Search = function(e) {
        var keycode = window.event?e.keyCode:e.which;
        if (keycode == 13) {
            clearInterval($scope.stocktimer);
            $scope.DrawAll($scope.search);
        }
    };

    //DrawAll($scope.code);
}]);
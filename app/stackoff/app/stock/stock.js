'use strict';

angular.module('myApp.stock', ['ngRoute'])

.config(['$routeProvider', '$httpProvider', function($routeProvider) {
    $routeProvider.when('/stock', {
        templateUrl: 'stock/stock.html',
        controller: 'StockCtrl'
    });
}])

.controller('StockCtrl', ['$scope', '$http', function($scope, $http) {// 路径配置

    loadJS('stock_lib', 'stock/stock_lib.js');
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
            var current_url = getStockCurDataURLfromLocal(code);
            var history_url = getStockHistoryDataURL(code,
                                                     cur_time['year']-1,
                                                     (cur_time['month']+9) % 12,
                                                     cur_time['date'],
                                                     cur_time['year'],
                                                     cur_time['month'],
                                                     cur_time['date']);
            var history_httpcli = GetHttpRequest();

            function updateStockInfo() {
                $http.get(current_url).success(function (data) {
                    var result = processStockCurDatafromLocal(data);
                    $scope.data.current = result['cline']['current'];
                    $scope.data.high = result['cline']['high'];
                    $scope.data.low = result['cline']['low'];
                    $scope.data.volumeper = result['cline']['volumeper'];
                    $scope.data.preclose = result['cline']['preclose'];
                    $scope.data.open = result['cline']['open'];
                    $scope.data.change = result['cline']['change'];
                    $scope.data.changeper = result['cline']['changeper'];
                    $scope.data.tradechange = result['cline']['tradechange'];
                    $scope.data.tradeper = result['cline']['tradeper'];
                    $scope.data.marketprice = result['cline']['marketprice'];
                    $scope.data.name = result['name'];
                    $scope.data.tradein1 = result['cline']['tradein_1'];
                    $scope.data.tradein2 = result['cline']['tradein_2'];
                    $scope.data.tradein3 = result['cline']['tradein_3'];
                    $scope.data.tradein4 = result['cline']['tradein_4'];
                    $scope.data.tradein5 = result['cline']['tradein_5'];
                    $scope.data.tradeout1 = result['cline']['tradeout_1'];
                    $scope.data.tradeout2 = result['cline']['tradeout_2'];
                    $scope.data.tradeout3 = result['cline']['tradeout_3'];
                    $scope.data.tradeout4 = result['cline']['tradeout_4'];
                    $scope.data.tradeout5 = result['cline']['tradeout_5'];
                });
                if (history_httpcli != null) {
                    history_httpcli.onreadystatechange = function () {
                        if (history_httpcli.readyState == 4 && history_httpcli.status == 200) {
                            var result = processStockHistoryData(history_httpcli.responseText);
                            var myChart_k = ec.init(document.getElementById('stock_k'));
                            var option_k = buildKLineOptions(result['datelines'], result['kline']);
                            myChart_k.setOption(option_k);
                            var myChart_v = ec.init(document.getElementById('stock_v'));
                            var option_v = pluginVolumeOptions(result['datelines'], result['volume']);
                            myChart_v.setOption(option_v);
                            history_httpcli = null;
                        }
                    };
                    history_httpcli.open('GET', history_url, true);
                    history_httpcli.send(null);
                }
            }
            $scope.stocktimer = setInterval(updateStockInfo, 5 * 1000);
        }
        );
    }


    $scope.data = {};
    $scope.items = [];

    $scope.Search = function(e) {
        var keycode = window.event?e.keyCode:e.which;
        if (keycode == 13) {
            clearInterval($scope.stocktimer);
            $scope.code = $scope.search;
            DrawAll($scope.code, CurrentTime());
        }
    };

    //$scope.code = ['000001', '000002', '000003', '000004', '000005'];
    $scope.code = '000001';
    DrawAll($scope.code, CurrentTime());
}]);
'use strict';

angular.module('myApp.stock', ['ngRoute'])

.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/stock', {
    templateUrl: 'stock/stock.html',
    controller: 'StockCtrl'
  });
}])

.controller('StockCtrl', [function() {
}]);
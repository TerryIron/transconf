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

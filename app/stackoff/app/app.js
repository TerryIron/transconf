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

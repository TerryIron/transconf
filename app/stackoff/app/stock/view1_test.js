'use strict';

describe('myApp.stock.module', function() {

  beforeEach(module('myApp.stock'));

  describe('stock controller', function(){

    it('should ....', inject(function($controller) {
      //spec body
      var StockCtrl = $controller('StockCtrl');
      expect(StockCtrl).toBeDefined();
    }));

  });
});
(function () {
  'use strict';

  angular
    .module('platform.authentication', [
      'platform.authentication.controllers',
      'platform.authentication.services'
    ]);

  angular
    .module('platform.authentication.controllers', []);

  angular
    .module('platform.authentication.services', ['ngCookies']);
})();

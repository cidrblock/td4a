var app = angular.module('mainController', ['ngRoute', 'ngMaterial', 'ngMessages', 'ui.codemirror', 'ng-split', 'ngCookies', 'LocalStorageModule'])

    .config(function($routeProvider,$locationProvider) {
        $locationProvider.html5Mode(true);
    })
    .config(function (localStorageServiceProvider) {
        localStorageServiceProvider
          .setPrefix('td4a')
    });

app.controller('main', function($scope, $http, $window, $mdToast, $timeout, $routeParams, $location, $cookies, localStorageService) {
  $scope.error = {}
  $scope.panels = {}
  $scope.config = {}
  $scope.demoShown = $cookies.get('demoShown') || false;

  $scope.extraKeys = {
    Tab: function(cm) {
      var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
      cm.replaceSelection(spaces);
    },
    "Cmd-S": function(cm) {
      localStorageService.set('panels', $scope.panels)
      localStorageService.set('config', $scope.config)
      var toast = $mdToast.simple()
        .textContent("Saved")
        .action('close')
        .highlightAction(true)
        .highlightClass('md-primary')
        .position('top right')
        .hideDelay('2000');
      $mdToast.show(toast)
    },
    "Cmd-R": function(cm) {
      $scope.p2_b1_click()
    },
    "Cmd-B": function(cm) {
      $scope.panels = { p1: '', p2: '', p3: '' };
      $timeout(function() {cm.refresh();});
    },

  }

  $scope.getter = function(rroute) {
      return $http
        .get(rroute).then(function(response) {
          if ((typeof(response.data) == 'object') && ("handled_error" in response.data)) {
            $scope.handledError(response.data.handled_error)
            return response.data;
          } else {
            return response.data;
          }
        })
        .catch(function(error) {
          console.log(error)
          return error
        }) //catch
  };

  $scope.init = function() {
    if (Object.keys($scope.config).length == 0) {
      $scope.getter('/config')
        .then(function(data) {
          $scope.config = data;
          $scope.config.p1.options.extraKeys = $scope.config.p2.options.extraKeys = $scope.extraKeys
          $scope.inventory()
        })
    } else {
      $scope.config.p1.options.extraKeys = $scope.config.p2.options.extraKeys = $scope.extraKeys
      $scope.inventory()

    }
  }

  $scope.inventory = function() {
    if ($scope.config.p1.inventory) {
      $scope.getter('/hosts')
        .then(function(data){
          $scope.hosts = data['hosts'];
        })
    }
  }

  $scope.handledError = function(error) {
    console.log(error.raw_error)
    if (error.line_number) {
        var errorMessage = `${error.title} ${error.details} Line number: ${error.line_number}\n`;
        var actualLineNumber = error.line_number -1 ;
        if (error.in == "p2") {
          var myEditor = angular.element(document.getElementById('p2_editor'))
        } else if (error.in == "p1") {
          var myEditor = angular.element(document.getElementById('p1_editor'))
        }
         var codeMirrorEditor = myEditor[0].childNodes[0].CodeMirror
         $scope.error.codeMirrorEditor = codeMirrorEditor
         $scope.error.line_number = actualLineNumber
         $scope.error.codeMirrorEditor.addLineClass($scope.error.line_number, 'wrap', 'error');
         codeMirrorEditor.scrollIntoView({line: actualLineNumber});
    } else {
        var errorMessage = `${error.title} ${error.details}\n`;
    }
    var toast = $mdToast.simple()
      .textContent(errorMessage)
      .action('close')
      .highlightAction(true)
      .highlightClass('md-warn')
      .position('top right')
      .hideDelay('60000');
    $mdToast.show(toast)
  };

  $scope.link = function() {
    $http({
          method  : 'POST',
          url     : '/link',
          data    : {"panels": {"p1": $scope.panels.p1, "p2": $scope.panels.p2}, "config": $scope.config},
          headers : { 'Content-Type': 'application/json' }
         })
      .then(function(response) {
          if (response.status == 200) {
            if ("handled_error" in response.data) {
              $scope.handledError(response.data.handled_error)
            } else {
              $location.search(`id=${response.data.id}`)
            }
          }
        }) //then
      .catch(function(error) {
        console.log(error.data)
      }) //catch
  }

  $scope.p1_b1_click = function() {
    $scope.config.p1.b1.show = false;
    $http({
          method  : 'POST',
          url     : $scope.config.p1.b1.url,
          data    : { "p1": $scope.panels.p1  },
          headers : { 'Content-Type': 'application/json' }
         })
      .then(function(response) {
        if (response.status == 200) {
          if ("handled_error" in response.data) {
            $scope.handledError(response.data.handled_error)
          } else {
            Object.assign($scope.panels, response.data);
          }
          $scope.config.p1.b1.show = true;
        }
      })
      .catch(function(error) {
        console.log(error.data)
        $scope.config.p1.b1.show = true;
      }) //catch
    } //render

  $scope.p2_b1_click = function() {
    $scope.config.p2.b1.show = false;
    if ('line_number' in $scope.error) {
      $scope.error.codeMirrorEditor.removeLineClass($scope.error.line_number, 'wrap', 'error');
    }
    $http({
          method  : 'POST',
          url     : $scope.config.p2.b1.url,
          data    : { "p1": $scope.panels.p1, "p2": $scope.panels.p2 },
          headers : { 'Content-Type': 'application/json' }
         })
      .then(function(response) {
        if (response.status == 200) {
          if ("handled_error" in response.data) {
            $scope.handledError(response.data.handled_error)
          } else {
            Object.assign($scope.panels, response.data);
          }
          $scope.config.p2.b1.show = true;
        }
      })
      .catch(function(error) {
        console.log(error.data)
        $scope.config.p2.b1.show = true;
      }) //catch
    } //render

  $scope.SelectedItemChange = function(host) {
    if (host != null) {
      $scope.getter(`inventory?host=${host}`)
        .then(function(data) {
          Object.assign($scope.panels, data)
        });
    }
  }

  $scope.showDemo = function() {
    $scope.getter('data.yml')
      .then(function(data) {
        $scope.panels.p1 = data
      })
    $scope.getter('template.j2')
      .then(function(data) {
        $scope.panels.p2 = data
      })
  }

  if ('id' in $location.search()) {
    $scope.getter(`/retrieve?id=${$location.search().id}`)
      .then(function(data) {
        if ((typeof(data) == 'object') && ("handled_error" in data)) {
          $scope.showDemo()
          $scope.init()
        } else {
          Object.assign($scope.config, data['config'])
          Object.assign($scope.panels, data['panels'])
          $scope.init()
        }
      })
  } else if (!($scope.demoShown)) {
    $scope.showDemo()
    $cookies.put('demoShown',true);
    $scope.init()
  } else if ( localStorageService.get('panels') && localStorageService.get('config')) {
    $scope.panels = localStorageService.get('panels')
    $scope.config = localStorageService.get('config')
    $scope.init()
  } else {
    $scope.panels = { p1: '', p2: '' }
    $scope.init()
  };







}); //controller

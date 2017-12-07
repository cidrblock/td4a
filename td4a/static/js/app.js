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
  $scope.template = { data: '', jinja: '' }
  $scope.renderButton = false;
  $scope.showDemo = $cookies.firstVisit || "";

  extraKeys= {
    Tab: function(cm) {
      var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
      cm.replaceSelection(spaces);
    },
    "Cmd-S": function(cm) {
      localStorageService.set('data', $scope.template)
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
      $scope.render()
    },
    "Cmd-B": function(cm) {
      $scope.template = { data: '', jinja: '', result: '' };
      $timeout(function() {cm.refresh();});
    },

  }

  $scope.codemirror = {
    dataOptions:
     {
        lineNumbers: true,
        theme:'material',
        lineWrapping : true,
        mode: 'yaml',
        indentUnit: 2,
        tabSize: 2,
        extraKeys: extraKeys
      },
    templateOptions:
     {
        lineNumbers: true,
        theme:'material',
        lineWrapping : true,
        mode: 'jinja2',
        extraKeys: extraKeys
      },
    resultOptions:
     {
        lineNumbers: true,
        theme:'material',
        lineWrapping : true,
        mode: 'yaml',
      }
  };

  $scope.demoShown = $cookies.get('demoShown') || false;
  if (!($scope.demoShown)) {
    $cookies.put('demoShown',true);
    $http({
          method  : 'GET',
          url     : 'data.yml',
         })
      .then(function(response) {
          if (response.status == 200) {
              $scope.template.data = response.data
            }
          })
    $http({
          method  : 'GET',
          url     : 'template.j2',
         })
      .then(function(response) {
          if (response.status == 200) {
              $scope.template.jinja = response.data
            }
      })
  } else if ('id' in $location.search()) {
    $http({
          method  : 'GET',
          url     : `/retrieve?id=${$location.search().id}`,
         })
      .then(function(response) {
          if (response.status == 200) {
            if ("handled_error" in response.data) {
              $scope.handledError(response.data.handled_error)
            } else {
              $scope.template = response.data
            }
          }
        }) // then
        .catch(function(error) {
          console.log(error.data)
        }) //catch

  } else {
    $scope.template = localStorageService.get('data')
  };

  $http({
        method  : 'GET',
        url     : 'config',
       })
    .then(function(response) {
        if (response.status == 200) {
            $scope.config = response.data
            console.log($scope.config)
            if ($scope.config.inventory) {
              $http({
                    method  : 'GET',
                    url     : 'hosts',
                   })
                .then(function(response) {
                    if (response.status == 200) {
                        $scope.hosts = response.data.hosts
                      }
                }) // then
            } // if inventory
          } // if 200
    }) // then


  $scope.SelectedItemChange = function(host) {
    if (host != null) {
      $http({
            method  : 'GET',
            url     : `inventory?host=${host}`,
           })
        .then(function(response) {
            if (response.status == 200) {
                $scope.template.data = response.data.data
              }
        })
    }
  }

  $scope.handledError = function(error) {
    console.log(error.raw_error)
    if (error.line_number) {
        var errorMessage = `${error.title} ${error.details} Line number: ${error.line_number}\n`;
        var actualLineNumber = error.line_number -1 ;
        if (error.in == "template") {
          var myEditor = angular.element(document.getElementById('templateEditor'))
        } else if (error.in == "data") {
          var myEditor = angular.element(document.getElementById('dataEditor'))
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
    console.log("shown?")
  };

  $scope.link = function() {
    $http({
          method  : 'POST',
          url     : '/link',
          data    : { "data": $scope.template.data, "template": $scope.template.jinja },
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

  $scope.render = function() {
    $scope.renderButton = true;
    if ('line_number' in $scope.error) {
      $scope.error.codeMirrorEditor.removeLineClass($scope.error.line_number, 'wrap', 'error');
    }
    $http({
          method  : 'POST',
          url     : '/render',
          data    : { "data": $scope.template.data, "template": $scope.template.jinja },
          headers : { 'Content-Type': 'application/json' }
         })
      .then(function(response) {
        if (response.status == 200) {
          if ("handled_error" in response.data) {
            $scope.handledError(response.data.handled_error)
          } else {
            $scope.template.result = response.data.result;
          }
          $scope.renderButton = false;
        }
      })
      .catch(function(error) {
        console.log(error.data)
        $scope.renderButton = false;
      }) //catch
    } //render
}); //controller

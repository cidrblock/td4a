var app = angular.module('mainController', ['ngRoute', 'ngMaterial', 'ngMessages', 'ui.codemirror', 'ng-split', 'ngCookies']);

app.config(function($routeProvider,$locationProvider) {
    $locationProvider.html5Mode(true);
})

app.controller('main', function($scope, $http, $window, $mdToast, $routeParams, $location, $cookies) {
  $scope.error = {}
  $scope.template = { data: '', jinja: '' }
  $scope.renderButton = false;
  $scope.showDemo = $cookies.firstVisit || "";
  $scope.codemirror = {
    dataOptions:
     {
        lineNumbers: true,
        theme:'material',
        lineWrapping : true,
        mode: 'yaml',
        indentUnit: 2,
        tabSize: 2,
        extraKeys: {
          Tab: function(cm) {
            var spaces = Array(cm.getOption("indentUnit") + 1).join(" ");
            cm.replaceSelection(spaces);
          }
        }
      },
    templateOptions:
     {
        lineNumbers: true,
        theme:'material',
        lineWrapping : true,
        mode: 'jinja2'
      },
    resultOptions:
     {
        lineNumbers: true,
        theme:'material',
        lineWrapping : true,
        mode: 'yaml',
      }
  }
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
            $scope.template.result = response.data.result;
            $scope.renderButton = false;
          }
        })
    .catch(function(error) {
      if ("Error" in error.data) {
        var errorMessage = `${error.data.Error.title}, ${error.data.Error.details}, line number: ${error.data.Error.line_number}\n`;
        var toast = $mdToast.simple()
          .textContent(errorMessage)
          .action('close')
          .highlightAction(true)
          .highlightClass('md-warn')
          .position('top right')
          .hideDelay('60000');
        $mdToast.show(toast)

        var actualLineNumber = error.data.Error.line_number -1 ;
        if (error.data.Error.in == "template") {
          var myEditor = angular.element(document.getElementById('templateEditor'))
        } else if (error.data.Error.in == "data") {
          var myEditor = angular.element(document.getElementById('dataEditor'))
        }
         var codeMirrorEditor = myEditor[0].childNodes[0].CodeMirror
         $scope.error.codeMirrorEditor = codeMirrorEditor
         $scope.error.line_number = actualLineNumber
         $scope.error.codeMirrorEditor.addLineClass($scope.error.line_number, 'wrap', 'error');
         codeMirrorEditor.scrollIntoView({line: actualLineNumber});
         $scope.renderButton = false;
      } else {
        console.log(error.data)
        $scope.renderButton = false;

      }
    });
  }
});

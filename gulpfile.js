var gulp = require('gulp'),
    uglify = require('gulp-uglify'),
    jshint = require('gulp-jshint'),
    concat = require('gulp-concat'),
    notify = require('gulp-notify'),
    rename = require('gulp-rename'),
    clean = require('gulp-clean');

var jsDest = 'td4a/static/jsTemp';
var cssDest = 'td4a/static/css';

gulp.task('default', function() {
});

gulp.task('codemirror', function(done) {
  gulp.src("bower_components/codemirror/lib/codemirror.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/mode/jinja2/jinja2.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/mode/yaml/yaml.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/addon/dialog/dialog.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/addon/search/searchcursor.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/addon/search/search.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/addon/search/matchesonscrollbar.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/addon/scroll/annotatescrollbar.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/addon/search/jump-to-line.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/codemirror/lib/codemirror.css")
      .pipe(gulp.dest(cssDest));
  gulp.src("bower_components/codemirror/addon/dialog/dialog.css")
      .pipe(gulp.dest(cssDest));
  gulp.src("bower_components/codemirror/theme/material.css")
      .pipe(gulp.dest(cssDest));
  done();
});

gulp.task('angular', function(done) {
  gulp.src("bower_components/angular/angular.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/angular-animate/angular-animate.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/angular-aria/angular-aria.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/angular-messages/angular-messages.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/angular-route/angular-route.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/angular-cookies/angular-cookies.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/angular-local-storage/dist/angular-local-storage.js")
      .pipe(gulp.dest(jsDest));
  done();
});

gulp.task('angular-material', function(done) {
  gulp.src("bower_components/angular-material/angular-material.js")
      .pipe(gulp.dest(jsDest));
  gulp.src("bower_components/angular-material/angular-material.css")
      .pipe(gulp.dest(cssDest));
  done();
});

gulp.task('split', function(done) {
  gulp.src("bower_components/Split.js/split.js")
      .pipe(gulp.dest(jsDest));
  done();
});

gulp.task('ui-codemirror', function(done) {
  gulp.src("bower_components/angular-ui-codemirror/ui-codemirror.js")
      .pipe(gulp.dest(jsDest));
  done();
});

gulp.task('ng-split', function(done) {
  gulp.src("bower_components/ng-split/dist/ng-split.js")
      .pipe(gulp.dest(jsDest));
  done();
});

gulp.task('scripts', function(done) {
  gulp.src([
                    'td4a/static/jsTemp/angular.js',
                    'td4a/static/jsTemp/codemirror.js',
                    'td4a/static/jsTemp/*.js'
                  ])
    .pipe(concat('main.js'))
    .pipe(gulp.dest('dist'))
    .pipe(rename('main.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest('td4a/static/js'))
    .pipe(notify({ message: 'Scripts task complete' }));
  done();
});

gulp.task('clean', function (done) {
  gulp.src(['td4a/static/jsTemp',
                     'dist'
                    ], {read: false})
        .pipe(clean({force: true}));
  done();
});

gulp.task('default', gulp.series('codemirror', 'angular', 'angular-material', 'split', 'ng-split', 'ui-codemirror', 'scripts'))

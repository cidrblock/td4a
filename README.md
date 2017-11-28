![screenshot](screenshot.png)
## Template Designer for Automation

### Overview

TD4A is a visual design aid for building and testing jinja2 templates.  It will combine data in yaml format with a jinja2 template and render the output.

All jinja2 filters are supported along with the filter plguins from Ansible version 2.4.1.0.

### Installation:

```
$ virtualenv venv
$ source venv/bin/activate
$ pip install td4a
$ python -m td4a
```

### Usage

The interface is browser based and has been tested using Chrome. If your browser did not automatically open when TD4A was started, you can visit http://127.0.0.1:5000 to see the interface.

The UI is broken into three sections:

1) DATA, this is where the data in yaml format is provided.
2) TEMPLATE, the jinja2 template to be rendered.
3) RESULT, after clicking the render button, the result pane will be populated with the rendered template.

### Custom filters

TD4A can load custom filters from a directory specified from the command line:

```
python -m td4a -cff ./filter_plugins
```

### Python version

To date, this has only been tested with python 2.7.

### Development

NPM and related packages are required to build the UI.

```
npm install
```

The UI components can be installed for development purposes using bower.

```
bower install
```

The dependancies can be concatenated and minified using gulp.

```
gulp
```

#! /usr/bin/env python
"""
jinja template renderer
"""
from argparse import ArgumentParser, RawTextHelpFormatter
import importlib
import os
import re
import sys
import threading
import traceback
import webbrowser
import ansible.plugins.filter as apf
from flask import Flask, request, jsonify, current_app
import jinja2
from jinja2 import Environment, TemplateSyntaxError, TemplateAssertionError
import yaml

APP = Flask(__name__, static_url_path='')

def pack_ansible_filters():
    """ Load the ansible filters from the filter directory
    """
    filter_list = []
    ansible_filter_path = os.path.dirname(apf.__file__)
    sys.path.append(ansible_filter_path)
    for entry in os.listdir(ansible_filter_path):
        if entry != '__init__.py' and entry.split('.')[-1] == 'py':
            filters = importlib.import_module(entry[:-3]).FilterModule().filters()
            for key, value in filters.iteritems():
                filter_list.append((key, value))
    return filter_list

def pack_custom_filters(custom_filter_path):
    """ Load the custom filters
    """
    filter_list = []
    sys.path.append(custom_filter_path)
    for entry in os.listdir(custom_filter_path):
        if entry != '__init__.py' and entry.split('.')[-1] == 'py':
            filters = importlib.import_module(entry[:-3]).FilterModule().filters()
            for key, value in filters.iteritems():
                filter_list.append((key, value))
    return filter_list

def check_template(str_template):
    """ check a template for syntax errors
    """
    env = Environment()
    try:
        env.parse(str_template)
        return None, str_template
    except TemplateSyntaxError, error:
        tback = traceback.extract_tb(sys.exc_traceback)
        template_error = next(x for x in tback if re.match('^<.*>$', x[0]))
        return {"Error":
                {
                    "in": "template",
                    "title": "Syntax error found in template.",
                    "line_number": template_error[1],
                    "details": str(error)
                }
               }, None

def render_template(data, template):
    """ Render a jinja template

    Args:
        tpl_path (str): A path to the template
        context (dict): A dict to pass to the teplate
        filters (list): A list of filters

    Return:
        str: an error
    """
    try:
        env = Environment()
        env.trim_blocks = True
        for entry in APP.filters:
            env.filters[entry[0]] = entry[1]
        result = env.from_string(template).render(data)
        return None, result
    except Exception, error:
        tback = traceback.extract_tb(sys.exc_traceback)
        template_error = next(x for x in tback if re.search('^<.*>$', x[0]))
        if template_error:
            return {"Error":
                    {
                        "in": "template",
                        "title": "Issue found while rendering template.",
                        "line_number": template_error[1],
                        "details": str(error)
                    }
                   }, None
        else:
            return {"Error":
                    {
                        "in": "unknown",
                        "title": "Unexpected error occured.",
                        "line_number": 'unknown',
                        "details": "Please see the console for details."
                    }
                   }, None

def load_data(str_data):
    """ load yaml from string
    """

    try:
        data = yaml.load(str_data)
        return None, data
    except yaml.YAMLError, error:
        if hasattr(error, 'problem_mark'):
            mark = error.problem_mark
        return {"Error":
                {
                    "in": "data",
                    "title": "Issue found loading data.",
                    "line_number": mark.line+1,
                    "details": "Error while parsing data"
                }
               }, None

@APP.route('/')
def root():
    """ root path
    """
    return APP.send_static_file('index.html')

@APP.route('/render', methods=['POST'])
def render():
    """ render path
    """
    payload = request.json
    if payload['data'] and payload['template']:
        error, data = load_data(payload['data'])
        if error:
            response = jsonify(error)
            response.status_code = 400
            return response
        error, template = check_template(payload['template'])
        if error:
            response = jsonify(error)
            response.status_code = 400
            return response
        error, result = render_template(data, template)
        if error:
            response = jsonify(error)
            response.status_code = 400
            return response
    else:
        result = ""
    return jsonify({"result": result})

def main():
    """ main
    """
    parser = ArgumentParser(description='',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-cff', action="store", dest="custom_filters",
                        required=False,
                        help="a folder containing custom filters")
    args = parser.parse_args()
    ansible_filters = pack_ansible_filters()
    if args.custom_filters:
        custom_filters = pack_custom_filters(args.custom_filters)
        APP.filters = ansible_filters + custom_filters
    else:
        APP.filters = ansible_filters
    url = "http://127.0.0.1:5000"
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    APP.run(debug=False, host='0.0.0.0')

if __name__ == '__main__':
    main()

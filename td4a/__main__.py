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
from flask import Flask, request, jsonify
import requests
from jinja2 import Environment, TemplateSyntaxError
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

@APP.route('/link', methods=['POST'])
def link():
    """ Save the documents in a couchdb and returns an id
    """
    payload = request.json
    if APP.args.username and APP.args.password and APP.args.url:
        username = APP.args.username
        password = APP.args.password
        url = APP.args.url
        response = requests.post("%s" % url, json=payload, auth=(username, password))
        return jsonify({"id": response.json()['id']})
    return jsonify({"error": "true"})


@APP.route('/retrieve', methods=['GET'])
def retrieve():
    """ return a doc from the couchdb
    """
    docid = request.args.get('id')
    if APP.args.username and APP.args.password and APP.args.url:
        username = APP.args.username
        password = APP.args.password
        url = APP.args.url
        response = requests.get("%s/%s?include_docs=true" % (url, docid), auth=(username, password))
        if response.status_code != 200:
            return jsonify({"error": "true"})
        doc = response.json()
        return jsonify({"data": doc['data'], "jinja": doc['template']})
    return jsonify({"error": "true"})

@APP.route('/enablelink', methods=['GET'])
def enablelink():
    """ check to see if the link button should be enabled
    """
    return jsonify({"enabled": APP.args.enable_links})

def parse_args():
    """ parse the cli args and add environ
    """
    parser = ArgumentParser(description='',
                            formatter_class=RawTextHelpFormatter)
    parser.add_argument('-f', action="store", dest="custom_filters",
                        required=False,
                        help="A folder containing custom filters.")
    args = parser.parse_args()
    args.username = os.environ.get('COUCH_USERNAME', False)
    args.password = os.environ.get('COUCH_PASSWORD', False)
    args.enable_links = os.environ.get('ENABLE_LINK', False)
    args.url = os.environ.get('COUCH_URL', False)
    return args

def load_filters(args):
    """ load the filters
    """
    ansible_filters = pack_ansible_filters()
    if args.custom_filters:
        custom_filters = pack_custom_filters(args.custom_filters)
        filters = ansible_filters + custom_filters
    else:
        filters = ansible_filters
    return filters

def main():
    """ main
    """
    APP.args = parse_args()
    APP.filters = load_filters(APP.args)
    reactor_args = {}
    def run_twisted_wsgi():
        from twisted.internet import reactor
        from twisted.web.server import Site
        from twisted.web.wsgi import WSGIResource
        resource = WSGIResource(reactor, reactor.getThreadPool(), APP)
        site = Site(resource)
        reactor.listenTCP(5000, site)
        reactor.run(**reactor_args)
    if APP.debug:
        reactor_args['installSignalHandlers'] = 0
        import werkzeug.serving
        run_twisted_wsgi = werkzeug.serving.run_with_reloader(run_twisted_wsgi)
    url = "http://127.0.0.1:5000"
    threading.Timer(1.25, lambda: webbrowser.open(url)).start()
    run_twisted_wsgi()

if __name__ == '__main__':
    main()

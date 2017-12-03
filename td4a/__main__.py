#! /usr/bin/env python
"""
jinja template renderer
"""
from argparse import ArgumentParser, RawTextHelpFormatter
import importlib
import os
import sys
import threading
import webbrowser
import ansible.plugins.filter as apf
from flask import Flask, request, jsonify
import requests
from jinja2 import meta, Environment, StrictUndefined

from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
from modules.td4ayaml import Td4aYaml
from modules.exception_handler import ExceptionHandler, HandledException

APP = Flask(__name__, static_url_path='')

def filter_load_dir(directory):
    """ Load jinja filters in ansible format
    """
    filter_list = []
    sys.path.append(directory)
    for entry in os.listdir(directory):
        if entry != '__init__.py' and entry.split('.')[-1] == 'py':
            filters = importlib.import_module(entry[:-3]).FilterModule().filters()
            for key, value in filters.iteritems():
                filter_list.append((key, value))
    return filter_list

def filters_load(args):
    """ load the filters
    """
    filters = []
    filters.extend(filter_load_dir(os.path.dirname(apf.__file__)))
    if args.custom_filters:
        filters.extend(filter_load_dir(args.custom_filters))
    return filters

@ExceptionHandler
def jinja_unresolved(template, typ):
    """ Check a jinja template for any unresolved vars
    """
    _ = typ
    env = Environment(undefined=StrictUndefined)
    env.trim_blocks = True
    for entry in APP.filters:
        env.filters[entry[0]] = entry[1]
    unresolved = meta.find_undeclared_variables(env.parse(template))
    return unresolved

@ExceptionHandler
def jinja_render(data, template, typ):
    """ Render a jinja template
    """
    _ = typ
    env = Environment(undefined=StrictUndefined)
    env.trim_blocks = True
    for entry in APP.filters:
        env.filters[entry[0]] = entry[1]
    result = env.from_string(template).render(data)
    return result

@ExceptionHandler
def yaml_parse(string, typ):
    """ load yaml from string
    """
    _ = typ
    yaml = Td4aYaml()
    data = yaml.load(string)
    return data


@ExceptionHandler
def link(payload, typ):
    """ store a doc in the db
    """
    _ = typ
    auth = (APP.args.username, APP.args.password)
    url = APP.args.url
    response = requests.post("%s" % url, json=payload, auth=auth)
    return {"id": response.json()['id']}

@ExceptionHandler
def render(payload, typ):
    """ Given the payload, render the result
    """
    _ = typ
    try:
        yaml = Td4aYaml()
        result = None
        if payload['data'] and payload['template']:
            data = yaml_parse(string=payload['data'], typ="data")
            for _ in range(10):
                if jinja_unresolved(template=yaml.dump(data), typ="data"):
                    data_post_jijna = jinja_render(data=data,
                                                   template=yaml.dump(data),
                                                   typ="data")
                    data = yaml_parse(string=data_post_jijna, typ="data")
            result = jinja_render(data=data, template=payload['template'], typ="template")
        return {"result": result}
    except HandledException as error:
        return error.json()

@ExceptionHandler
def retrieve(doc_id, typ):
    """ get a doc from the db
    """
    _ = typ
    auth = (APP.args.username, APP.args.password)
    url = APP.args.url
    cdoc = requests.get("%s/%s?include_docs=true" % (url, doc_id), auth=auth)
    doc = cdoc.json()
    if cdoc.status_code == 200:
        response = {"data": doc['data'], "jinja": doc['template']}
    else:
        response = {"handled_error": {
            "in": "document retrieval",
            "title": "Message: Issue loading saved document.",
            "line_number": None,
            "details": "Details: %s" % doc['error'],
            "raw_error": "%s" % cdoc.text
            }
                   }
    return response

@APP.route('/')
def root():
    """ root path
    """
    try:
        return APP.send_static_file('index.html')
    except HandledException as error:
        return jsonify(error.json())

@APP.route('/link', methods=['POST'])
def rest_link():
    """ Save the documents in a couchdb and returns an id
    """
    try:
        response = link(payload=request.json, typ="link")
        return jsonify(response)
    except HandledException as error:
        return jsonify(error.json())

@APP.route('/render', methods=['POST'])
def rest_render():
    """ render path
    """
    try:
        response = render(payload=request.json, typ="page")
        return jsonify(response)
    except HandledException as error:
        return jsonify(error.json())

@APP.route('/retrieve', methods=['GET'])
def rest_retrieve():
    """ return a doc from the couchdb
    """
    try:
        response = retrieve(doc_id=request.args.get('id'), typ="link")
        return jsonify(response)
    except HandledException as error:
        return jsonify(error.json())

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

def main():
    """ main
    """
    APP.args = parse_args()
    APP.filters = filters_load(APP.args)
    reactor_args = {}
    APP.debug = False
    def run_twisted_wsgi():
        """ run twisted
        """
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

""" /render
"""
from flask import request, jsonify, Blueprint
from flask import current_app as app
from jinja2 import meta, Environment, StrictUndefined
from td4a.models.exception_handler import ExceptionHandler, HandledException
from td4a.models.td4ayaml import Td4aYaml

api_render = Blueprint('api_render', __name__) # pylint: disable=invalid-name

def jinja_env(filters):
    """ return a jinja env
    """
    env = Environment(undefined=StrictUndefined)
    env.trim_blocks = True
    for entry in filters:
        env.filters[entry[0]] = entry[1]
    return env

@ExceptionHandler
def jinja_unresolved(template, filters, typ):
    """ Check a jinja template for any unresolved vars
    """
    _ = typ
    env = jinja_env(filters=filters)
    unresolved = meta.find_undeclared_variables(env.parse(template))
    return unresolved

@ExceptionHandler
def jinja_render(data, template, filters, typ):
    """ Render a jinja template
    """
    _ = typ
    env = jinja_env(filters=filters)
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
def render(payload, filters, typ):
    """ Given the payload, render the result
    """
    _ = typ
    try:
        yaml = Td4aYaml()
        result = None
        if payload['data'] and payload['template']:
            data = yaml_parse(string=payload['data'], typ="data")
            for _ in range(10):
                if jinja_unresolved(template=yaml.dump(data), filters=filters, typ="data"):
                    data_post_jijna = jinja_render(data=data,
                                                   template=yaml.dump(data),
                                                   filters=filters,
                                                   typ="data")
                    data = yaml_parse(string=data_post_jijna, typ="data")
            result = jinja_render(data=data,
                                  template=payload['template'],
                                  filters=filters,
                                  typ="template")
        return {"result": result}
    except HandledException as error:
        return error.json()

@api_render.route('/render', methods=['POST'])
def rest_render():
    """ render path
    """
    try:
        response = render(payload=request.json, filters=app.filters, typ="page")
        return jsonify(response)
    except HandledException as error:
        return jsonify(error.json())

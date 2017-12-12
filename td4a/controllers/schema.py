""" /retrieve
"""
import json
from flask import current_app as app
from flask import request, jsonify, Blueprint
from td4a.models.exception_handler import ExceptionHandler, HandledException
from td4a.models.sort_commented_map import sort_commented_map
from td4a.models.td4ayaml import Td4aYaml
import genson

api_schema = Blueprint('api_schema', __name__) # pylint: disable=invalid-name

@ExceptionHandler
def schema(data, typ):
    """ Build schema from data
    """
    _ = typ
    yaml = Td4aYaml()
    obj_data = yaml.load(data['p1'])
    json_schema = genson.Schema()
    json_schema.add_object(obj_data)
    schema_dict = json_schema.to_dict()
    schema_yaml = yaml.load(yaml.dump(schema_dict))
    sorted_schema_yaml = sort_commented_map(commented_map=schema_yaml)
    sorted_schema_string = yaml.dump(sorted_schema_yaml)
    return sorted_schema_string

@api_schema.route('/schema', methods=['POST'])
def rest_schema():
    """ Build a schema for data
    """
    try:
        payload = request.json
        response = schema(data=payload, typ="data")
        return jsonify({"p2": response})
    except HandledException as error:
        return jsonify(error.json())

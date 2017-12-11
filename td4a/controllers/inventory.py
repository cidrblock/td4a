""" /inventory
"""
from flask import request, jsonify, Blueprint
from flask import current_app as app
from td4a.models.exception_handler import ExceptionHandler, HandledException
from td4a.models.td4ayaml import Td4aYaml
import json
import collections

api_inventory = Blueprint('api_inventory', __name__) # pylint: disable=invalid-name

@api_inventory.route('/inventory', methods=['GET'])
def rest_inventory():
    """ return inventory for host
    """
    yaml = Td4aYaml()
    inventory = app.inventory.get(request.args.get('host'), "")
    data = json.loads(json.dumps(inventory))
    response_text = ''
    for section in sorted(data.keys()):
        response_text += yaml.dump({section: data[section]})
    response = {"p1": response_text}
    return jsonify(response)

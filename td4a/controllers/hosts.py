""" /hosts
"""
from flask import jsonify, Blueprint
from flask import current_app as app

api_hosts = Blueprint('api_hosts', __name__)  # pylint: disable=invalid-name

@api_hosts.route('/hosts', methods=['GET'])
def hosts():
    """ check to see if the link button should be enabled
    """
    devices = app.inventory.keys()
    return jsonify({"hosts": sorted(devices)})

""" /enablelink
"""
from flask import jsonify, Blueprint
from flask import current_app as app

api_enable_link = Blueprint('api_enable_link', __name__)  # pylint: disable=invalid-name

@api_enable_link.route('/enablelink', methods=['GET'])
def enablelink():
    """ check to see if the link button should be enabled
    """
    return jsonify({"enabled": app.args.enable_links})

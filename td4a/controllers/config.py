""" /config
"""
from flask import jsonify, Blueprint
from flask import current_app as app

api_config = Blueprint('api_config', __name__)  # pylint: disable=invalid-name

@api_config.route('/config', methods=['GET'])
def config():
    """ provide some config options to the UI
    """
    ui_config = {"link": bool(app.args.url), "inventory": bool(app.args.inventory_source)}
    return jsonify(ui_config)

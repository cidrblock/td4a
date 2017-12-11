""" /config
"""
from flask import jsonify, Blueprint
from flask import current_app as app

api_config = Blueprint('api_config', __name__)  # pylint: disable=invalid-name

@api_config.route('/config', methods=['GET'])
def config():
    """ provide some config options to the UI
    """
    if app.args.ui_mode == "jinja":
        ui_config = {
            "p1": {
                "options": {
                    "lineNumbers": True,
                    "theme":"material",
                    "lineWrapping" : True,
                    "mode": "yaml",
                    "indentUnit": 2,
                    "tabSize": 2
                },
                "title": "DATA",
                "inventory": bool(app.args.inventory_source),
                "b1": {
                    "show": False,
                    "text": None,
                    "url": None
                }
            },
            "p2": {
                "options": {
                    "lineNumbers": True,
                    "theme": "material",
                    "lineWrapping" : True,
                    "mode": "jinja2"
                },
                "title": "RENDER",
                "b1": {
                    "show": True,
                    "text": "Render",
                    "url": "/render"
                }
            },
            "p3":  {
                "options": {
                    "lineNumbers": True,
                    "theme": "material",
                    "lineWrapping" : True,
                    "mode": 'text'
                },
                "title": "RESULT",
                "b1": {
                    "show": bool(app.args.url),
                    "text": "link"
                }
            }
        }
    return jsonify(ui_config)

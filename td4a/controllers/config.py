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
                    "icon": None,
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
                    "icon": "create",
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
                    "icon": "link",
                    "show": bool(app.args.url),
                    "text": "link"
                }
            }
        }
    elif app.args.ui_mode == "schema":
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
                    "icon": "create",
                    "show": True,
                    "text": "schema",
                    "url": "/schema"
                }
            },
            "p2": {
                "options": {
                    "lineNumbers": True,
                    "theme": "material",
                    "lineWrapping" : True,
                    "mode": "yaml"
                },
                "title": "SCHEMA",
                "b1": {
                    "icon": "check",
                    "show": True,
                    "text": "Validate",
                    "url": "/validate"
                }
            },
            "p3":  {
                "options": {
                    "lineNumbers": True,
                    "theme": "material",
                    "lineWrapping" : True,
                    "mode": "yaml"
                },
                "title": "VALIDATION SUCCESS/ERRORS",
                "b1": {
                    "icon": "link",
                    "show": bool(app.args.url),
                    "text": "link"
                }
            }
        }
    return jsonify(ui_config)

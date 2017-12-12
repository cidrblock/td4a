from flask import Flask, request, jsonify
from td4a.controllers.config import api_config
from td4a.controllers.hosts import api_hosts
from td4a.controllers.inventory import api_inventory
from td4a.controllers.link import api_link
from td4a.controllers.render import api_render
from td4a.controllers.retrieve import api_retrieve
from td4a.controllers.schema import api_schema
from td4a.controllers.validate import api_validate




app = Flask(__name__, static_url_path='') # pylint: disable=invalid-name
app.register_blueprint(api_config)
app.register_blueprint(api_hosts)
app.register_blueprint(api_inventory)
app.register_blueprint(api_link)
app.register_blueprint(api_render)
app.register_blueprint(api_retrieve)
app.register_blueprint(api_schema)
app.register_blueprint(api_validate)

@app.route('/')
def root():
    """ root path
    """
    return app.send_static_file('index.html')

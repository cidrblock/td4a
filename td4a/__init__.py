from flask import Flask, request, jsonify
from td4a.controllers.render import api_render
from td4a.controllers.link import api_link
from td4a.controllers.retrieve import api_retrieve
from td4a.controllers.enable_link import api_enable_link

app = Flask(__name__, static_url_path='') # pylint: disable=invalid-name
app.register_blueprint(api_render)
app.register_blueprint(api_link)
app.register_blueprint(api_retrieve)
app.register_blueprint(api_enable_link)

@app.route('/')
def root():
    """ root path
    """
    return app.send_static_file('index.html')

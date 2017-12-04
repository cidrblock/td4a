from flask import request, jsonify, Blueprint
from flask import current_app as app
from td4a.models.exception_handler import ExceptionHandler, HandledException
import requests

api_link = Blueprint('api_link', __name__)

@ExceptionHandler
def link(payload, args, typ):
    """ store a doc in the db
    """
    _ = typ
    auth = (args.username, args.password)
    url = args.url
    response = requests.post("%s" % url, json=payload, auth=auth)
    return {"id": response.json()['id']}


@api_link.route('/link', methods=['POST'])
def rest_link():
    """ Save the documents in a couchdb and returns an id
    """
    try:
        response = link(payload=request.json, args=app.args, typ="link")
        return jsonify(response)
    except HandledException as error:
        return jsonify(error.json())

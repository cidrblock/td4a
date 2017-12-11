""" /retrieve
"""
from flask import request, jsonify, Blueprint
from flask import current_app as app
from td4a.models.exception_handler import ExceptionHandler, HandledException
import requests

api_retrieve = Blueprint('api_retrieve', __name__) # pylint: disable=invalid-name

@ExceptionHandler
def retrieve(doc_id, typ):
    """ get a doc from the db
    """
    _ = typ
    auth = (app.args.username, app.args.password)
    url = app.args.url
    cdoc = requests.get("%s/%s?include_docs=true" % (url, doc_id), auth=auth)
    doc = cdoc.json()
    if cdoc.status_code == 200:
        response = {"panels": doc['panels'], "config": doc['config']}
    else:
        response = {"handled_error": {
            "in": "document retrieval",
            "title": "Message: Issue loading saved document.",
            "line_number": None,
            "details": "Details: %s" % doc['error'],
            "raw_error": "%s" % cdoc.text
            }
                   }
    return response

@api_retrieve.route('/retrieve', methods=['GET'])
def rest_retrieve():
    """ return a doc from the couchdb
    """
    try:
        response = retrieve(doc_id=request.args.get('id'), typ="link")
        return jsonify(response)
    except HandledException as error:
        return jsonify(error.json())

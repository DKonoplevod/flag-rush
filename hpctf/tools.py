import json
from bson import ObjectId
from flask import make_response, request
from hpctf import db
import datetime


def jsonify(obj, attributes=[], include=[], exclude=[]):
    j = {}
    if not attributes:
        attributes = obj._fields.keys()
    for attr_name in include:
        if attr_name not in attributes:
            attributes.append(attr_name)

    for attr_name in attributes:
        if attr_name in exclude:
            continue
        attr = getattr(obj, attr_name, None)
        if attr is None:
            j[attr_name] = ""
        elif isinstance(attr, ObjectId):
            j[attr_name] = unicode(attr)
        elif isinstance(attr, datetime.datetime):
            j[attr_name] = unicode(attr)
        elif isinstance(attr, db.Document):
            j[attr_name] = unicode(attr.id)
        elif isinstance(attr, list):
            j[attr_name] = [unicode(item) for item in attr]
        else:
            j[attr_name] = attr
    return j


def render_json(data):
    response = make_response('{} ('.format(request.args.get('callback', '')) + json.dumps(data) + ');')
    response.headers['Content-Type'] = 'text/javascript'
    return response

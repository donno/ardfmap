#!/usr/bin/env python
"""A prototype server developed as a proof-of-concept for a new mapping system
for foxhunting and balloon chases.

This requires Flask, which is a microframework for Python.
See http://flask.pocoo.org/
"""

import database
import flask

app = flask.Flask(__name__, static_url_path='', static_folder='')
db = database.getDatabase()


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/geometry', methods=['GET'])
def geometryList():
    lastTime = flask.request.args.get('lastTime', None)
    return flask.json.jsonify(db.getGeometry(lastTime))


@app.route('/api/geometry', methods=['POST'])
def geometryCreate():
    """Creates new geometry in the database."""
    geoJson = flask.request.get_json()
    databaseId = db.addGeometry(geoJson, 'NYI')
    return flask.json.jsonify({
        "message": "New geometry saved.",
        "databaseId": databaseId,
        })


@app.route('/api/geometry/<int:geoId>', methods=['GET'])
def geometry(geoid):
    geometry = db.getGeometry(geometryId=geoId)['geometry'][0]
    return flask.json.jsonify(geometry)


@app.route('/api/geometry/<int:geoId>', methods=['PUT'])
def geometryEdit(geoId):
    geoJson = flask.request.get_json()
    db.updateGeometry(geoId, geoJson)
    return flask.json.jsonify({
        "message": "Updated geometry %d." % geometryId,
        "databaseId": geometryId,
        })


@app.route('/api/geometry/<int:geoId>', methods=['DELETE'])
def geometryDelete(geoId):
    db.deleteGeometry(geoId)
    return flask.json.jsonify({"deleted": geoId})


if __name__ == '__main__':
    app.run(port=8083)

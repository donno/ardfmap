#!/usr/bin/env python
"""A prototype server developed as a proof-of-concept for a new mapping system
for foxhunting and balloon chases.

This requires Flask, which is a microframework for Python.
See http://flask.pocoo.org/
"""

import database
import flask
import flask.ext.login

app = flask.Flask(__name__, static_url_path='', static_folder='')
db = database.getDatabase()
loginManager = flask.ext.login.LoginManager(app)


class User(flask.ext.login.UserMixin):
    def __init__(self, uid, username):
        self.uid = uid
        self.username = username

    def get_id(self):
        return self.uid


@loginManager.user_loader
def loadUser(userid):
    username, active = db.user(int(userid))
    return User(userid, username)


@app.route("/api/login", methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        contentType = flask.request.headers.get('Content-Type')
        if contentType.startswith('application/json'):
            body = flask.request.get_json()
            username = body.get('username')
            password = body.get('password')
        else:
            username = flask.request.form['username']
            password = flask.request.form['password']
    elif flask.request.method == 'GET':
        username = flask.request.args.get('username')
        password = flask.request.args.get('password')

    userId = db.login(username, password)
    if userId is not None:
        # TODO: Return the user id and remember that.
        user = User(userId, username)
    else:
        user = flask.ext.login.AnonymousUserMixin()

    loggedIn = flask.ext.login.login_user(user)
    next = flask.request.args.get("next")
    if loggedIn and next:
        flask.redirect(next)
    elif loggedIn:
        return flask.json.jsonify({
            'login': 'successful' if loggedIn else 'failed',
        })
    else:
        return app.response_class(flask.json.dumps({
            'error': {
                'code': 400,
                'message': 'The username and/or password is incorrect.',
            }}),
            status=400,
            mimetype='application/json')


@app.route("/api/logout", methods=['GET'])
@flask.ext.login.login_required
def logout():
    flask.ext.login.logout_user()
    return flask.json.jsonify({
        "action": "logout",
        "message": "Logged out successfully",
        })


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/geometry', methods=['GET'])
def geometryList():
    lastTime = flask.request.args.get('lastTime', None)
    return flask.json.jsonify(db.getGeometry(lastTime))


@app.route('/api/geometry', methods=['POST'])
@flask.ext.login.login_required
def geometryCreate():
    """Creates new geometry in the database."""
    username = flask.ext.login.current_user.username
    geoJson = flask.request.get_json()
    databaseId = db.addGeometry(geoJson, username)
    return flask.json.jsonify({
        "message": "New geometry saved.",
        "databaseId": databaseId,
        })


@app.route('/api/geometry/<int:geoId>', methods=['GET'])
def geometry(geoid):
    geometry = db.getGeometry(geometryId=geoId)['geometry'][0]
    return flask.json.jsonify(geometry)


@app.route('/api/geometry/<int:geoId>', methods=['PUT'])
@flask.ext.login.login_required
def geometryEdit(geoId):
    geoJson = flask.request.get_json()
    db.updateGeometry(geoId, geoJson)
    return flask.json.jsonify({
        "message": "Updated geometry %d." % geometryId,
        "databaseId": geometryId,
        })


@app.route('/api/geometry/<int:geoId>', methods=['DELETE'])
@flask.ext.login.login_required
def geometryDelete(geoId):
    db.deleteGeometry(geoId)
    return flask.json.jsonify({"deleted": geoId})


if __name__ == '__main__':
    app.secret_key = "ardfmap_1234"
    #app.config.update({'PROPAGATE_EXCEPTIONS': True})
    app.run(port=8083, debug=False)

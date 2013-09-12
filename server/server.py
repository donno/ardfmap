#!/usr/bin/env python
"""A prototype server developed as a proof-of-concept for a new mapping system
for foxhunting and balloon chases."""

import BaseHTTPServer
import CGIHTTPServer
import SimpleHTTPServer
import cgi
import json
import urlparse
import re

import database

db = database.getDatabase()

# TODO: Factor out the API part.

class APIError(Exception):
  def __init__(self, message, code):
    Exception.__init__(self, message)
    self.code = code

def login(username, password):
  if not username:
    raise APIError("no username was given", code=401)
  elif not password:
    raise APIError("no password was given", code=401)

  response = db.login(username, password)
  if not response:
    raise APIError("the username and/or password was incorrect.", code=401)
  else:
    return '{"message": "loggedin"}'

class ApiHandler:

  geometryMatcher = re.compile("/api/geometry/(\d+)/?")

  def __call__(self, handler, method):
    print 'ApiHandler(%s)' % handler.path
    contentType = handler.headers.getheader('content-type')
    if contentType:
      ctype, pdict = cgi.parse_header(contentType)
    else:
      ctype, pdict = None, None

    matches = self.geometryMatcher.match(handler.path)
    if matches:
      # We found /api/geometry/<id>
      #
      # Supported actions are GET and DELETE.
      if method != 'PUT' and method != 'GET' and method != 'DELETE':
        raise APIError("Only PUT, GET and DELETE are supported", code=405)

      geometryId = int(matches.group(1))

      if method == 'GET':
        # TODO: Handle the case where there is no geometry with the given ID.
        geometry = db.getGeometry(geometryId=geometryId)['geometry'][0]
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        json.dump(geometry, handler.wfile)
      elif method == 'PUT':
        length = int(handler.headers.getheader('content-length'))
        try:
          geoJson = json.loads(handler.rfile.read(length))
        except ValueError, e:
          raise APIError("Failed to parse request body.", code=400)

        db.updateGeometry(geometryId, geoJson)

        handler.wfile.write('{"message": "New geometry saved.",'
                            '"databaseId": ' + str(geometryId) + '}')

      elif method == 'DELETE':
        #raise APIError("DELETE has not been implemented yet.", code=501)

        # TODO: Handle what happens if its permission denied.
        db.deleteGeometry(geometryId)
        # Assume it worked.

        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        json.dump({'deleted': geometryId}, handler.wfile)
    elif handler.path == u'/api/login':
      if method != 'POST':
        raise APIError("Only POST is supported", code=405)
      if ctype != 'application/json':
        raise APIError("Only application/json is accepted.", code=406)

      length = int(handler.headers.getheader('content-length'))
      try:
        requestBody = json.loads(handler.rfile.read(length))
      except ValueError, e:
        raise APIError("failed to parse request body.", code=400)

      r = login(requestBody.get('username'), requestBody.get('password'))

      handler.send_response(200)
      handler.send_header("Content-type", "application/json")
      handler.end_headers()
      handler.wfile.write(r)
    elif (handler.path == u'/api/geometry' or
          (method == 'GET' and handler.path.startswith(u'/api/geometry?'))):
      if method != 'POST' and method != 'GET':
        raise APIError("Only POST and GET are supported", code=405)

      if method == 'GET':
        # Check if there is the query parameters.
        qs = urlparse.parse_qs(urlparse.urlparse(handler.path).query,
                               keep_blank_values=True)
        lastTime = qs.get('lastTime', [None])[0]

        # List all the geometry or the new geometry since lastTime.
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        json.dump(db.getGeometry(lastTime), handler.wfile)
      elif method == 'POST':
        # Save new geometry.
        length = int(handler.headers.getheader('content-length'))
        try:
          geoJson = json.loads(handler.rfile.read(length))
        except ValueError, e:
          raise APIError("failed to parse request body.", code=400)

        databaseId = db.addGeometry(geoJson)
        assert isinstance(databaseId, int)
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        handler.wfile.write('{"message": "New geometry saved.",'
                            '"databaseId": ' + str(databaseId) + '}')

class RequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

  def common(self, method):
    if self.path.startswith('/api/'):
      try:
        try:
          return self.api(self, method)
        except NotImplementedError, e:
          raise APIError(e.message, code=501)
      except APIError, e:
        self.send_response(e.code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": e.message}))
        return
    else:
      m = getattr(SimpleHTTPServer.SimpleHTTPRequestHandler, 'do_' + method)
      return m(self)

  def do_GET(self):
    return self.common('GET')

  def do_PUT(self):
    return self.common('PUT')

  def do_POST(self):
    return self.common('POST')

  def do_DELETE(self):
    return self.common('DELETE')

def main():
  server = BaseHTTPServer.HTTPServer

  # TODO: Remove this as the cgi-bin work was is unlikely to be checked in.
  # NOTE: cgi-bin requires /cgi-bin/<stuff>.py where as the other way uses
  # /api/<stuff> so the HTML/JS needs changing to switch between them.
  useCgiBinVersion = False
  if useCgiBinVersion:
    # This version uses cgi-bin instead of the custom handlers above.
    # cgi-bin:
    #    PRO: Allows you to edit the .py without restarting
    #         Can be re-used with Apache / another server.
    #    CON: Didn't work to well on a Linux server.
    #         Spawns a new Python process for each request.
    handler = CGIHTTPServer.CGIHTTPRequestHandler
  else:

    handler = RequestHandler
  handler.api = ApiHandler()
  server_address = ("", 8083)

  httpd = server(server_address, handler)
  httpd.serve_forever()

if __name__ == '__main__':
  main()

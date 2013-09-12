
import json
import urllib2

class GeometryReference:
  """A typed data-structre for storing the ID of a geometry object from the
  server."""
  def __init__(self, id, interface):
    if isinstance(id, GeometryReference):
      self.id = id.id
      self.interface = interface
      # The provided interface is ignored in favour of using the original one.
    else:
      assert isinstance(id, int)
      self.id = id
      self.interface = interface

  def __str__(self):
    return str(self.id)

class Interface:
  def __init__(self, apiBaseUri):
    """Constructs an interface onto the API provided at apiBaseUri.

    @param apiBaseUri: The base part of the URI of the web service.
    @param apiBaseUri: string
    """
    if not apiBaseUri.endswith('/'):
      apiBaseUri += '/'
    self.baseUri = apiBaseUri

  def login(self, username, password):
    raise NotImplementedError("Login/authentication services have not been "
                              "implemented at this time.")

  def createLine(self, points):
    """Creates a new line.

    @param points: A list containing (x,y) tuples.
    @param points: list
    """

    data = {
      "type": "LineString",
      "coordinates": points,
    }

    req = urllib2.Request(self.baseUri + 'geometry', data=json.dumps(data))
    r = urllib2.urlopen(req)
    data = json.load(r)
    return GeometryReference(data.get('databaseId'), self)

  def updateLine(self, objectId, points):
    """Updates a line with the new points given."""
    objectId = GeometryReference(objectId, self)

    # This works with just the points and is is by no means efficient.
    data = self.geometry(objectId)

    if data['type'] != 'LineString':
      raise TypeError("The geoJSON object is not a line.")

    data['coordinates'] = points

    request = urllib2.Request(self.baseUri + 'geometry/%d' % objectId.id,
                              data=json.dumps(data))
    request.add_header('Content-Type', 'application/json')
    request.get_method = lambda: 'PUT'
    r = urllib2.urlopen(request)
    data = json.load(r)
    return data

  def allGeometry(self):
    """Returns the geoJSON encoded representation of all the geometry on the
    server."""

    # TODO: This needs to handle pagination once that is implemented in the web
    # service.
    req = urllib2.Request(self.baseUri + 'geometry')
    r = urllib2.urlopen(req)

    data = json.load(r)

    # This ignore the "lastEditTime" and just works on the data.
    for item in data.get('geometry', []):
      yield item

    r.close()

  def geometry(self, objectId):
    """Returns the geoJSON encoded representation of a given geometry object on
    the server."""

    objectId = GeometryReference(objectId, self)
    req = urllib2.Request(self.baseUri + 'geometry/%d' % objectId.id)
    r = urllib2.urlopen(req)

    data = json.load(r)
    r.close()
    return data

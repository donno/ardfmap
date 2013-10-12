"""Provides an interface onto a database backend for storing the information.
"""

import datetime
import json
import sqlite3


def readIsoDate(dateString):
  fmt = '%Y-%m-%d %H:%M:%S'
  return datetime.datetime.strptime(dateString, fmt)

class Database:

  def addGeometry(self, geoJson):
    """Adds the geometry as specified by the geoJSON to the database.

    Returns the ID of the newly added geometry.
    """
    raise NotImplementedError('A derived class should provide this method.')

  def updateGeometry(self, databaseId, geoJson):
    """Updates the geometry to the corresponding ID in the database with
    geoJson."""
    raise NotImplementedError('A derived class should provide this method.')

  def deleteGeometry(self, databaseId):
    """Deletes the geometry with the corresponding ID in the database."""
    raise NotImplementedError('A derived class should provide this method.')

  def login(self, username, password):
    """Performs a user login.

    Returns None if it fails otherwise the user ID.
    """

    raise NotImplementedError('A derived class should provide this method.')

  def user(self, uid):
    """Returns the username and if the account is active."""
    raise NotImplementedError('A derived class should provide this method.')


class DatabaseSqlite(Database):
  """A database suitable for small deployment, development and testing."""

  def __init__(self):
    self._connection  = sqlite3.connect('ardfmap.db')

    c = self._connection.cursor()

    # Create the tables.
    query = """CREATE TABLE IF NOT EXISTS geometry(
      id INTEGER PRIMARY KEY ASC,
      who TEXT,
      'when' DATETIME DEFAULT CURRENT_TIMESTAMP,
      contents TEXT
      );"""

    c.execute(query)

    query = """CREATE TABLE IF NOT EXISTS sessions(
      id INTEGER PRIMARY KEY ASC,
      userid INTEGER,
      'when' DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(userid) REFERENCES user(id)
      );"""

    c.execute(query)

    query = """CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY ASC,
      username TEXT,
      email TEXT,
      password TEXT
      );"""
    c.execute(query)

    c.execute("INSERT INTO users(username, password) VALUES (?, ?)",
              ('testuser', 'password'))

    self._connection.commit()

  def close():
    self._connection.close()

  def login(self, username, password):
    c = self._connection.cursor()
    query = c.execute("SELECT id, username FROM users "
                      "WHERE username = '%s' AND password = '%s'" %
                      (username, password))
    row = query.fetchone()

    if row:
      # print the username
      userId = row[0]
      # Insert it into the session table and return the session id.
      return True
    else:
      return False
  def user(self, uid):
    """Returns the username and if the account is active."""
    c = self._connection.cursor()
    query = c.execute("SELECT username FROM users WHERE id = %d" % uid)
    row = query.fetchone()
    if row:
      return (row[0], True)
    else:
      return (None, False)

  def getGeometry(self, lastTime=None, geometryId=None):
    """Returns the geometry as geoJSON that is stored in the database.

    It also includes the last edit time, which can be used to request just the
    geometry from that date onwards next time.

    If geometryId is provided it will return a list with a single element which
    matches the given ID of an itme in the database.
    """
    c = self._connection.cursor()

    lastEditTime = datetime.datetime.min
    geometry = []
    if geometryId:
      assert not lastTime
      query = c.execute(
        'SELECT "when", contents, id, who FROM geometry WHERE id = %d' %
        geometryId)
    elif lastTime:
      lastTime = lastTime.replace('T', ' ')
      query = c.execute(
        'SELECT "when", contents, id, who FROM geometry WHERE "when" > "%s"' %
        lastTime)
    else:
      query = c.execute('SELECT "when", contents, id, who FROM geometry')
    for row in query:
      editTime = readIsoDate(row[0])
      if lastEditTime < editTime:
        lastEditTime = editTime

      # Important: This adds the "who", "serverId" properties into the objects.
      item = json.loads(row[1])
      r = row

      if 'properties' not in item:
        item['properties'] = {}

      item['properties'].update({
        'popupContent': "#%d: Last changed by %s on %s." % (r[2], r[3], r[0]),
        'serverID': r[2],
        'author': r[3],
        'lastChangeDate': r[0],
        })
      geometry.append(item)
    else:
      # No geometry, so we are all up to date.
      lastEditTime = datetime.datetime.utcnow()

    self._connection.commit()

    return {
      'lastEditTime': lastEditTime.isoformat(),
      'geometry': geometry,
      }

  def addGeometry(self, geoJson):
    """Adds the geometry as specified by the geoJSON to the database.

    Returns the ID of the newly added geometry.
    """
    c = self._connection.cursor()

    # TODO: Add the date it was created and who by...
    c.execute("INSERT INTO geometry(who, contents) VALUES ('NYI', '%s')" %
              json.dumps(geoJson))

    q = c.execute("SELECT last_insert_rowid()")
    databaseId = next(q)[0]

    self._connection.commit()
    return databaseId

  def updateGeometry(self, databaseId, geoJson):
    """Updates the geometry to the corresponding ID in the database with
    geoJson."""
    c = self._connection.cursor()

    # TODO: Add the date it was created and who by...
    c.execute("UPDATE geometry SET contents='%s' WHERE id=%d" %
              (json.dumps(geoJson), databaseId))
    self._connection.commit()

  def deleteGeometry(self, databaseId):
    """Deletes the geometry with the corresponding ID in the database."""
    c = self._connection.cursor()
    c.execute("DELETE FROM geometry WHERE id=%d" % databaseId)
    return True

def getDatabase():
  """Returns a database implementation."""
  return DatabaseSqlite()

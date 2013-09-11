ardfmap
=======

Amateur radio direction finding mapping system

A system designed for use with electronic foxhunting events and balloon chases.

## Getting started ##

Start the server by double clicking the server.py (or python server.py in a
terminal.

Visit http://localhost:8083 in your web browser.

## Architecture ##

### Server ###

The server componintent is currently pure Python using only Python standard
libaries, and hosts a HTTP server. IN addition to hosting the web client it
provides access to the database via a REST-style API.

At the moment it stores the data in a SQLite database to avoid the need of
installing database server like Postgres.

This design lends itself to making it easy to run it on the computers in car
during the hunts/chases. On the long term roadmap the plan is to also provide a
website that can be hosted on a public facing webserver (i.e through
Apache/lighttpd/ngnix/Cherokee) which can use Postgres the database backend
instead of SQLite.

### Client ###

Two clients are provided at this time, the web interface which utelises the
[Leaflet](http://leafletjs.com/) to provide an interactive client for humans in
their web browser and a CLI/API client for communicating with the server for
developing specialised agents.

## License ##

Copyright (c) 2013 Sean Donnellan

This software is licensed under the terms and conditions of the The MIT License
(MIT), see LICENSE for details.

This software the following third party software:
* [Leaflet](http://leafletjs.com) (c) 2013, Vladimir Agafonkin, CloudMade
* Leaflet.draw Copyright (c) 2013, Jacob Toye, Smartrak

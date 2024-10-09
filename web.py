import os
from importlib import import_module
import builtins

import flask
from rdflib.namespace import Namespace

import helpers
from escape_helpers import sparql_escape

# WSGI variable name used by the server
app = flask.Flask(__name__)

##################
## Vocabularies ##
##################
mu = Namespace('http://mu.semte.ch/vocabularies/')
mu_core = Namespace('http://mu.semte.ch/vocabularies/core/')
mu_ext = Namespace('http://mu.semte.ch/vocabularies/ext/')

SERVICE_RESOURCE_BASE = 'http://mu.semte.ch/services/'

builtins.app = app
builtins.helpers = helpers
builtins.sparql_escape = sparql_escape

import_module("ext.app.web")

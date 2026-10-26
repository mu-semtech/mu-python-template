import os
from importlib import import_module
import builtins
import threading
import warnings

import flask
from rdflib.namespace import Namespace

import helpers
from helpers import BaseHTTPException
from escape_helpers import sparql_escape

# WSGI variable name used by the server
app = flask.Flask(__name__)


@app.errorhandler(BaseHTTPException)
def handle_base_http_exception(exc):
    return exc.to_response()


# Flask 2.3 removed before_first_request, kept for services written against older template versions
if not hasattr(app, 'before_first_request'):
    def before_first_request(f):
        warnings.warn("app.before_first_request is deprecated, run startup code at import time of your web.py instead",
                      DeprecationWarning, stacklevel=2)
        lock = threading.Lock()
        done = False

        @app.before_request
        def run_once():
            nonlocal done
            if not done:
                with lock:
                    if not done:
                        f()
                        done = True
        return f
    app.before_first_request = before_first_request

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
builtins.BaseHTTPException = BaseHTTPException

# Import the app from the service consuming the template
app_file = os.environ.get('APP_ENTRYPOINT')
module_path = 'ext.app.{}'.format(app_file)
import_module(module_path)

#######################
## Start Application ##
#######################
if __name__ == '__main__':
    debug = os.environ.get('MODE') == "development"
    app.run(debug=debug, host='0.0.0.0', port=80)

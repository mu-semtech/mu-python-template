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

# Import the app from the service consuming the template
app_file = os.environ.get('APP_ENTRYPOINT')
try:
    module_path = 'ext.app.{}'.format(app_file)
    import_module(module_path)
except Exception:
    helpers.logger.exception('Exception raised when importing app code')

if os.environ.get('LOG_EXCEPTIONS'):
    @app.errorhandler(Exception)
    def handle_exception(e):
        helpers.logger.exception('Unhandled exception raised in route, returning 500')
        raise e

#######################
## Start Application ##
#######################
if __name__ == '__main__':
    debug = os.environ.get('MODE') == "development"
    app.run(debug=debug, host='0.0.0.0', port=80)

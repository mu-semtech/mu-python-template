import os
from functools import wraps
from importlib import import_module
import builtins
import threading

import flask
from flask import g
from rdflib.namespace import Namespace

import helpers
from helpers import BaseHTTPException, MU_AUTH_ALLOWED_GROUPS, MU_AUTH_USED_GROUPS
from escape_helpers import sparql_escape

# WSGI variable name used by the server
app = flask.Flask(__name__)


@app.errorhandler(BaseHTTPException)
def handle_base_http_exception(exc):
    return exc.to_response()


@app.after_request
def forward_mu_auth_response_headers(response):
    # Groups resolved by mu-authorization during a SPARQL query are forwarded to the client.
    # The last query executed within the request wins, None means the header is removed.
    if hasattr(g, 'mu_auth_allowed_groups'):
        if g.mu_auth_allowed_groups is not None:
            response.headers[MU_AUTH_ALLOWED_GROUPS] = g.mu_auth_allowed_groups
        elif MU_AUTH_ALLOWED_GROUPS in response.headers:
            del response.headers[MU_AUTH_ALLOWED_GROUPS]
    if hasattr(g, 'mu_auth_used_groups'):
        if g.mu_auth_used_groups is not None:
            response.headers[MU_AUTH_USED_GROUPS] = g.mu_auth_used_groups
        elif MU_AUTH_USED_GROUPS in response.headers:
            del response.headers[MU_AUTH_USED_GROUPS]
    return response


PRINT_DEPRECATION_WARNINGS = (os.environ.get('PRINT_DEPRECATION_WARNINGS') or 'true').lower() in ('true', 'yes', '1')
_printed_deprecation_warnings = set()


def warn_deprecated(key, message):
    """Log a deprecation warning once per key. Uses the template logger, as Python hides a DeprecationWarning
    raised outside of __main__ by default."""
    if PRINT_DEPRECATION_WARNINGS and key not in _printed_deprecation_warnings:
        _printed_deprecation_warnings.add(key)
        helpers.logger.warning("[DEPRECATION] " + message)


# Flask 2.3 removed before_first_request, kept for services written against older template versions
if not hasattr(app, 'before_first_request'):
    def before_first_request(f):
        warn_deprecated('before_first_request',
                        "app.before_first_request is deprecated, run startup code at import time of your web.py instead")
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

##############
## Builtins ##
##############
# Available without an import for backwards compatibility. Services importing helpers or sparql_escape
# themselves shadow these builtins, so only implicit usage logs a deprecation warning.
class _ImplicitHelpers:
    def __getattr__(self, name):
        warn_deprecated(f"helpers.{name}",
                        f"using helpers.{name} without an import is deprecated, add `import helpers` or `from helpers import {name}` to your service")
        return getattr(helpers, name)

    def __setattr__(self, name, value):
        setattr(helpers, name, value)


@wraps(sparql_escape)
def _implicit_sparql_escape(*args, **kwargs):
    warn_deprecated('sparql_escape',
                    "using sparql_escape without an import is deprecated, add `from escape_helpers import sparql_escape` to your service")
    return sparql_escape(*args, **kwargs)


builtins.app = app
builtins.helpers = _ImplicitHelpers()
builtins.sparql_escape = _implicit_sparql_escape

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

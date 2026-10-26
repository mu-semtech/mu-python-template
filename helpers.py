import copy
import uuid
import datetime
import logging
import os
import sys
from flask import jsonify, request, has_request_context
from rdflib.namespace import DC
from escape_helpers import sparql_escape
from SPARQLWrapper import SPARQLWrapper, JSON

"""
The template provides the user with several helper methods. They aim to give you a step ahead for:

- logging
- JSONAPI-compliancy
- SPARQL querying

The below helpers can be imported from the `helpers` module. For example:
```py
from helpers import *
```

Available functions:
"""

MU_APPLICATION_GRAPH = os.environ.get('MU_APPLICATION_GRAPH')
ALLOW_MU_AUTH_SUDO = os.environ.get("ALLOW_MU_AUTH_SUDO") in ['true', 'True', 'yes']
DEFAULT_MU_AUTH_SCOPE = os.environ.get("DEFAULT_MU_AUTH_SCOPE")

# TODO: Figure out how logging works when production uses multiple workers
log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
log_dir = os.getenv('LOG_DIR', '/logs')
if not os.path.exists(log_dir): os.makedirs(log_dir)
logger = logging.getLogger('MU_PYTHON_TEMPLATE_LOGGER')
logger.setLevel(log_levels.get(os.environ.get('LOG_LEVEL').upper()))
fileHandler = logging.FileHandler("{0}/{1}.log".format(log_dir, 'logs'))
logger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler(stream=sys.stdout)# or stderr?
logger.addHandler(consoleHandler)

LOG_SPARQL_ALL_VAR = os.environ.get('LOG_SPARQL_ALL')
LOG_SPARQL_QUERIES = os.environ.get(
    'LOG_SPARQL_QUERIES',
    default=LOG_SPARQL_ALL_VAR
).lower() == 'true'
LOG_SPARQL_UPDATES = os.environ.get(
    'LOG_SPARQL_UPDATES',
    default=LOG_SPARQL_ALL_VAR
).lower() == 'true'

def generate_uuid():
    """Generates a random unique user id (UUID) based on the host ID and current time"""
    return str(uuid.uuid1())


def log(msg, *args, **kwargs):
    """
    Write a log message to the log file.

    Works exactly the same as the logging.info (https://docs.python.org/3/library/logging.html#logging.info) method from pythons' logging module.
    Logs are written to the /logs directory in the docker container.

    Note that the `helpers` module also exposes `logger`, which is the logger instance (https://docs.python.org/3/library/logging.html#logger-objects)
    used by the template. The methods provided by this instance can be used for more fine-grained logging.
    """
    return logger.info(msg, *args, **kwargs)

class BaseHTTPException(Exception):
    """
    Exception resulting in a JSONAPI compliant error response with the given status code (400 by default).

    Raise it from anywhere in a request handler instead of returning `error(...)`. The template registers an
    error handler that turns it into a response.
    The keyword arguments are the members of JSONAPI error objects: https://jsonapi.org/format/#error-objects
    """
    def __init__(self, status_code=400, detail=None, headers=None, id=None, links=None,
                 code=None, title=None, source=None, meta=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        self.error_members = {key: value for key, value in dict(
            id=id, links=links, code=code, title=title, source=source, meta=meta
        ).items() if value is not None}

    def to_response(self):
        response = error(self.detail, self.status_code, **self.error_members)
        response.headers.update(self.headers or {})
        return response


def error(msg, status=400, **kwargs):
    """
    Returns a Response object containing a JSONAPI compliant error response with the given status code (400 by default).

    Response object documentation: https://flask.palletsprojects.com/en/1.1.x/api/#response-objects
    The kwargs can be any other key supported by JSONAPI error objects: https://jsonapi.org/format/#error-objects

    Alternatively, raise a `BaseHTTPException` to abort request handling with an error response.
    """
    error_obj = kwargs
    error_obj["detail"] = msg
    error_obj["status"] = status
    response = jsonify({
        "errors": [error_obj]
    })
    response.status_code = error_obj["status"]
    response.headers["Content-Type"] = "application/vnd.api+json"
    return response



def session_id_header(request):
    """Returns the MU-SESSION-ID header from the given requests' headers"""
    return request.headers.get('MU-SESSION-ID')


def rewrite_url_header(request):
    """Returns the X-REWRITE-URL header from the given requests' headers"""
    return request.headers.get('X-REWRITE-URL')


def validate_json_api_content_type(request):
    """Validate whether the request contains the JSONAPI content-type header (application/vnd.api+json). Returns a 404 otherwise"""
    content_type = request.content_type or ""
    if "application/vnd.api+json" not in content_type:
        return error("Content-Type must be application/vnd.api+json instead of " +
                     content_type)


def validate_resource_type(expected_type, data):
    """Validate whether the type specified in the JSON data is equal to the expected type. Returns a `409` otherwise."""
    if data['type'] != expected_type:
        return error("Incorrect type. Type must be " + str(expected_type) +
                     ", instead of " + str(data['type']) + ".", 409)

def build_sparql_query():
    sparql_query = SPARQLWrapper(os.environ.get('MU_SPARQL_ENDPOINT'), returnFormat=JSON)
    if os.environ.get('MU_SPARQL_TIMEOUT'):
        timeout = int(os.environ.get('MU_SPARQL_TIMEOUT'))
        sparql_query.setTimeout(timeout)
    return sparql_query

def build_sparql_update():
    sparql_update = SPARQLWrapper(os.environ.get('MU_SPARQL_UPDATEPOINT'), returnFormat=JSON)
    sparql_update.method = 'POST'
    if os.environ.get('MU_SPARQL_TIMEOUT'):
        timeout = int(os.environ.get('MU_SPARQL_TIMEOUT'))
        sparql_update.setTimeout(timeout)
    return sparql_update

# Shared instances holding the connection configuration. `query` and `update` execute on a copy,
# so changes made to these by a service (e.g. a timeout or custom headers) still apply to every query.
sparqlQuery = build_sparql_query()
sparqlUpdate = build_sparql_update()

MU_HEADERS = [
    "MU-SESSION-ID",
    "MU-CALL-ID",
    "MU-AUTH-ALLOWED-GROUPS",
    "MU-AUTH-USED-GROUPS"
]

def set_sparql_interface_headers(sparql_interface, sudo=False, scope=None):
    for header in MU_HEADERS:
        if has_request_context() and header in request.headers:
            sparql_interface.customHttpHeaders[header] = request.headers[header]
        else: # Make sure headers used for a previous query are cleared
            if header in sparql_interface.customHttpHeaders:
                del sparql_interface.customHttpHeaders[header]
    if sudo:
        if ALLOW_MU_AUTH_SUDO:
            sparql_interface.customHttpHeaders["mu-auth-sudo"] = "true"
        else:
            raise BaseHTTPException(403, "tried to execute sudo query without explicit permission on container level")

    if scope:
        sparql_interface.customHttpHeaders["mu-auth-scope"] = scope
    elif DEFAULT_MU_AUTH_SCOPE:
        sparql_interface.customHttpHeaders["mu-auth-scope"] = DEFAULT_MU_AUTH_SCOPE


def query(the_query: str, *, sudo: bool = False, scope: str | None = None):
    """Execute the given SPARQL query (select/ask/construct) on the triplestore and returns the results in the given return Format (JSON by default)."""
    # we're editing properties of sparql_interface, if this is done by multiple worker threads, the behavior is undefined, better use a copy
    sparql_interface = copy.deepcopy(sparqlQuery)

    set_sparql_interface_headers(sparql_interface, sudo=sudo, scope=scope)

    sparql_interface.setQuery(the_query)
    if LOG_SPARQL_QUERIES:
        log("Execute query: \n" + the_query)
    try:
        return sparql_interface.query().convert()
    except Exception as e:
        log("Failed Query: \n" + the_query)
        raise e


def update(the_query: str, *, sudo: bool = False, scope: str | None = None):
    """Execute the given update SPARQL query on the triplestore. If the given query is not an update query, nothing happens."""
    # we're editing properties of sparql_interface, if this is done by multiple worker threads, the behavior is undefined, better use a copy
    sparql_interface = copy.deepcopy(sparqlUpdate)

    set_sparql_interface_headers(sparql_interface, sudo=sudo, scope=scope)

    sparql_interface.setQuery(the_query)
    if sparql_interface.isSparqlUpdateRequest():
        if LOG_SPARQL_UPDATES:
            log("Execute query: \n" + the_query)
        try:
            sparql_interface.query()
        except Exception as e:
            log("Failed Query: \n" + the_query)
            raise e


def update_modified(subject, modified=None):
    """(DEPRECATED) Executes a SPARQL query to update the modification date of the given subject URI (string).
     The default date is now."""
    if modified is None:
        modified = datetime.datetime.now()
    query = " WITH <%s> " % MU_APPLICATION_GRAPH
    query += " DELETE {"
    query += "   < %s > < %s > %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += " }"
    query += " WHERE {"
    query += "   <%s> <%s> %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += " }"
    update(query)

    query = " INSERT DATA {"
    query += "   GRAPH <%s> {" % MU_APPLICATION_GRAPH
    query += "     <%s> <%s> %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += "   }"
    query += " }"
    update(query)

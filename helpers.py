import uuid
import datetime
import logging
import os
import sys
from flask import jsonify, request
from rdflib.namespace import DC
from escape_helpers import sparql_escape
from SPARQLWrapper import SPARQLWrapper, JSON

MU_APPLICATION_GRAPH = os.environ.get('MU_APPLICATION_GRAPH')

# TODO: Figure out how logging works when production uses multiple workers
log_levels = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
log_dir = '/logs'
if not os.path.exists(log_dir): os.makedirs(log_dir)
logger = logging.getLogger('MU_PYTHON_TEMPLATE_LOGGER')
logger.setLevel(log_levels.get(os.environ.get('LOG_LEVEL').upper()))
fileHandler = logging.FileHandler("{0}/{1}.log".format(log_dir, 'logs'))
logger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler(stream=sys.stdout)# or stderr?
logger.addHandler(consoleHandler)

def generate_uuid():
    """Generates a unique user id based the host ID and current time"""
    return str(uuid.uuid1())


def log(msg, *args, **kwargs):
    """write a log message to the log file. Logs are written to the `/logs`
     directory in the docker container."""
    return logger.info(msg, *args, **kwargs)


def session_id_header(request):
    """returns the MU-SESSION-ID header from the given request"""
    return request.headers.get('MU-SESSION-ID')


def rewrite_url_header(request):
    """return the X-REWRITE-URL header from the given request"""
    return request.headers.get('X-REWRITE-URL')


def error(title, status="400", detail=None, id=None, links=None, code=None, source=None, meta=None):
    """Returns a Response object containing a JSONAPI compliant error response
    with the given status code (400 by default).

    See https://jsonapi.org/format/#error-objects for desired structure."""
    error_obj = {
        "title": title,
        "status": status
    }
    if detail is not None: error_obj["detail"] = detail
    if id is not None: error_obj["id"] = id
    if links is not None: error_obj["links"] = links
    if code is not None: error_obj["code"] = code
    if source is not None: error_obj["source"] = source
    if meta is not None: error_obj["meta"] = meta
    response = jsonify({
        "errors": [error_obj]
    })
    response.status_code = error_obj["status"]
    response.headers["Content-Type"] = "application/vnd.api+json"
    return response


def validate_json_api_content_type(request):
    """Validate whether the content type of the request is application/vnd.api+json."""
    if "application/vnd.api+json" not in request.content_type:
        return error("Content-Type must be application/vnd.api+json instead of " +
                     request.content_type)


def validate_resource_type(expected_type, data):
    """Validate whether the type specified in the JSON data is equal to the expected type.
    Returns a `409` otherwise."""
    if data['type'] is not expected_type:
        return error("Incorrect type. Type must be " + str(expected_type) +
                     ", instead of " + str(data['type']) + ".", 409)


sparqlQuery = SPARQLWrapper(os.environ.get('MU_SPARQL_ENDPOINT'), returnFormat=JSON)
sparqlUpdate = SPARQLWrapper(os.environ.get('MU_SPARQL_UPDATEPOINT'), returnFormat=JSON)
sparqlUpdate.method = 'POST'
if os.environ.get('MU_SPARQL_TIMEOUT'):
    timeout = int(os.environ.get('MU_SPARQL_TIMEOUT'))
    sparqlQuery.setTimeout(timeout)
    sparqlUpdate.setTimeout(timeout)

MU_HEADERS = [
    "MU-SESSION-ID",
    "MU-CALL-ID",
    "MU-AUTH-ALLOWED-GROUPS",
    "MU-AUTH-USED-GROUPS"
]

def query(the_query):
    """Execute the given SPARQL query (select/ask/construct)on the tripple store and returns the results
    in the given returnFormat (JSON by default)."""
    log("execute query: \n" + the_query)
    for header in MU_HEADERS:
        if header in request.headers:
            sparqlQuery.customHttpHeaders[header] = request.headers[header]
        else: # Make sure headers used for a previous query are cleared
            if header in sparqlQuery.customHttpHeaders:
                del sparqlQuery.customHttpHeaders[header]
    sparqlQuery.setQuery(the_query)
    return sparqlQuery.query().convert()


def update(the_query):
    """Execute the given update SPARQL query on the tripple store,
    if the given query is no update query, nothing happens."""
    for header in MU_HEADERS:
        if header in request.headers:
            sparqlUpdate.customHttpHeaders[header] = request.headers[header]
        else: # Make sure headers used for a previous query are cleared
            if header in sparqlUpdate.customHttpHeaders:
                del sparqlUpdate.customHttpHeaders[header]
    sparqlUpdate.setQuery(the_query)
    if sparqlUpdate.isSparqlUpdateRequest():
        sparqlUpdate.query()


def update_modified(subject, modified=datetime.datetime.now()):
    """Executes a SPARQL query to update the modification date of the given subject URI (string).
     The default date is now."""
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

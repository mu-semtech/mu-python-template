import uuid
import datetime
import logging
import os
import sys
from web import graph
from flask import jsonify
from rdflib.namespace import DC
from escape_helpers import sparql_escape
from SPARQLWrapper import SPARQLWrapper, JSON


def generate_uuid():
    """Generates a unique user id based the host ID and current time"""
    return str(uuid.uuid1())


log_levels = {'DEBUG': logging.DEBUG,
              'INFO': logging.INFO,
              'WARNING': logging.WARNING,
              'ERROR': logging.ERROR,
              'CRITICAL': logging.CRITICAL}
log_dir = '/logs'
if not os.path.exists(log_dir): os.makedirs(log_dir)
thelogger = logging.getLogger('')
thelogger.setLevel(log_levels.get(os.environ.get('LOG_LEVEL').upper()))
fileHandler = logging.FileHandler("{0}/{1}.log".format(log_dir, 'logs'))
thelogger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler(stream=sys.stdout)# or stderr?
thelogger.addHandler(consoleHandler)

def log(msg):
    """write a log message to the log file. Logs are written to the `/logs`
     directory in the docker container."""
    thelogger.info(msg)


def session_id_header(request):
    """returns the HTTP_MU_SESSION_ID header from the given request"""
    return request.args.get('HTTP_MU_SESSION_ID')


def rewrite_url_header(request):
    """return the HTTP_X_REWRTITE_URL header from the given request"""
    return request.args.get('HTTP_X_REWRITE_URL')


def error(msg, status=400):
    """Returns a JSONAPI compliant error response with the given status code (400 by default)."""
    response = jsonify({'message': msg})
    response.status_code = status
    return response


def validate_json_api_content_type(request):
    """Validate whether the content type of the request is application/vnd.api+json."""
    if "/^application/vnd.api+json" not in request.args.get('CONTENT_TYPE'):
        return error("Content-Type must be application/vnd.api+json instead of" +
                     request.args.get('CONTENT_TYPE'))


def validate_resource_type(expected_type, data):
    """Validate whether the type specified in the JSON data is equal to the expected type.
    Returns a `409` otherwise."""
    if data['type'] is not expected_type:
        return error("Incorrect type. Type must be " + str(expected_type) +
                     ", instead of " + str(data['type']) + ".", 409)


sparqlQuery = SPARQLWrapper(os.environ.get('MU_SPARQL_ENDPOINT'), returnFormat=JSON)
sparqlUpdate = SPARQLWrapper(os.environ.get('MU_SPARQL_UPDATEPOINT'), returnFormat=JSON)
sparqlUpdate.method = 'POST'

def query(the_query):
    """Execute the given SPARQL query (select/ask/construct)on the tripple store and returns the results
    in the given returnFormat (JSON by default)."""
    log("execute query: \n" + the_query)
    sparqlQuery.setQuery(the_query)
    return sparqlQuery.query().convert()


def update(the_query):
    """Execute the given update SPARQL query on the tripple store,
    if the given query is no update query, nothing happens."""
    sparqlUpdate.setQuery(the_query)
    if sparqlUpdate.isSparqlUpdateRequest():
        sparqlUpdate.query()


def update_modified(subject, modified=datetime.datetime.now()):
    """Executes a SPARQL query to update the modification date of the given subject URI (string).
     The default date is now."""
    query = " WITH <%s> " % graph
    query += " DELETE {"
    query += "   < %s > < %s > %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += " }"
    query += " WHERE {"
    query += "   <%s> <%s> %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += " }"
    update(query)

    query = " INSERT DATA {"
    query += "   GRAPH <%s> {" % graph
    query += "     <%s> <%s> %s ." % (subject, DC.Modified, sparql_escape(modified))
    query += "   }"
    query += " }"
    update(query)


def verify_string_parameter(parameter):
    if parameter and type(parameter) is str:
        if "insert" in parameter.lower(): return error("unauthorized insert in string parameter")
        if "delete" in parameter.lower(): return error("unauthorized delete in string parameter")
        if "load" in parameter.lower(): return error("unauthorized load in string parameter")
        if "clear" in parameter.lower(): return error("unauthorized clear in string parameter")
        if "create" in parameter.lower(): return error("unauthorized create in string parameter")
        if "drop" in parameter.lower(): return error("unauthorized drop in string parameter")
        if "copy" in parameter.lower(): return error("unauthorized copy in string parameter")
        if "move" in parameter.lower(): return error("unauthorized move in string parameter")
        if "add" in parameter.lower(): return error("unauthorized add in string parameter")

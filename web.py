import flask
import os
import helpers
from rdflib.namespace import Namespace
import json

app = flask.Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello world'


@app.route('/example')
def query():
    """Example query: Returns all the triples in the application graph in a JSON
    format."""
    q =  "SELECT *"
    q += "WHERE{"
    q += "  GRAPH <http://mu.semte.ch/application> {"
    q += "    ?s ?p ?o"
    q += "  }"
    q += "}"
    return json.dumps(helpers.query(q))


##################
## Vocabularies ##
##################
mu = Namespace('http://mu.semte.ch/vocabularies/')
mu_core = Namespace('http://mu.semte.ch/vocabularies/core/')
mu_ext = Namespace('http://mu.semte.ch/vocabularies/ext/')

graph = os.environ.get('MU_APPLICATION_GRAPH')
SERVICE_RESOURCE_BASE = 'http://mu.semte.ch/services/'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
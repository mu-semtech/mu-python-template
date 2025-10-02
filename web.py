import os
from importlib import import_module
import builtins

from fastapi import FastAPI
from fastapi.responses import Response
from jsonapi_pydantic.v1_0 import Error, TopLevel
from starlette.exceptions import HTTPException as StarletteHTTPException
from rdflib.namespace import Namespace

import helpers
from escape_helpers import sparql_escape

# WSGI variable name used by the server
app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    error_object = TopLevel(
        errors=[
            Error(
                detail=str(exc.detail),
                status=exc.status_code
            )
        ]
    )
    return Response(
        content=error_object.model_dump_json(), status_code=exc.status_code, headers={
            'Content-Type': 'application/vnd.api+json'
        }
    )

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
module_path = 'ext.app.{}'.format(app_file)
import_module(module_path)

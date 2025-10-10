import os
from importlib import import_module
import builtins

from fastapi import FastAPI, APIRouter
from typing import Mapping, Any
from fastapi.responses import Response
from jsonapi_pydantic.v1_0 import Error, TopLevel, Meta, Source, ErrorLinks
from starlette.exceptions import HTTPException as StarletteHTTPException
from rdflib.namespace import Namespace

import helpers
from escape_helpers import sparql_escape

# WSGI variable name used by the server
app = FastAPI()


class BaseHTTPException(StarletteHTTPException):
    """
    Implementation of JSONAPI compliant error responses with provided status code (400 by default) using the
    default FASTAPI Error mechanism

    Response object documentation: https://flask.palletsprojects.com/en/1.1.x/api/#response-objects
    The kwargs can be any other key supported by JSONAPI error objects: https://jsonapi.org/format/#error-objects
    """

    def __init__(
            self,
            status_code: int=400,
            detail: str | None = None,
            headers: Mapping[str, str] | None = None,
            id: Any | None = None,
            links: ErrorLinks | None = None,
            code: str | None = None,
            title: str | None = None,
            source: Source | None = None,
            meta: Meta | None = None
    ) -> None:
        super().__init__(status_code, detail, headers)
        self.id = id
        self.links = links
        self.code = code
        self.title = title
        self.source = source
        self.meta = meta


@app.exception_handler(BaseHTTPException)
async def http_exception_handler(request, exc):
    error_object = TopLevel(
        errors=[
            Error(
                detail=str(exc.detail),
                status=exc.status_code,
                id=exc.id,
                links=exc.links,
                code=exc.code,
                title=exc.title,
                source=exc.source,
                meta=exc.meta
            )
        ]
    )
    headers = exc.headers or {}
    headers['Content-Type'] = 'application/vnd.api+json'
    return Response(
        content=error_object.model_dump_json(), status_code=exc.status_code, headers=headers
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
builtins.BaseHTTPException = BaseHTTPException

# Import the app from the service consuming the template
app_file = os.environ.get('APP_ENTRYPOINT')
module_path = 'ext.app.{}'.format(app_file)
package = import_module(module_path)
for value in package.__dict__.values():
    if isinstance(value, APIRouter):
        app.include_router(value)

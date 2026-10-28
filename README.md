# Mu Python template

Template for [mu.semte.ch](http://mu.semte.ch)-microservices written in Python3.13. Based on the [Flask](https://palletsprojects.com/p/flask/)-framework.

## Quickstart

Create a `Dockerfile` which extends the `semtech/mu-python-template`-image and set a maintainer.
```docker
FROM semtech/mu-python-template:2.0.0-beta.3
LABEL maintainer="maintainer@example.com"
```

Create a `web.py` entrypoint-file. (naming of the entrypoint can be configured through `APP_ENTRYPOINT`)
```python
@app.route("/hello")
def hello():
    return "Hello from the mu-python-template!"
```

Build the Docker-image for your service
```sh
docker build -t my-python-service .
```

Run your service
```sh
docker run -p 8080:80
```

You now should be able to access your service's endpoint
```sh
curl localhost:8080/hello
```

## Developing a microservice using the template

### Dependencies

If your service needs external libraries other than the ones already provided by the template (Flask, SPARQLWrapper and rdflib), you can specify those in a [`requirements.txt`](https://pip.pypa.io/en/stable/reference/requirements-file-format/)-file. The template will take care of installing them when you build your Docker image and when you boot the template in development mode for the first time.

Some python dependencies depend on C/C++ libraries which are not present in the image (e.g. libgeos for a package such as shapely). To install those, add an `on-build.sh` file to your service, in line with the `on-build.sh` support of the mu-javascript-template and mu-ruby-template. It is executed before the python dependencies are installed. E.g.:
```bash
#!/bin/sh
apt-get update && apt-get install -y libgeos-dev
```

### Development mode

By leveraging Dockers' [bind-mount](https://docs.docker.com/storage/bind-mounts/), you can mount your application code into an existing service image. This spares you from building a new image to test each change. Just mount your services' folder to the containers' `/app`. On top of that, you can configure the environment variable `MODE` to `development`. That enables live-reloading of the server, so it immediately updates when you save a file.  

example docker-compose parameters:
```yml
    environment:
      MODE: "development"
    volumes:
      - /home/my/code/my-python-service:/app
```

By default, development mode runs Flask's development server, which shows an interactive debugger on errors. Set `DEV_SERVER` to `gunicorn` to run the production server with live-reloading instead, e.g. to test behaviour with multiple workers or threads.

### Helper methods
<a id="helpers.generate_uuid"></a>

#### `generate_uuid`

```python
def generate_uuid()
```

> Generates a random unique user id (UUID) based on the host ID and current time

<a id="helpers.log"></a>

#### `log`

```python
def log(msg, *args, **kwargs)
```

> Write a log message.
> 
> Works exactly the same as the logging.info (https://docs.python.org/3/library/logging.html#logging.info) method from pythons' logging module.
> Logs are written to stdout of the container (e.g. visible via `docker logs`).
> 
> Note that the `helpers` module also exposes `logger`, which is the logger instance (https://docs.python.org/3/library/logging.html#logger-objects) 
> used by the template. The methods provided by this instance can be used for more fine-grained logging.

<a id="helpers.BaseHTTPException"></a>

#### `BaseHTTPException` Objects

```python
class BaseHTTPException(Exception)
```

> Exception resulting in a JSONAPI compliant error response with the given status code (400 by default).
> 
> Raise it from anywhere in a request handler instead of returning `error(...)`. The template registers an
> error handler that turns it into a response.
> The keyword arguments are the members of JSONAPI error objects: https://jsonapi.org/format/#error-objects

<a id="helpers.error"></a>

#### `error`

```python
def error(msg, status=400, **kwargs)
```

> Returns a Response object containing a JSONAPI compliant error response with the given status code (400 by default).
> 
> Response object documentation: https://flask.palletsprojects.com/en/stable/api/#response-objects
> The kwargs can be any other key supported by JSONAPI error objects: https://jsonapi.org/format/#error-objects
> 
> Alternatively, raise a `BaseHTTPException` to abort request handling with an error response.

<a id="helpers.session_id_header"></a>

#### `session_id_header`

```python
def session_id_header(request)
```

> Returns the MU-SESSION-ID header from the given requests' headers

<a id="helpers.rewrite_url_header"></a>

#### `rewrite_url_header`

```python
def rewrite_url_header(request)
```

> Returns the X-REWRITE-URL header from the given requests' headers

<a id="helpers.validate_json_api_content_type"></a>

#### `validate_json_api_content_type`

```python
def validate_json_api_content_type(request)
```

> Validate whether the request contains the JSONAPI content-type header (application/vnd.api+json). Returns a 404 otherwise

<a id="helpers.validate_resource_type"></a>

#### `validate_resource_type`

```python
def validate_resource_type(expected_type, data)
```

> Validate whether the type specified in the JSON data is equal to the expected type. Returns a `409` otherwise.

<a id="helpers.query"></a>

#### `query`

```python
def query(the_query: str, *, sudo: bool = False, scope: str | None = None)
```

> Execute the given SPARQL query (select/ask/construct) on the triplestore and returns the results in the given return Format (JSON by default).
> 
> Advanced options:
> - sudo: perform a sudo query, ignoring the groups of the originating request. Only allowed if the environment variable `ALLOW_MU_AUTH_SUDO` is set to `true` (or `True` or `yes`)
> - scope: a scope string to use when executing this query. If left as None, the default scope of `DEFAULT_MU_AUTH_SCOPE` is used if any. Otherwise, no scope is used in the query

<a id="helpers.update"></a>

#### `update`

```python
def update(the_query: str, *, sudo: bool = False, scope: str | None = None)
```

> Execute the given update SPARQL query on the triplestore. If the given query is not an update query, nothing happens.
> 
> Advanced options:
> - sudo: perform a sudo query, ignoring the groups of the originating request. Only allowed if the environment variable `ALLOW_MU_AUTH_SUDO` is set to `true` (or `True` or `yes`)
> - scope: a scope string to use when executing this query. If left as None, the default scope of `DEFAULT_MU_AUTH_SCOPE` is used if any. Otherwise, no scope is used in the query

<a id="helpers.update_modified"></a>

#### `update_modified`

```python
def update_modified(subject, modified=None)
```

> (DEPRECATED) Executes a SPARQL query to update the modification date of the given subject URI (string).
> The default date is now.

<a id="escape_helpers.sparql_escape_string"></a>

#### `sparql_escape_string`

```python
def sparql_escape_string(obj)
```

> Converts the given string to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape_datetime"></a>

#### `sparql_escape_datetime`

```python
def sparql_escape_datetime(obj)
```

> Converts the given datetime to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape_date"></a>

#### `sparql_escape_date`

```python
def sparql_escape_date(obj)
```

> Converts the given date to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape_time"></a>

#### `sparql_escape_time`

```python
def sparql_escape_time(obj)
```

> Converts the given time to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape_int"></a>

#### `sparql_escape_int`

```python
def sparql_escape_int(obj)
```

> Converts the given int to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape_float"></a>

#### `sparql_escape_float`

```python
def sparql_escape_float(obj)
```

> Converts the given float to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape_bool"></a>

#### `sparql_escape_bool`

```python
def sparql_escape_bool(obj)
```

> Converts the given bool to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape_uri"></a>

#### `sparql_escape_uri`

```python
def sparql_escape_uri(obj)
```

> Converts the given URI to a SPARQL-safe RDF object string with the right RDF-datatype.

<a id="escape_helpers.sparql_escape"></a>

#### `sparql_escape`

```python
def sparql_escape(obj)
```

> Converts the given object to a SPARQL-safe RDF object string with the right RDF-datatype. 
> 
> These functions should be used especially when inserting user-input to avoid SPARQL-injection.
> Separate functions are available for different python datatypes.
> The `sparql_escape` function however can automatically select the right method to use, for the following Python datatypes:
> 
> - `str`
> - `int`
> - `float`
> - `datetime.datetime`
> - `datetime.date`
> - `datetime.time`
> - `boolean`
> 
> The `sparql_escape_uri`-function can be used for escaping URI's.

### Error handling

A request handler can return a JSONAPI error response built with `error(...)`, or raise a `BaseHTTPException` (available without an import, like `app`). The template turns the exception into the same JSONAPI error response.
```python
@app.route("/hello/<name>")
def hello(name):
    if name == "world":
        raise BaseHTTPException(418, "The world is not a person", title="Invalid name")
    return f"Hello {name}!"
```

### Running code on startup

Code at the top level of your `web.py` runs when the service boots, before any requests are handled. `@app.before_first_request` was removed from Flask, the template still provides it for backwards compatibility, but it is deprecated.

The SPARQL helpers can be used outside of a request (e.g. on startup or in a background thread). Headers of the original request are passed on only when the helper is used within a request.

A cross-template feature to wait for the stack (database, migrations, ...) to be ready is planned. Until then, a simplistic check can look like this:

```python
import time
from helpers import query, log

def wait_for_triplestore():
    while True:
        try:
            query("ASK { ?s ?p ?o }")
            break
        except Exception:
            log("Triplestore not live yet, retrying...")
            time.sleep(1)
    log("Triplestore ready!")

wait_for_triplestore()
```

### Writing SPARQL Queries

The template itself is unopinionated when it comes to constructing SPARQL-queries. However, since Python's most common string formatting methods aren't a great fit for SPARQL queries, we hereby want to provide an example on how to construct a query based on [template strings](https://docs.python.org/3.8/library/string.html#template-strings) while keeping things readable.

```py
from string import Template
from helpers import query
from escape_helpers import sparql_escape_uri

my_person = "http://example.com/me"
query_template = Template("""
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?name
WHERE {
    $person a foaf:Person ;
        foaf:firstName ?name .
}
""")
query_string = query_template.substitute(person=sparql_escape_uri(my_person))
query_result = query(query_string)
```

## Deployment

Example snippet for adding a service to a docker-compose stack:
```yml
my-python:
  image: my-python-service
  environment:
    LOG_LEVEL: "debug"
```

### Environment variables
#### General

- `LOG_LEVEL` takes the same options as defined in the Python [logging](https://docs.python.org/3/library/logging.html#logging-levels) module.

- `MODE` to specify the deployment mode. Can be `development` as well as `production`. Defaults to `production`

- `DEV_SERVER` the server used in development mode. Can be `flask` (default) or `gunicorn`.

- `MU_SPARQL_ENDPOINT` is used to configure the SPARQL endpoint.

  - By default this is set to `http://database:8890/sparql`. In that case the triple store used in the backend should be linked to the microservice container as `database`.


- `MU_APPLICATION_GRAPH` specifies the graph in the triple store the microservice will work in.

  - By default this is set to `http://mu.semte.ch/application`. The graph name can be used in the service via `settings.graph`.


- `MU_SPARQL_TIMEOUT` is used to configure the timeout (in seconds) for SPARQL queries.

#### mu-authorization
- `ALLOW_MU_AUTH_SUDO`: allow queries with `sudo=True`, which bypass the access rights of the user making the request. Accepts `true`/`True`/`yes`. Defaults to not allowed.

- `DEFAULT_MU_AUTH_SCOPE`: the scope used for queries which don't provide their own `scope`. Defaults to no scope.

#### SPARQL Query Logging
- `LOG_SPARQL_ALL`: Log *all* executed queries, read as well as update (default `True`)

- `LOG_SPARQL_QUERIES`: Log *read* queries (default: `undefined`). Overrules `LOG_SPARQL_ALL`

- `LOG_SPARQL_UPDATES`: Log *update* queries (default `undefined`). Overrules `LOG_SPARQL_ALL`.

The string "true", ignoring casing, is considered `True`.  All other values are considered `False`.

#### Gunicorn configuration
The service runs with [Gunicorn](https://gunicorn.org/) using [Uvicorn](https://www.uvicorn.org/) workers. The number of worker processes is configured via `WEB_CONCURRENCY` (default `1` in this template). See `gunicorn_conf.py` for other supported environment variables (`HOST`, `PORT`, `BIND`, `LOG_LEVEL`).

Each worker handles one request at a time, like earlier versions of the template. Other [gunicorn settings](https://docs.gunicorn.org/en/stable/settings.html) can be passed through `GUNICORN_CMD_ARGS`, e.g. `"--threads 4"` to handle 4 requests concurrently per worker. The template helpers are thread-safe, but make sure the code of your service is before increasing this.

### Production

For hosting the app in a production setting, the template runs a Gunicorn server with Uvicorn workers, configured via the environment variables described above (see also `gunicorn_conf.py`).

## Other

### Reassigning `app`
In regular Flask applications (e.g. those not run within this template) you are required to define `app` by using `app = Flask(__name__)` or similar. This does *not* need to be done in your web.py, as this is handled by the microservice architecture/template. Redefining this may cause `The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.` to be thrown on your routes, which can be luckily be fixed by simply removing the previously mentioned `app = ...` line.

### Upgrading from earlier versions
- The template is based on Python 3.13 (was 3.8) and recent versions of Flask, rdflib and SPARQLWrapper. Pinned dependencies of your service might need an update.
- The meinheld server was replaced by gunicorn with Uvicorn workers, see [Gunicorn configuration](#gunicorn-configuration).
- The base image is `python:3.13-slim` instead of the full python image. gcc and g++ are available, other system libraries can be installed with an [`on-build.sh`](#dependencies).
- `query` and `update` execute on a copy of `helpers.sparqlQuery` and `helpers.sparqlUpdate`, making them thread-safe. Configuration set on those objects (e.g. a timeout or custom headers) still applies to every query.
- Logs are written to stdout only. Services relying on log files in `/logs` should read `docker logs` (or ship stdout) instead.

### readme.py
To simplify documenting the helper functions, `README.py` can be used to import & render the docstrings into README.md.
Usage:
```python3
python3 -m pip install pydoc-markdown
python3 README.py
```
You can customise the output through the API configuration! See [README.py](README.py) && the [pydoc-markdown docs](https://niklasrosenstein.github.io/pydoc-markdown/).

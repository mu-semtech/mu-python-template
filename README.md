# Mu Python template

Template for [mu.semte.ch](http://mu.semte.ch)-microservices written in Python3.8. Based on the [Flask](https://palletsprojects.com/p/flask/)-framework.

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

### Development mode

By leveraging Dockers' [bind-mount](https://docs.docker.com/storage/bind-mounts/), you can mount your application code into an existing service image. This spares you from building a new image to test each change. Just mount your services' folder to the containers' `/app`. On top of that, you can configure the environment variable `MODE` to `development`. That enables live-reloading of the server, so it immediately updates when you save a file.  

example docker-compose parameters:
```yml
    environment:
      MODE: "development"
    volumes:
      - /home/my/code/my-python-service:/app
```

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

> Write a log message to the log file.
> 
> Works exactly the same as the logging.info (https://docs.python.org/3/library/logging.html#logging.info) method from pythons' logging module.
> Logs are written to the /logs directory in the docker container.  
> 
> Note that the `helpers` module also exposes `logger`, which is the logger instance (https://docs.python.org/3/library/logging.html#logger-objects) 
> used by the template. The methods provided by this instance can be used for more fine-grained logging.

<a id="helpers.error"></a>

#### `error`

```python
def error(msg, status=400, **kwargs)
```

> Returns a Response object containing a JSONAPI compliant error response with the given status code (400 by default).
> 
> Response object documentation: https://flask.palletsprojects.com/en/1.1.x/api/#response-objects
> The kwargs can be any other key supported by JSONAPI error objects: https://jsonapi.org/format/#error-objects

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
def query(the_query)
```

> Execute the given SPARQL query (select/ask/construct) on the triplestore and returns the results in the given return Format (JSON by default).

<a id="helpers.update"></a>

#### `update`

```python
def update(the_query)
```

> Execute the given update SPARQL query on the triplestore. If the given query is not an update query, nothing happens.

<a id="helpers.update_modified"></a>

#### `update_modified`

```python
def update_modified(subject, modified=datetime.datetime.now())
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

- `MU_SPARQL_ENDPOINT` is used to configure the SPARQL endpoint.

  - By default this is set to `http://database:8890/sparql`. In that case the triple store used in the backend should be linked to the microservice container as `database`.


- `MU_APPLICATION_GRAPH` specifies the graph in the triple store the microservice will work in.

  - By default this is set to `http://mu.semte.ch/application`. The graph name can be used in the service via `settings.graph`.


- `MU_SPARQL_TIMEOUT` is used to configure the timeout (in seconds) for SPARQL queries.

#### SPARQL Query Logging
- `LOG_SPARQL_ALL`: Log *all* executed queries, read as well as update (default `True`)

- `LOG_SPARQL_QUERIES`: Log *read* queries (default: `undefined`). Overrules `LOG_SPARQL_ALL`

- `LOG_SPARQL_UPDATES`: Log *update* queries (default `undefined`). Overrules `LOG_SPARQL_ALL`.

The string "true", ignoring casing, is considered `True`.  All other values are considered `False`.

#### Meinheld Gunicorn Docker Variables
Since this template is based on the meinheld-gunicorn-docker image, all possible environment config for that image is also available for the template. See [meinheld-gunicorn-docker#environment-variables](https://github.com/tiangolo/meinheld-gunicorn-docker#environment-variables) for more info. The template configures `WEB_CONCURRENCY` in particular to `1` by default.

### Production

For hosting the app in a production setting, the template depends on [meinheld-gunicorn-docker](https://github.com/tiangolo/meinheld-gunicorn-docker). All [environment variables](https://github.com/tiangolo/meinheld-gunicorn-docker#environment-variables) used by meinheld-gunicorn can be used to configure your service as well.

## Other

### Reassigning `app`
In regular Flask applications (e.g. those not run within this template) you are required to define `app` by using `app = Flask(__name__)` or similar. This does *not* need to be done in your web.py, as this is handled by the microservice architecture/template. Redefining this may cause `The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.` to be thrown on your routes, which can be luckily be fixed by simply removing the previously mentioned `app = ...` line.

### readme.py
To simplify documenting the helper functions, `README.py` can be used to import & render the docstrings into README.md.
Usage:
```python3
python3 -m pip install pydoc-markdown
python3 README.py
```
You can customise the output through the API configuration! See [README.py](README.py) && the [pydoc-markdown docs](https://niklasrosenstein.github.io/pydoc-markdown/).

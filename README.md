# Mu Python template

Template for [mu.semte.ch](http://mu.semte.ch)-microservices written in Python3. Based on the [Flask](https://palletsprojects.com/p/flask/)-framework.

## Quickstart

Create a `Dockerfile` which extends the `semtech/mu-python-template`-image and set a maintainer.
```docker
FROM semtech/mu-python-template:2.0.0-beta.1
LABEL maintainer="sam.landuydt@gmail.com"
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

If your service needs external libraries other than the ones already provided by the template (Flask, SPARQLWrapper and rdflib), you can specify those in a [`requirements.txt`](https://pip.pypa.io/en/stable/reference/requirements-file-format/)-file. The template will take care of installing them when you build your Docker image.

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

The template provides the user with several helper methods. They aim to give you a step ahead for:

- logging
- JSONAPI-compliancy
- SPARQL querying

The below helpers can be imported from the `helpers` module. For example:
```py
from helpers import *
```
Available functions:
#### log(msg)

Works exactly the same as the [logging.info](https://docs.python.org/3/library/logging.html#logging.info) method from pythons' logging module.
Logs are written to the /logs directory in the docker container.  
Note that the `helpers` module also exposes `logger`, which is the [logger instance](https://docs.python.org/3/library/logging.html#logger-objects) used by the template. The methods provided by this instance can be used for more fine-grained logging.

#### generate_uuid()

Generate a random UUID (String).

#### session_id_header(request)

Get the session id from the HTTP request headers.

#### rewrite_url_header(request)

Get the rewrite URL from the HTTP request headers.

#### validate_json_api_content_type(request)

Validate whether the Content-Type header contains the JSONAPI `content-type`-header. Returns a 400 otherwise.

#### validate_resource_type(expected_type, data)

Validate whether the type specified in the JSONAPI data is equal to the expected type. Returns a 409 otherwise.

#### error(title, status="400", detail=None, id=None, links=None, code=None, source=None, meta=None)
    Returns a JSONAPI compliant error [Response object](https://flask.palletsprojects.com/en/1.1.x/api/#response-objects) with the given status code (default: 400). Allowed keys are described by [JSONAPI error objects](https://jsonapi.org/format/#error-objects).

#### query(query)

Executes the given SPARQL select/ask/construct query.

#### update(query)

Executes the given SPARQL update query.


The template provides one other helper module, being the `escape_helpers`-module. It contains functions for SPARQL query-escaping. Example import:
```py
from escape_helpers import *
```

 Available functions:
#### sparql_escape ; sparql_escape_{string|uri|date|datetime|time|bool|int|float}(value)

Converts the given object to a SPARQL-safe RDF object string with the right RDF-datatype.  
This functions should be used especially when inserting user-input to avoid SPARQL-injection.

Separate functions are available for different python datatypes, the `sparql_escape` function however can automatically select the right method to use, for following Python  datatypes:

- `str`
- `int`
- `float`
- `datetime.datetime`
- `datetime.date`
- `datetime.time`
- `boolean`

The `sparql_escape_uri`-function can be used for escaping URI's.

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

- `LOG_LEVEL` takes the same options as defined in the Python [logging](https://docs.python.org/3/library/logging.html#logging-levels) module.

- `MODE` to specify the deployment mode. Can be `development` as well as `production`. Defaults to `production`

- `MU_SPARQL_ENDPOINT` is used to configure the SPARQL endpoint.

  - By default this is set to `http://database:8890/sparql`. In that case the triple store used in the backend should be linked to the microservice container as `database`.


- `MU_APPLICATION_GRAPH` specifies the graph in the triple store the microservice will work in.

  - By default this is set to `http://mu.semte.ch/application`. The graph name can be used in the service via `settings.graph`.


- `MU_SPARQL_TIMEOUT` is used to configure the timeout (in seconds) for SPARQL queries.


Since this template is based on the meinheld-gunicorn-docker image, all possible environment config for that image is also available for the template. See [meinheld-gunicorn-docker#environment-variables](https://github.com/tiangolo/meinheld-gunicorn-docker#environment-variables) for more info. The template configures `WEB_CONCURRENCY` in particular to `1` by default.

### Production

For hosting the app in a production setting, the template depends on [meinheld-gunicorn-docker](https://github.com/tiangolo/meinheld-gunicorn-docker). All [environment variables](https://github.com/tiangolo/meinheld-gunicorn-docker#environment-variables) used by meinheld-gunicorn can be used to configure your service as well.

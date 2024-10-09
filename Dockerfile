FROM python:3.13
LABEL maintainer="team@semantic.works"

# Gunicorn Docker config
ENV PYTHONPATH "/usr/src/app:/app"

COPY ./start.sh /
COPY ./gunicorn_config.py /
RUN chmod +x /start.sh
CMD ["/start.sh"]

# Template config
ENV LOG_LEVEL info
ENV LOG_SPARQL_ALL True
ENV MU_SPARQL_ENDPOINT 'http://database:8890/sparql'
ENV MU_SPARQL_UPDATEPOINT 'http://database:8890/sparql'
ENV MU_APPLICATION_GRAPH 'http://mu.semte.ch/application'

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD . /usr/src/app

RUN ln -s /app /usr/src/app/ext \
     && cd /usr/src/app \
     && pip3 install -r requirements.txt

ONBUILD ADD Dockerfile requirement[s].txt /app/
ONBUILD RUN cd /app/ \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

ONBUILD ADD . /app/
ONBUILD RUN touch /app/__init__.py

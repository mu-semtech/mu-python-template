FROM python:3
MAINTAINER Michaël Dierick "michael@dierick.io"

ENV APP_ENTRYPOINT web
ENV LOG_LEVEL info
ENV MU_SPARQL_ENDPOINT 'http://database:8890/sparql'
ENV MU_SPARQL_UPDATEPOINT 'http://database:8890/sparql'
ENV MU_APPLICATION_GRAPH 'http://mu.semte.ch/application'

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD . /usr/src/app

RUN ln -s /app /usr/src/app/ext \
     && cd /usr/src/app \
     && pip3 install -r requirements.txt

ONBUILD ADD . /app/
ONBUILD RUN cd /app/ \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

EXPOSE 80

CMD python web.py

FROM python:3.12-slim
LABEL maintainer="team@semantic.works"

ENV MODULE_NAME=web
ENV PYTHONPATH="/usr/src/app:/app"
ENV WEB_CONCURRENCY="1"

COPY ./start.sh /root/start.sh
RUN chmod +x /root/start.sh

# Template config
ENV APP_ENTRYPOINT=web
ENV LOG_LEVEL=info
ENV LOG_SPARQL_ALL=True
ENV MU_SPARQL_ENDPOINT='http://database:8890/sparql'
ENV MU_SPARQL_UPDATEPOINT='http://database:8890/sparql'
ENV MU_APPLICATION_GRAPH='http://mu.semte.ch/application'
ENV MODE='production'

RUN mkdir -p /usr/src/app && mkdir /logs
WORKDIR /usr/src/app
ADD . /usr/src/app

RUN ln -s /app /usr/src/app/ext \
     && cd /usr/src/app \
     && pip install -r requirements.txt

CMD [ "/root/start.sh" ]
ONBUILD ADD Dockerfile requirement[s].txt /app/
ONBUILD RUN cd /app/ \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

ONBUILD ADD . /app/
ONBUILD RUN touch /app/__init__.py

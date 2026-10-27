FROM python:3.13-slim
LABEL maintainer="team@semantic.works"

# Don't write bytecode for cleaner mounts
ENV PYTHONDONTWRITEBYTECODE=1
# Print output immediately
ENV PYTHONUNBUFFERED=1

# Gunicorn Docker config
ENV PYTHONPATH "/usr/src/app:/app"
ENV WEB_CONCURRENCY "1"

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./gunicorn_conf.py /gunicorn_conf.py

# Template config
ENV APP_ENTRYPOINT web
ENV LOG_LEVEL info
ENV LOG_SPARQL_ALL True
ENV MU_SPARQL_ENDPOINT 'http://database:8890/sparql'
ENV MU_SPARQL_UPDATEPOINT 'http://database:8890/sparql'
ENV MU_APPLICATION_GRAPH 'http://mu.semte.ch/application'
ENV MODE 'production'

# Compilers for dependencies that ship no wheels (previous base image was a full python image)
RUN apt-get update \
     && apt-get install -y --no-install-recommends gcc g++ \
     && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir uv==0.13.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ADD . /usr/src/app

RUN ln -s /app /usr/src/app/ext \
     && cd /usr/src/app \
     && uv pip install --system --no-cache -r requirements.txt

ONBUILD ADD Dockerfile requirement[s].txt on-build.sh* /app/
ONBUILD RUN cd /app/ \
    && if [ -f on-build.sh ]; then chmod +x on-build.sh && ./on-build.sh; fi \
    && if [ -f requirements.txt ]; then uv pip install --system --no-cache -r requirements.txt; fi

ONBUILD ADD . /app/
ONBUILD RUN touch /app/__init__.py

CMD ["/start.sh"]

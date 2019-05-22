#!/bin/bash

ARGS=""

ARGS="$ARGS --log-to-terminal"
ARGS="$ARGS --port 8080"
ARGS="$ARGS --url-alias /static wsgi/static"

exec mod_wsgi-express start-server $ARGS wsgi/application
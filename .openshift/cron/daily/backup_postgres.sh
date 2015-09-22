#!/bin/bash
# Backs up the OpenShift PostgreSQL database for this application

NOW="$(date +"%Y-%m-%d")"
FILENAME="$OPENSHIFT_DATA_DIR/$OPENSHIFT_APP_NAME_fixtures_$NOW.json"

# version conflict!
# pg_dump: server version: 9.2.8; pg_dump version: 8.4.20
# pg_dump: aborting because of server version mismatch
# pg_dump -Fc -h $OPENSHIFT_POSTGRESQL_DB_HOST -p $OPENSHIFT_POSTGRESQL_DB_PORT $OPENSHIFT_APP_NAME > $FILENAME

# workaround: pulling django fixtures, slower, but works
source $OPENSHIFT_PYTHON_DIR/virtenv/bin/activate
cd $OPENSHIFT_REPO_DIR
python manage.py dumpdata --natural --exclude=contenttype --exclude=auth.Permission > $FILENAME
gzip $FILENAME

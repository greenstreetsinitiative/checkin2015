# The Ultimate Guide

Sorry, OS X instructions only until someone else writes up additional instructions. 

## Install all the things

1. Install [Git](http://git-scm.com/book/en/v2/Getting-Started-Installing-Git). You can do this by installing XCode Command Line tools.
2. Install [brew](http://brew.sh/). 
3. `brew install python`. This also installs pip.
4. `pip install virtualenv`
5. `pip install virtualenvwrapper`
6. `brew install postgres`. IMPORTANT: Read what brew tells you. You might want to make start postgresql at login `ln -sfv /usr/local/opt/postgresql/*.plist ~/Library/LaunchAgents` and then load postgresql now with `launchctl load ~/Library/LaunchAgents/homebrew.mxcl.postgresql.plist`.
7. `brew install postgis`
8. Check for errors with `brew doctor` if desired.

## Download this project!

1. `git clone https://github.com/greenstreetsinitiative/checkin2015.git` OR fork (via the Github website) and clone your fork.
2. Navigate to the checkin2015 directory in your terminal.

## Setup the database

1. `initdb /usr/local/var/postgres -E utf8`
2. `createuser -d -P postgres` creates a role that can make databases.
3. `pg_ctl -D /usr/local/var/postgres -l /usr/local/var/postgres/server.log start &` if the server is not already running.
4. `createuser django`
5. `createdb -O django checkin`
6. `psql -d checkin -c "ALTER USER django WITH PASSWORD 'django';"`
7. `psql -d checkin -c "CREATE EXTENSION postgis;"`

## Setup the virtual environment

1. `mkvirtualenv greenstreets`. You can name it other than greenstreets too.
2. Find .virtualenvs/greenstreets/bin/postactivate and edit that file to include the environment variables:
```
export SECRET_KEY="abcdef"
export DB_NAME="checkin"
export DB_USER="django"
export DB_PASSWORD="django"
export DB_PORT="5432"
export DB_HOST="localhost"
export EMAIL_HOST_USER="xten"
export EMAIL_HOST_PASSWORD="xten"
export MANDRILL_API_KEY="V62ndycapG44sI-x9EcG1A"
```
3. `workon greenstreets`. This activates the virtual environment.

## Run it

1. `pip install -r requirements.txt` 
2. `python manage.py migrate`
3.  If you have data, `python manage.py loaddata data.json`
4. `python manage.py runserver`

## Bonus: Export data to CSV

```
psql -d checkin -c "\copy (select checkins.*, legs.* from (select a.id, a.name, a.email, orgs.employer_name, orgs.team_name, a.share, a.home_address, a.work_address, a.comments, a.carbon_change, a.carbon_savings, a.calorie_change, a.calories_total, a.change_type, a.already_green from survey_commutersurvey a left outer join (select m.id as employer_id, m.name as employer_name, n.id as team_id, n.name as team_name from survey_employer m left outer join survey_team n on m.id = n.parent_id) orgs on (a.employer_id = orgs.employer_id and a.team_id = orgs.team_id)) checkins right outer join (select x.checkin_id, x.day, x.direction, y.name, x.duration  from survey_leg x, survey_mode y where x.mode_id = y.id) legs on checkins.id = legs.checkin_id) to ../Checkins.csv CSV HEADER"
```

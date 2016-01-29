#!/usr/bin/env bash

user=postgres
webserver=/vagrant/simon-web

{
	apt-get update
} > /dev/null && echo "Base system dependencies updated"

{
	sudo apt-get install -y --force-yes \
	git \
	subversion \
	python-psycopg2 \
	python-dev \
	libxml2-dev \
	libxslt-dev
} > /dev/null && echo "New system dependencies installed"

{
	sudo apt-get install -y --force-yes \
	postgresql-9.1 \
	postgresql-contrib-9.1 \
	postgresql-client-common \
	postgresql-client-9.1

} > /dev/null && echo "PostgreSQL installed"

{
	sudo -u postgres psql -c "alter role $user password 'postgres'"
	sudo -u postgres psql -c "create database simon with owner=$user"
} > /dev/null && echo "Simon database created and populated"

{
	wget --quiet https://bootstrap.pypa.io/get-pip.py > /dev/null && python get-pip.py > /dev/null && rm get-pip.py && echo "pip installed" && pip install -r /vagrant/requirements.txt > /dev/null && echo "Python dependencies installed"
} && echo "Python dependencies installed"

{
	cd $webserver
	python manage.py syncdb
	python manage.py runserver 0.0.0.0:8000 &
	cd -
} && echo "Django web server is up  and running :)"

echo "VM dependencies installed"
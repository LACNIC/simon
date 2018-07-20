#!/usr/bin/env bash

user=postgres
home=/vagrant
webserver=$home/simon-web
dump=$home/simon.dump
dump_zip=$dump.zip
pip_requirements=$home/requirements.txt

{
	apt-get update
} > /dev/null && echo "Base system dependencies updated"

{
	sudo apt-get install -y --force-yes \
	git \
	apache2 \
	apache2-dev \
	# python-psycopg2 \
	python-dev \
	libxml2-dev \
	libxslt-dev \
	unzip \
	python-numpy \
	python-scipy \
	python-matplotlib \
	ipython \
	ipython-notebook \
	python-pandas \
	python-sympy \
	python-nose

	build-essential


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
	touch $dump ^^ echo "Dummy file created"
	unzip $dump_zip
	# && sudo -u postgres psql < $dump && echo "Simon database created and populated"
	# echo "from django.contrib.auth.models import User; User.objects.create_superuser('simon', 'admin@example.com', 'simon')" | python manage.py shell

	# Archivos que faltan
	sudo touch /opt/django/simon/simon-web/simon_project/passwords.py
	sudo mkdir /opt/django/simon/simon-web/logs
	sudo touch /opt/django/simon/simon-web/logs/debug.log

} > /dev/null

{
	curl https://bootstrap.pypa.io/get-pip.py | sudo python && echo "pip installed" && pip install -r $pip_requirements > /dev/null && echo "Python dependencies installed"
} && echo "Python dependencies installed"

echo "VM dependencies installed"

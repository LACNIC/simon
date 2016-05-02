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
	subversion \
	python-psycopg2 \
	python-dev \
	libxml2-dev \
	libxslt-dev \
	unzip
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
	unzip $dump_zip
	sudo -u postgres psql < $dump
	# echo "from django.contrib.auth.models import User; User.objects.create_superuser('simon', 'admin@example.com', 'simon')" | python manage.py shell
} > /dev/null && echo "Simon database created and populated"

{
	wget --quiet https://bootstrap.pypa.io/get-pip.py > /dev/null && python get-pip.py > /dev/null && rm get-pip.py && echo "pip installed" && pip install -r $pip_requirements > /dev/null && echo "Python dependencies installed"
} && echo "Python dependencies installed"

#{
	# cd $webserver
	# python manage.py syncdb
	# python manage.py runserver 0.0.0.0:8000 &
	# cd -
#} && echo "Django web server is up  and running :)"

echo "VM dependencies installed"
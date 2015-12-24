#!/usr/bin/env bash

echo "Installing dependencies"

apt-get update

{
	apt-get -y --force-yes install \
	git \
	subversion \
	python-psycopg2 \
	python-dev \
	libxml2-dev \
	libxslt-dev
}

{
	sudo apt-get install --force-yes postgresql-9.1
	sudo apt-get install --force-yes postgresql-contrib-9.1
	sudo apt-get install --force-yes postgresql-client-common
} && echo "PostgreSQL installed"

{
	wget --quiet https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py && echo "pip installed" || echo "pip not installed" && pip install -r /vagrant/requirements.txt && echo "Python dependencies installed"
}

echo "VM dependencies installed"
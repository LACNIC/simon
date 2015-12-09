#!/usr/bin/env bash

echo "Installing dependencies"

apt-get update

apt-get -y --force-yes install \
git \
subversion \
python-psycopg2 \
python-dev \
libxml2-dev \
libxslt-dev

sudo apt-get install postgresql \
postgresql-contrib \
postgresql-client-common

wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py && echo "pip instalado"
pip install -r requirements.txt

pip install django==1.6
pip install lxml
pip install netaddr
pip install virtualenv
pip install geoip2
pip install django-admin-bootstrapped==2.3.5
pip install django-cors-headers==1.0.0
pip install trparse==0.1.0
pip install newrelic==2.50.0.39

echo "Finalizó la instalación de las dependencias de la VM..."
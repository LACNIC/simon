#!/usr/bin/env bash

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

# wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && rm get-pip.py

pip install django==1.6
pip install lxml
pip install netaddr
pip install virtualenv

echo "Finalizó la instalación de las dependencias de la VM..."
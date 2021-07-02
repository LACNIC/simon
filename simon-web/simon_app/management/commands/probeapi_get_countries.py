#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from django.core.management.base import BaseCommand
from .probeapi_libs import get_countries


class Command(BaseCommand):
    def handle(self, *args, **options):
        print(list(args))
        print(get_countries(ccs=args))

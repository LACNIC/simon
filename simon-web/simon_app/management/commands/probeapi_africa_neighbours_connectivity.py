#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement


class Command(BaseCommand):
    @probeapi(command="Africa Connectivity [Neighbours]")
    def handle(self, *args, **options):
        neighbours = {
            'BI': ['RW'], 'DZ': ['MR'], 'ET': ['KE'], 'RW': ['BI', 'CD', 'TZ', 'UG'], 'TZ': ['RW', 'ZM'],
            'CM': ['CF', 'GQ'], 'NA': ['AO'], 'LR': ['GN'], 'TD': ['CF'], 'ZM': ['AO', 'CD', 'MW', 'MZ', 'TZ'],
            'CI': ['GN'], 'GQ': ['CM', 'GA'], 'MR': ['DZ', 'ML', 'SN'], 'CG': ['CF', 'CD'],
            'CF': ['CM', 'TD', 'CD', 'CG', 'SD'], 'AO': ['CD', 'ZM', 'NA'], 'CD': ['AO', 'CF', 'CG', 'RW', 'ZM'],
            'GA': ['GQ'], 'GN': ['CI', 'LR', 'ML', 'SN', 'SL'], 'ZW': ['MZ'], 'KE': ['ET', 'SO'], 'ML': ['GN', 'MR'],
            'MW': ['ZM'], 'SO': ['KE'], 'SN': ['GN', 'MR'], 'SL': ['GN'], 'UG': ['RW'], 'MZ': ['ZM', 'ZW'], 'SD': ['CF']
        }

        def init_msm((N, ns)):
            msm = ProbeApiMeasurement()

            results = msm.init(
                tps=["%s.exp.dev.lacnic.net" % n.lower() for n in ns],
                ccs=[N]
            )

            return results

        results = map(init_msm, [(N, ns) for N, ns in neighbours.items()])

        return results

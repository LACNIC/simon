#!/usr/bin/python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import SpeedtestTestPoint, Country
from simon_app.decorators import probeapi
from probeapi import ProbeApiMeasurement
from simon_app.decorators import timed


class Command(BaseCommand):


    command = "Africa Connectivity [Neighbours]"

    @timed(name=command)
    @probeapi(command=command)
    def handle(self, *args, **options):
        neighbours = {
            'BI': ['RW'], 'DZ': ['MR'], 'ET': ['DJ', 'ER', 'KE', 'SO', 'SS', 'SD'], 'RW': ['BI', 'CD', 'TZ', 'UG'], 'TZ': ['RW', 'ZM'],
            'CM': ['CF', 'GQ'], 'NA': ['AO'], 'LR': ['GN'], 'TD': ['CF'], 'ZM': ['AO', 'CD', 'MW', 'MZ', 'TZ'],
            'CI': ['GN'], 'GQ': ['CM', 'GA'], 'MR': ['DZ', 'ML', 'SN'], 'CG': ['CF', 'CD'],
            'CF': ['CM', 'TD', 'CD', 'CG', 'SD'], 'AO': ['CD', 'CG', 'ZM', 'NA'], 'CD': ['AO', 'CF', 'CG', 'RW', 'ZM'],
            'GA': ['GQ'], 'GN': ['CI', 'LR', 'ML', 'SN', 'SL'], 'ZW': ['MZ'], 'KE': ['ET', 'SO'], 'ML': ['GN', 'MR'],
            'MW': ['ZM'], 'SO': ['KE'], 'SN': ['GN', 'MR'], 'SL': ['GN'], 'UG': ['RW'], 'MZ': ['ZM', 'ZW'], 'SD': ['CF'],
            'CV': ['SN', 'GM', 'GW', 'MR']
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

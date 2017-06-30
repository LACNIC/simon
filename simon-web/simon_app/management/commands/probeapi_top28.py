#!/usr/bin/python
# -*- coding: utf-8 -*-
from probeapi import ProbeApiMeasurement


def ping_top28(ccs):
        msm = ProbeApiMeasurement(max_job_queue_size=50, max_points=20)

        top28 = ['jumia.com.ng' , 'konga.com', 'bidorbuy.co.za', 'fnb.co.za', 'gtbank.com', 'absa.co.za',
                 'standardbank.co.za', 'almasryalyoum.com', 'elkhabar.com', 'vanguardngr.com', 'news24.com',
                 'punchng.com', 'iol.co.za', 'ghanaweb.com', 'nairaland.com', 'supersport.com', 'alwafd.org',
                 'iroking.com']

        top28_results = msm.init(
            tps=top28,
            ccs=ccs
        )

        return top28_results

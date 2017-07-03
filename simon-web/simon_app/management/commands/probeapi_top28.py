#!/usr/bin/python
# -*- coding: utf-8 -*-
from probeapi import ProbeApiMeasurement
from probeapi_traceroute import ProbeApiTraceroute

SITES = ['jumia.com.ng', 'konga.com', 'bidorbuy.co.za', 'fnb.co.za', 'gtbank.com', 'absa.co.za',
         'standardbank.co.za', 'almasryalyoum.com', 'elkhabar.com', 'vanguardngr.com', 'news24.com',
         'punchng.com', 'iol.co.za', 'ghanaweb.com', 'nairaland.com', 'supersport.com', 'alwafd.org',
         'iroking.com']


def ping_top28(ccs):
    msm = ProbeApiMeasurement(max_job_queue_size=50, max_points=20)

    top28 = SITES

    top28_results = msm.init(
        tps=top28,
        ccs=ccs
    )

    return top28_results


def trace_top28(ccs):
    msm = ProbeApiTraceroute(
        max_job_queue_size=50,
        max_points=20,
        ping_count=3
    )

    top28 = SITES

    results = msm.init(
        tps=top28,
        ccs=ccs
    )

    return results

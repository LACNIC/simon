#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from simon_app.models import HourlyBatch, ProbeApiFetchFromFTP, ProbeApiV3PingResult, AS, ProbeApiV3TracerouteResultMetaData, ProbeApiV3PingResultMetaData, ProbeApiV3DataResult, ProbeApiV3TracerouteHop
from simon_app.decorators import probeapi
from simon_app.decorators import timed_command, mem_comsumption
import numpy
from simon_app.api_views import get_cc_from_ip_address
import pytz


class Command(BaseCommand):

    def handle(self, *args, **options):

        objetos = ProbeApiFetchFromFTP.objects.all()
        cant_pings_guardados = 0
        cant_tr_guardados = 0

        for o in objetos:

            result_parts = o.command_result.split("<CMD>")
            name_result = o.command_name.split("<CMD>")
            probe_id = name_result[0].split("|")[1].split("=")[1]
            country_origin = get_cc_from_ip_address(o.ip)
            as_origin = AS.objects.get_as_by_ip(o.ip).asn
            print(o.server_time, o.timestamp)
            try:
                dt_timestamp = datetime.fromtimestamp(o.timestamp / 1000, pytz.utc)
                time_diff = (o.server_time - dt_timestamp).total_seconds()
            except:
                dt_timestamp = datetime.fromtimestamp(0 / 1000, pytz.utc)
                time_diff = -1

            #TRACERT|host=out-of-lac.exp.dev.lacnic.net|ttl=32|timeout=1000|sleep=10|resolve=1|ipv4only=1|

            if len(o.traceroutemetadata.all()) == 0:
                cant_tr_guardados = cant_tr_guardados + 1
                ### TRACE ROUTE RESULTS
                name_parts = name_result[2].split("|")

                hostname = name_parts[1].split("=")[1]
                ttl = name_parts[2].split("=")[1]
                ipv4only = False
                ipv6only = False
                for i in name_parts:

                    if i.startswith("ipv4only="):
                        ipv4only = i.split("=")[1]
                    if i.startswith("ipv6only="):
                        ipv6only = i.split("=")[1]

                print(probe_id, hostname, ipv4only, ipv6only, o.server_time)
                traceroute_result = ProbeApiV3TracerouteResultMetaData.objects.create(
                    probeapi_probe_id = probe_id,
                    hostname = hostname,
                    ipv4only = ipv4only,
                    ipv6only = ipv6only,
                    error_msg = "",
                    server_time = o.server_time,
                    time_diff = float(time_diff),
                    probeapifetchfromftp = o
                )
                # traceroute_result.save()

                traceroute = result_parts[1].split("|")
                #tr_hops = traceroute.split("|")[2:-1]
                #print ("cant hops: %s" % str(len(tr_hops)))
                hops = {}
                hop_num = 1
                error_msg = ""
                for k in traceroute:
                    parts = k.split("#")
                    if len(parts) == 1:
                        if k.split("=")[0] == "ip":
                            ip_dest_final = k.split("=")[1]
                        if k.split("=")[0] == "hostname":
                            host_final = k.split("=")[1]
                        if k.split("=")[0] == "ERROR":
                            error_msg = k.split("=")[1].split("\n")[0]
                    if len(parts) > 1:
                        #ip=10.0.0.1,hostname=,mtu=,rttl=64,pings=8.42,4.47,2.99
                        ip_dest = ''
                        minimo = 0
                        avg = 0
                        maximo = 0
                        std = 0
                        mediana = 0
                        pings = []
                        for j in parts:

                            if j.split("=")[0] == "ip":
                                ip_dest = j.split("=")[1]
                                country_destination = get_cc_from_ip_address(ip_dest)
                                as_destination = AS.objects.get_as_by_ip(ip_dest).asn
                            if j.split("=")[0] == "hostname":
                                host = j.split("=")[1]
                            if j.split("=")[0] == "mtu":
                                mtu = j.split("=")[1]
                            if j.split("=")[0] == "rttl":
                                rttl = j.split("=")[1]
                            if j.split("=")[0] == "pings":
                                if j.split("=")[1]=="":
                                    pings = []
                                else:
                                    pings = j.split("=")[1].split(",")
                                try:
                                    std = float(numpy.std(numpy.array(pings).astype(numpy.float)))
                                    mediana = float(numpy.median(numpy.array(pings).astype(numpy.float)))
                                    minimo = float(numpy.min(numpy.array(pings).astype(numpy.float)))
                                    maximo = float(numpy.max(numpy.array(pings).astype(numpy.float)))
                                    avg = float(numpy.mean(numpy.array(pings).astype(numpy.float)))
                                except:
                                    stdev, median, minimo, maximo, avg = [0, 0, 0, 0, 0]

                        data_obj = ProbeApiV3DataResult.objects.create(
                                testype="traceroute",
                                version=3,
                                ip_destination=ip_dest,
                                ip_origin=o.ip,
                                number_probes=3,
                                min_rtt=minimo,
                                max_rtt=maximo,
                                ave_rtt=avg,
                                dev_rtt=std,
                                median_rtt=mediana,
                                packet_loss=3-len(pings),
                                country_origin=country_origin,
                                country_destination=country_destination,
                                ip_version=(4 if '.' in ip_dest else 6),
                                as_origin=as_origin,
                                as_destination=as_destination,
                                date_test=dt_timestamp
                        )

                        tr_hop_obj = ProbeApiV3TracerouteHop.objects.create(
                                data = data_obj,
                                traceroute = traceroute_result,
                                hop_number = hop_num,
                                error_msg = error_msg
                        )
                        hop_num = hop_num + 1


            if len(o.pingmetadata.all()) == 0:
                cant_pings_guardados = cant_pings_guardados + 1

                ### PING RESULTS
                ip_dest = ''
                hostname = ''
                send = 0
                lost = 0
                percentage = 0
                minimo = 0
                avg = 0
                maximo = 0
                std = 0
                rtts = [0]
                error_msg = ''
                ping = result_parts[0].split("|")
                for i in ping:
                    if i.startswith("ip="):
                        ip_dest = i.split("=")[1]
                    if i.startswith("hostname="):
                        hostname = i.split("=")[1]
                    if i.startswith("packetStats="):
                        send, _, lost, percentage = i.split("=")[1].split(",")
                    if i.startswith("rttStats="):
                        minimo, avg, maximo, std, pipe = i.split("=")[1].split(",")
                    if i.startswith("result="):
                        rtts = i.split("=")[1].split(",")
                    if i.startswith("ERROR="):
                        error_msg = i.split("=")[1].split("\n")[0]

                try:
                    stdev = float(numpy.std(numpy.array(rtts).astype(numpy.float)))
                    median = float(numpy.median(numpy.array(rtts).astype(numpy.float)))
                    minimo = float(minimo)
                    maximo = float(maximo)
                    avg = float(avg)
                    send = int(send)
                    lost = int(lost)
                    percentage = float(percentage)
                except:
                    stdev, median, minimo, maximo, avg, send, lost, percentage = [0, 0, 0, 0, 0, 0, 0, 0]

                # print(minimo,str(rtts), send)

                # print(ping, probe_id)
                for i in name_result[1].split("|"):
                    ipv4only = False
                    ipv6only = False
                    if i.startswith("ipv4only="):
                        ipv4only = i.split("=")[1]
                    if i.startswith("ipv6only="):
                        ipv6only = i.split("=")[1]

                country_destination = get_cc_from_ip_address(ip_dest)
                as_destination = AS.objects.get_as_by_ip(ip_dest).asn

                metadata = ProbeApiV3PingResultMetaData.objects.create(
                    probeapifetchfromftp=o,
                    probeapi_probe_id=probe_id,
                    hostname=hostname,
                    ipv4only=ipv4only,
                    ipv6only=ipv6only,
                    error_msg=error_msg,
                    server_time=o.server_time,
                    time_diff=float(time_diff)
                )
                metadata.save()

                data = ProbeApiV3DataResult(
                    testype="ping",
                    version=3,
                    ip_destination=ip_dest,
                    ip_origin=o.ip,
                    number_probes=send,
                    min_rtt=minimo,
                    max_rtt=maximo,
                    ave_rtt=avg,
                    dev_rtt=stdev,
                    median_rtt=median,
                    packet_loss=lost,
                    country_origin=country_origin,
                    country_destination=country_destination,
                    ip_version=(4 if '.' in ip_dest else 6),
                    as_origin=as_origin,
                    as_destination=as_destination,
                    date_test=dt_timestamp
                )
                data.save()

                result = ProbeApiV3PingResult.objects.create(
                    metadata = metadata,
                    data = data,
                    packet_loss_percentage=percentage
                )

                #result.save()

        print("Se guardaron %s resultados ping" % str(cant_pings_guardados))
        print("Se guardaron %s resultados traceroute" % str(cant_tr_guardados))
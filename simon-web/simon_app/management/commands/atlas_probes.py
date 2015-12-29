# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from simon_app.models import *
import json
import urllib2
from simon_app.reportes import GMTUY
from simon_app.mailing import *
from simon_app.management.commands.tweet import *

"""
    Crawls the RIPE Atlas probe API looking for new probes in the region.
"""

class Command(BaseCommand):
    def handle(self, *args, **options):
        command = "New Atlas Probes Check"
        try:

            existent_probes = RipeAtlasProbe.objects.all().values_list('probe_id', flat=True)
            statuses = []
            new_probes = []  # stores probe and status objects

            base_url = "https://atlas.ripe.net"
            ccs = Country.objects.get_region_countries().values_list('iso', flat=True)
            anchor = 0

            anchor_count = anchor
            for cc in ccs:

                next = "/api/v1/probe/?country_code=%s" % (cc)
                while next != None:

                    url = "%s%s" % (base_url, next)
                    page_content = json.loads(urllib2.urlopen(url).read())
                    next = page_content['meta']['next']

                    for probe in page_content['objects']:

                        is_anchor = probe['is_anchor']
                        if is_anchor:
                            anchor_count += 1

                        status = probe['status_name']
                        rap_status = RipeAtlasProbeStatus(
                            date=datetime.now(GMTUY()),
                            status=status
                        )
                        statuses.append(status)

                        if probe['id'] in existent_probes:
                            rap_status.probe = RipeAtlasProbe.objects.get(probe_id=probe['id'])
                            rap_status.save()
                            continue

                        rap = RipeAtlasProbe(
                            probe_id=probe['id'],
                            country_code=probe['country_code'],
                            asn_v4=probe['asn_v4'],
                            asn_v6=probe['asn_v6'],
                            prefix_v4=probe['prefix_v4'],
                            prefix_v6=probe['prefix_v6'],
                        )
                        rap.save()

                        rap_status.probe = rap
                        rap_status.save()

                        new_probes.append({'probe': rap, 'status': rap_status, 'cc': cc, 'is_anchor': is_anchor})

            from collections import Counter
            counter = Counter(statuses)
            for c in counter:
                amount = counter[c]
                print c, amount, "(%.0f%%)" % (100.0 * amount / len(statuses))
            print "Anchor count for LAC region: %.0f" % (anchor_count)


            # Mailing

            # monitored = RipeAtlasMonitoredIds.objects.all().values_list('probe_id', flat=True)
            # new_monitored = [np.probe for np in new_probes if np.probe_id in monitored]

            n = len(new_probes)
            if n > 0:
                subject = "Nuevas RIPE Atlas probes en LAC"
                ctx = {
                    'probes': new_probes
                }

                send_mail_new_probes_found(subject=subject, ctx=ctx)

                text = "%s %s RIPE Atlas probes en la región!" % (n, "nuevas" if n > 1 else "nueva")
                tweet(text)

                new_anchors = [p for p in new_probes if p.is_anchor]
                for a in new_anchors:
                    text = "Una buena noticia! Se ha detectado un nuevo RIPE Atlas Anchor en la región (%s)!" % (a.probe.country_code)
                    tweet(text)

            status = True
        except:
            status = False
        finally:
            ca = CommandAudit(command=command, status=status)
            ca.save()

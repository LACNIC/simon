from django.core.management.base import BaseCommand
from simon_app.models import RipeAtlasPingResult, RipeAtlasMeasurement


class Command(BaseCommand):
    def handle(self, *args, **options):

        from ripe.atlas.sagan import PingResult
        from simon_app.api_views import getCountryFromIpAddress

        msm=args[0]

        def atlas_result(*args):
            my_result = PingResult(args[0])

            try:
                packet_loss = my_result.packets_sent - my_result.packets_received
            except:
                packet_loss = 0

            try:
                res = RipeAtlasPingResult(
                    probe_id=my_result.probe_id,
                    measurement_id=my_result.measurement_id,

                    ip_destination=my_result.destination_address,
                    ip_origin=my_result.origin,
                    country_destination=getCountryFromIpAddress(my_result.destination_address),
                    country_origin=getCountryFromIpAddress(my_result.origin),

                    ip_version=my_result.af,
                    testype='icmp',

                    min_rtt=my_result.rtt_min,
                    max_rtt=my_result.rtt_max,
                    ave_rtt=my_result.rtt_average,
                    median_rtt=my_result.rtt_median,
                    number_probes=my_result.packets_sent,
                    packet_loss=packet_loss
                )

                if res.is_valid():
                    print res
                    res.save()

            except Exception as e:
                print e



        from socketIO_client import SocketIO
        # print "Subscribing to RIPE Atlas measurement ID: %s" % msm
        socketIO = SocketIO('https://atlas-stream.ripe.net/stream/socket.io', 443)
        socketIO.on("atlas_result", atlas_result)
        socketIO.emit("atlas_subscribe", {'stream_type': 'result', 'msm': msm})
        socketIO.wait()
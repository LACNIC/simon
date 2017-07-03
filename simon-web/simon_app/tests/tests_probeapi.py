from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from simon_app.management.commands.probeapi_traceroute import ProbeApiTraceroute


class ProbeapiParserTestCase(TransactionTestCase):
    PROBEAPI_RESPONSE = '{"StartTracertTestByCountryResult":[{"ASN":{"AsnID":"AS29614","AsnName":"VODAFONE GHANA AS ' \
                        'INTERNATIONAL TRANSIT"},"Accuracy":0,"Country":{"CountryCode":"GH",' \
                        '"CountryFlag":"http:\/\/bscapi.blob.core.windows.net\/bsc-img-country-logos\/gh.png",' \
                        '"CountryName":"Ghana","State":"Greater Accra Region","StateCode":null},' \
                        '"DateTimeStamp":"\/Date(1499042318694+0000)\/","ID":88191137,"Location":{"Latitude":5.55,' \
                        '"Longitude":-0.2167},"Network":{"CountryCode":null,"LogoURL":null,"NetworkID":"23920",' \
                        '"NetworkName":"Vodafone Ghana As International Transit"},"TRACERoute":[{' \
                        '"Destination":"konga.com","HostName":"konga.com","IP":"192.229.182.48","Tracert":[{' \
                        '"HostName":"41-218-208-1-adsl-dyn.4u.com.gh","IP":"41.218.208.1","PingTimeArray":["14","15",' \
                        '"15"],"Ping1":"14","Ping2":"15","Ping3":"15","Status":"OK"},{"HostName":"",' \
                        '"IP":"80.87.78.69","PingTimeArray":["15","14","15"],"Ping1":"15","Ping2":"14","Ping3":"15",' \
                        '"Status":"OK"},{"HostName":"","IP":"80.231.76.186","PingTimeArray":["15","14","15"],' \
                        '"Ping1":"15","Ping2":"14","Ping3":"15","Status":"OK"},' \
                        '{"HostName":"ix-pos-3-0-1.core4.LDN-London.as6453.net","IP":"80.231.76.185",' \
                        '"PingTimeArray":["107","107","107"],"Ping1":"107","Ping2":"107","Ping3":"107",' \
                        '"Status":"OK"},{"HostName":"if-xe-0-1-3-0.tcore2.LDN-London.as6453.net","IP":"80.231.62.25",' \
                        '"PingTimeArray":["108","108","108"],"Ping1":"108","Ping2":"108","Ping3":"108",' \
                        '"Status":"OK"},{"HostName":"ldn-b5-link.telia.net","IP":"62.115.9.173","PingTimeArray":[' \
                        '"111","110","111"],"Ping1":"111","Ping2":"110","Ping3":"111","Status":"OK"},' \
                        '{"HostName":"edgecast-ic-306177-ldn-b5.c.telia.net","IP":"62.115.42.138","PingTimeArray":[' \
                        '"108","108","108"],"Ping1":"108","Ping2":"108","Ping3":"108","Status":"OK"},{"HostName":"",' \
                        '"IP":"192.229.182.48","PingTimeArray":["109","118","107"],"Ping1":"109","Ping2":"118",' \
                        '"Ping3":"107","Status":"OK"}]}]},{"ASN":{"AsnID":"AS29614","AsnName":"VODAFONE GHANA AS ' \
                        'INTERNATIONAL TRANSIT"},"Accuracy":0,"Country":{"CountryCode":"GH",' \
                        '"CountryFlag":"http:\/\/bscapi.blob.core.windows.net\/bsc-img-country-logos\/gh.png",' \
                        '"CountryName":"Ghana","State":"","StateCode":null},"DateTimeStamp":"\/Date(' \
                        '1499042313447+0000)\/","ID":88212404,"Location":{"Latitude":5.55,"Longitude":-0.2167},' \
                        '"Network":{"CountryCode":null,"LogoURL":null,"NetworkID":"23920","NetworkName":"Vodafone ' \
                        'Ghana As International Transit"},"TRACERoute":[{"Destination":"konga.com",' \
                        '"HostName":"konga.com","IP":"192.229.182.48","Tracert":[{"HostName":"","IP":"172.27.119.3",' \
                        '"PingTimeArray":["99","79","118"],"Ping1":"99","Ping2":"79","Ping3":"118","Status":"OK"},' \
                        '{"HostName":"","IP":"172.29.119.2","PingTimeArray":["80","79","138"],"Ping1":"80",' \
                        '"Ping2":"79","Ping3":"138","Status":"OK"},{"HostName":"","IP":"172.29.119.150",' \
                        '"PingTimeArray":["89","109","99"],"Ping1":"89","Ping2":"109","Ping3":"99","Status":"OK"},' \
                        '{"HostName":"","IP":"172.23.119.2","PingTimeArray":["389","289","339"],"Ping1":"389",' \
                        '"Ping2":"289","Ping3":"339","Status":"OK"},{"HostName":"","IP":"41.21.232.82",' \
                        '"PingTimeArray":["89","79","79"],"Ping1":"89","Ping2":"79","Ping3":"79","Status":"OK"},' \
                        '{"HostName":"","IP":"10.118.46.166","PingTimeArray":[null,null,null],"Ping1":null,' \
                        '"Ping2":null,"Ping3":null,"Status":"Timeout"},{"HostName":"ae26-100-xcr1.lns.cw.net",' \
                        '"IP":"195.59.222.29","PingTimeArray":["219","218","209"],"Ping1":"219","Ping2":"218",' \
                        '"Ping3":"209","Status":"OK"},{"HostName":"ldn-b4-link.telia.net","IP":"213.248.75.169",' \
                        '"PingTimeArray":["309","188","189"],"Ping1":"309","Ping2":"188","Ping3":"189",' \
                        '"Status":"OK"},{"HostName":"edgecast-ic-306178-ldn-b5.c.telia.net","IP":"62.115.41.74",' \
                        '"PingTimeArray":["219","190","197"],"Ping1":"219","Ping2":"190","Ping3":"197",' \
                        '"Status":"OK"},{"HostName":"","IP":"192.229.182.48","PingTimeArray":["218","208","198"],' \
                        '"Ping1":"218","Ping2":"208","Ping3":"198","Status":"OK"}]}]},{"ASN":{"AsnID":"AS30986",' \
                        '"AsnName":"Scancom Ltd."},"Accuracy":0,"Country":{"CountryCode":"GH",' \
                        '"CountryFlag":"http:\/\/bscapi.blob.core.windows.net\/bsc-img-country-logos\/gh.png",' \
                        '"CountryName":"Ghana","State":"Greater Accra Region","StateCode":null},' \
                        '"DateTimeStamp":"\/Date(1499042322413+0000)\/","ID":88205432,"Location":{"Latitude":8,' \
                        '"Longitude":-2},"Network":{"CountryCode":null,"LogoURL":null,"NetworkID":"37181",' \
                        '"NetworkName":"Scancom Ltd."},"TRACERoute":[{"Destination":"konga.com",' \
                        '"HostName":"konga.com","IP":"192.229.182.48","Tracert":[{' \
                        '"HostName":"94-76-225-129.static.as29550.net","IP":"94.76.225.129","PingTimeArray":["137",' \
                        '"152","236"],"Ping1":"137","Ping2":"152","Ping3":"236","Status":"OK"},' \
                        '{"HostName":"cr0.rdg.as29550.net","IP":"92.48.95.61","PingTimeArray":["133","163","211"],' \
                        '"Ping1":"133","Ping2":"163","Ping3":"211","Status":"OK"},' \
                        '{"HostName":"ae1-cr0.the.as29550.net","IP":"91.186.5.249","PingTimeArray":["215","137",' \
                        '"225"],"Ping1":"215","Ping2":"137","Ping3":"225","Status":"OK"},{"HostName":"",' \
                        '"IP":"195.66.224.62","PingTimeArray":["139","147","134"],"Ping1":"139","Ping2":"147",' \
                        '"Ping3":"134","Status":"OK"},{"HostName":"","IP":"152.195.97.135","PingTimeArray":["147",' \
                        '"137","134"],"Ping1":"147","Ping2":"137","Ping3":"134","Status":"OK"},{"HostName":"",' \
                        '"IP":"192.16.28.89","PingTimeArray":["147","153","162"],"Ping1":"147","Ping2":"153",' \
                        '"Ping3":"162","Status":"OK"},{"HostName":"","IP":"192.229.182.48","PingTimeArray":["150",' \
                        '"152","135"],"Ping1":"150","Ping2":"152","Ping3":"135","Status":"OK"}]}]},' \
                        '{"ASN":{"AsnID":"AS37282","AsnName":"MAINONE"},"Accuracy":0,"Country":{"CountryCode":"GH",' \
                        '"CountryFlag":"http:\/\/bscapi.blob.core.windows.net\/bsc-img-country-logos\/gh.png",' \
                        '"CountryName":"Ghana","State":"","StateCode":null},"DateTimeStamp":"\/Date(' \
                        '1499042330477+0000)\/","ID":88052951,"Location":{"Latitude":5.55,"Longitude":-0.2167},' \
                        '"Network":{"CountryCode":null,"LogoURL":null,"NetworkID":"13455","NetworkName":"MAINONE"},' \
                        '"TRACERoute":[{"Destination":"konga.com","HostName":"konga.com","IP":"192.229.182.48",' \
                        '"Tracert":[{"HostName":"","IP":"10.0.2.100","PingTimeArray":[null,null,null],"Ping1":null,' \
                        '"Ping2":null,"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"45.222.194.33",' \
                        '"PingTimeArray":["50","36","59"],"Ping1":"50","Ping2":"36","Ping3":"59","Status":"OK"},' \
                        '{"HostName":"if-01.NG-CLS-PE-01.ngn.mainonecable.com","IP":"41.75.80.2","PingTimeArray":[' \
                        '"64","65","62"],"Ping1":"64","Ping2":"65","Ping3":"62","Status":"OK"},{"HostName":"",' \
                        '"IP":"10.0.100.5","PingTimeArray":["44","67","57"],"Ping1":"44","Ping2":"67","Ping3":"57",' \
                        '"Status":"OK"},{"HostName":"","IP":"","PingTimeArray":[null,null,null],"Ping1":null,' \
                        '"Ping2":null,"Ping3":null,"Status":"Timeout"},' \
                        '{"HostName":"ae-118-3504.edge3.london1.level3.net","IP":"4.69.166.142","PingTimeArray":[' \
                        '"140","157","122"],"Ping1":"140","Ping2":"157","Ping3":"122","Status":"OK"},{"HostName":"",' \
                        '"IP":"4.68.63.150","PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,"Ping3":null,' \
                        '"Status":"Timeout"},{"HostName":"edgecast.londra32.lon.seabone.net","IP":"89.221.43.253",' \
                        '"PingTimeArray":["146","153",null],"Ping1":"146","Ping2":"153","Ping3":null,' \
                        '"Status":"Timeout"},{"HostName":"","IP":"192.229.182.48","PingTimeArray":["158","151",' \
                        '"166"],"Ping1":"158","Ping2":"151","Ping3":"166","Status":"OK"}]}]},' \
                        '{"ASN":{"AsnID":"AS37623","AsnName":"SURFLINE_GHANA_AS"},"Accuracy":0,"Country":{' \
                        '"CountryCode":"GH",' \
                        '"CountryFlag":"http:\/\/bscapi.blob.core.windows.net\/bsc-img-country-logos\/gh.png",' \
                        '"CountryName":"Ghana","State":"Greater Accra Region","StateCode":null},' \
                        '"DateTimeStamp":"\/Date(1499042331148+0000)\/","ID":88194353,"Location":{"Latitude":5.55,' \
                        '"Longitude":-0.2167},"Network":{"CountryCode":null,"LogoURL":null,"NetworkID":"1199",' \
                        '"NetworkName":"Surfline_ghana_as"},"TRACERoute":[{"Destination":"konga.com",' \
                        '"HostName":"konga.com","IP":"192.229.182.48","Tracert":[{"HostName":"","IP":"",' \
                        '"PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},' \
                        '{"HostName":"","IP":"","PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,' \
                        '"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"172.21.12.202","PingTimeArray":["34",' \
                        '"31","29"],"Ping1":"34","Ping2":"31","Ping3":"29","Status":"OK"},{"HostName":"","IP":"",' \
                        '"PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},' \
                        '{"HostName":"","IP":"41.242.112.190","PingTimeArray":["123","137","132"],"Ping1":"123",' \
                        '"Ping2":"137","Ping3":"132","Status":"OK"},{"HostName":"","IP":"41.242.112.117",' \
                        '"PingTimeArray":["139","149","140"],"Ping1":"139","Ping2":"149","Ping3":"140",' \
                        '"Status":"OK"},{"HostName":"gigabitethernet1-0-3.pascr6.parispastourelle.opentransit.net",' \
                        '"IP":"193.251.255.57","PingTimeArray":["138","148","140"],"Ping1":"138","Ping2":"148",' \
                        '"Ping3":"140","Status":"OK"},' \
                        '{"HostName":"et-2-0-0-0.pastr3.parispastourelle.opentransit.net","IP":"193.251.129.45",' \
                        '"PingTimeArray":["141","138","148"],"Ping1":"141","Ping2":"138","Ping3":"148",' \
                        '"Status":"OK"},{"HostName":"","IP":"81.52.186.183","PingTimeArray":["139","141","136"],' \
                        '"Ping1":"139","Ping2":"141","Ping3":"136","Status":"OK"},{"HostName":"",' \
                        '"IP":"192.229.182.48","PingTimeArray":["139","140","147"],"Ping1":"139","Ping2":"140",' \
                        '"Ping3":"147","Status":"OK"}]}]},{"ASN":{"AsnID":"AS29614","AsnName":"VODAFONE GHANA AS ' \
                        'INTERNATIONAL TRANSIT"},"Accuracy":0,"Country":{"CountryCode":"GH",' \
                        '"CountryFlag":"http:\/\/bscapi.blob.core.windows.net\/bsc-img-country-logos\/gh.png",' \
                        '"CountryName":"Ghana","State":"Greater Accra Region","StateCode":null},' \
                        '"DateTimeStamp":"\/Date(1499042338952+0000)\/","ID":88141985,"Location":{"Latitude":5.55,' \
                        '"Longitude":-0.2167},"Network":{"CountryCode":null,"LogoURL":null,"NetworkID":"23920",' \
                        '"NetworkName":"Vodafone Ghana As International Transit"},"TRACERoute":[{' \
                        '"Destination":"konga.com","HostName":"konga.com","IP":"192.229.182.48","Tracert":[{' \
                        '"HostName":"","IP":"","PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,' \
                        '"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"","PingTimeArray":[null,null,null],' \
                        '"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"",' \
                        '"PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},' \
                        '{"HostName":"ffm-b2-link.telia.net","IP":"62.115.138.81","PingTimeArray":[null,null,null],' \
                        '"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"",' \
                        '"PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},' \
                        '{"HostName":"","IP":"","PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,' \
                        '"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"","PingTimeArray":[null,null,null],' \
                        '"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"",' \
                        '"PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"},' \
                        '{"HostName":"","IP":"","PingTimeArray":[null,null,null],"Ping1":null,"Ping2":null,' \
                        '"Ping3":null,"Status":"Timeout"},{"HostName":"","IP":"192.229.182.48","PingTimeArray":[null,' \
                        'null,null],"Ping1":null,"Ping2":null,"Ping3":null,"Status":"Timeout"}]}]}]} '

    def test_parse_response(self):
        url = 'https://kong.speedcheckerapi.com:8443/ProbeAPIService/Probes.svc/StartTracertTestByCountry?countrycode=GH&count=3&destination=jumia.com.ng&probeslimit=10&timeout=70000'
        pam = ProbeApiTraceroute()
        results = pam.process_response(self.PROBEAPI_RESPONSE, requested_url=url)
        return self.assertEqual(len(results), 6) and self.assertEqual([len(r.hops) for r in results], [8, 10, 7, 9, 10, 10])

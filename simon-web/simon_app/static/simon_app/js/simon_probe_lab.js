/*
 * JavaScript tester that is used to measure latency.
 * LACNIC - May 2014
 */

var simonURL = "http://200.10.62.135/";
var pointsURL = simonURL + "web_points/jsonpLatencyCallback/";
var amount = 4;
var testsConfigsURL = simonURL + "web_configs/";
var reportOfflineURL = simonURL + "postxmlresult/offline";
var postLatencyURL = simonURL + "postxmlresult/latency";
var ipv6ResolveURL = "http://simon.v6.labs.lacnic.net/cemd/getip";
var ipv4ResolveURL = "http://simon.v4.labs.lacnic.net/cemd/getip";

var siteOnLineTimeout = 6000;// ms
var latencyTimeout = 1000; // ms
var testType = 'tcp_web';
var countryCode = "";
var ipv4Adress = "";
var ipv6Address = "";

//var DEFAULT_TIME = -1;// default time for throughput results
var runLatency = true;
var runThroughput = false;
var runJitter = false;
var samples = 0;
var data = [];

function printr(text) {

    $('#console').append(text);
    $('#console').append('<br>');
    var y = $('#console').scrollTop();
    $('#console').scrollTop(y + 30);
}

function updateChart(rtt) {
    var i = Math.floor((rtt - MIN) / (MAX / CATEGORIES));
    var viejo = $('#container').highcharts().series[0].data[i]['y'];
    $('#container').highcharts().series[0].data[i].update(++viejo);

    $('#container').highcharts().setTitle({text: 'Distribución - ' + (data.length) + ' muestras<br>' + 'min/avg/max:   ' + getMin(data) + '/' + getMean(data) + '/' + getMax(data) + ' ms.'});
}

function iqr(a) {
    var l = a.length - 1, q1, q3, fw, b = [], i;

    q1 = (a[Math.floor(l * 0.25)] + a[Math.ceil(l * 0.25)]) / 2;
    q3 = (a[Math.floor(l * 0.75)] + a[Math.ceil(l * 0.75)]) / 2;

    fw = (q3 - q1) * 1.5;

    l++;

    for (i = 0; i < l && a[i] < q3 + fw; i++) {
        if (a[i] > q1 - fw) {
            b.push(a[i]);
        }
    }

    return b;
}

function getNumericalValues(dataSet) {
    // Gets numerical and positive values only
    if (dataSet instanceof Array && dataSet.length > 0) {
        var res = [];
        for (i in dataSet) {
            if (typeof dataSet[i] == 'number') {
                res.push(dataSet[i]);
            }
        }
        return res;
    }
    return 0;
}

function sortfunction(a, b) {
    /*
     * Causes an array to be sorted numerically and ascending.
     */
    return (a - b);
}

function getMin(dataSet) {
    if (dataSet instanceof Array && dataSet.length > 0) {
        dataSet.sort(function (a, b) {
            return a - b;
        });
        return dataSet[0];
    }
    return 0;
}

function getMax(dataSet) {
    if (dataSet instanceof Array && dataSet.length > 0) {
        dataSet.sort(function (a, b) {
            return a - b;
        });
        dataSet.reverse();
        return dataSet[0];
    }
    return 0;
}

function getMedian(dataSet) {

    if (dataSet instanceof Array && dataSet.length > 0) {
        // numeric comparator. Returns negative number if a < b, positive if a >
        // b
        // and 0 if they're equal
        // used to sort an array numerically
        dataSet.sort(function (a, b) {
            return a - b;
        });

        var half = Math.floor(dataSet.length / 2);

        if (dataSet.length % 2)
            return dataSet[half];
        else
            return Math.floor((dataSet[half - 1] + dataSet[half]) / 2.0);
    }
    return 0;
}

function getStdDev(dataSet) {
    if (dataSet instanceof Array && dataSet.length > 0) {
        var deviations = new Array(dataSet.length);
        var mean = getMean(dataSet);
        for (i in dataSet) {
            deviations.push(Math.pow((dataSet[i] - mean), 2));
        }
        if ((deviations.length - 1) != 0) {
            return Math.round(Math.sqrt(sum(deviations)
                / (deviations.length - 1)));
        }
    }
    return 0;
}

function getMean(dataSet) {
    if (dataSet instanceof Array && dataSet.length > 0) {

        return Math.floor(sum(dataSet) / dataSet.length);
    }
    return 0;
}

function sum(dataSet) {
    var sum = 0;
    if (dataSet instanceof Array) {
        for (i in dataSet) {
            if (typeof dataSet[i] == 'number') {
                sum += dataSet[i];
            }
        }
    }
    return sum;
}

function getLost(dataSet) {
    var lost = 0;
    if (dataSet instanceof Array && dataSet.length > 0) {
        for (i in dataSet) {
            if (typeof dataSet[i] != 'number') {
                lost++;
            }
        }
    }
    return lost;
}

LAB = {
    start: function (site) {
        printr("Measuring latency to " + site);

        for (var i = 0; i < 1500; i++) {
            var c = setTimeout(function () {
                LAB.latencyTest(site);
            }, latencyTimeout * i);
        }
    },

    latencyTest: function (ip) {

        var ts, rtt, IPVersion = this.getIPversion(ip);
        var url;
        if (IPVersion == '4') {
            url = "http://" + ip + "/" + Math.random();
        } else if (IPVersion == '6') {
            url = "http://[" + ip + "]/" + Math.random();
        } else {
            // abort
        }

        $.jsonp({
            type: 'GET',
            url: url,
            cache: false,
            dataType: 'jsonp',
            timeout: latencyTimeout,
            xhrFields: {
                withCredentials: true
            },

            beforeSend: function (xhr) {
                if (xhr.overrideMimeType) {
                    xhr.setRequestHeader("Connection", "close");
                }
                ts = +new Date;
            },

            error: function (xhr, textStatus, errorThrown) {
                // If there is an error and the site is up, we can suppose it is due to 404
                rtt = (+new Date - ts);
                printr(rtt + ' ms');
                if (textStatus != 'timeout' && rtt <= MAX) {
                    updateChart(rtt);
                    data.push(rtt);
                }
            },
        });
    },

    getIPversion: function (ip) {
        var ipv6regex = /([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{0,4}|:[0-9A-Fa-f]{1,4})?|(:[0-9A-Fa-f]{1,4}){0,2})|(:[0-9A-Fa-f]{1,4}){0,3})|(:[0-9A-Fa-f]{1,4}){0,4})|:(:[0-9A-Fa-f]{1,4}){0,5})((:[0-9A-Fa-f]{1,4}){2}|:(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])(\.(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])){3})|(([0-9A-Fa-f]{1,4}:){1,6}|:):[0-9A-Fa-f]{0,4}|([0-9A-Fa-f]{1,4}:){7}:/g;
        var ipv4regex = /(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/g;
        if (ipv4regex.test(ip)) {
            return '4';
        } else if (ipv6regex.test(ip)) {
            return '6';
        }
        return 1;
    }
}
/*
 * JavaScript probe that is hosted in different sites and harvests data as users visit that site.
 * LACNIC Labs - 2016
 */
SIMON = {};
SIMON.debug = false;
SIMON = {

    params: {
        percentage: 1.0,// 100%
        amount: 5,// amount of points
        numTests: 10,// amount of tests per point. Greater numTests --> less
        // error
        protocol: location.protocol === 'https:' && "https" || "http",
        post: true,
        print: true,
        console: 'console'
    },

    urls: {
        home: SIMON.debug && "http://127.0.0.1:8000/" || "https://simon.lacnic.net/",
        configs: SIMON.debug && "http://127.0.0.1:8000/web_configs/" || "https://simon.lacnic.net/web_configs/",
        offline: SIMON.debug && "http://127.0.0.1:8000/postxmlresult/offline/" || "https://simon.lacnic.net/postxmlresult/offline/",
        post: SIMON.debug && "http://127.0.0.1:8000/postxmlresult/latency/" || "https://simon.lacnic.net/postxmlresult/latency/",
        country: SIMON.debug && "http://127.0.0.1:8000/getCountry/" || "https://simon.lacnic.net/getCountry/",
        ipv6ResolveURL: "https://simon.v6.labs.lacnic.net/cemd/getip/jsonp/",
        ipv4ResolveURL: SIMON.debug && "http://127.0.0.1:8002/getip/" || "https://simon.v4.labs.lacnic.net/cemd/getip/jsonp/"
    },

    workflow: {
        latency: false,// TODO
        throughput: false
    },

    points: [],

    running: false,

    siteOnLineTimeout: 6000,
    latencyTimeout: 1000,
    testType: 'tcp_web',
    countryCode: "",
    ipv4Address: "",
    ipv6Address: "",
    DEFAULT_TIME: -1,

    before_start: function () {

    },

    after_end: function () {

    },

    before_each: function () {

    },

    after_each: function (rtt) {

    },

    after_points: function () {

    },

    init: function () {

        if (Math.random() < SIMON.params.percentage && SIMON.running == false) {
            SIMON.running = true;
            SIMON.before_start();
            return SIMON.getCountry();
        } else {
            SIMON.log("N/A");
        }
    },

    stop: function () {
        SIMON.printr("Stopping tests...it may take a while");
        SIMON.running = false;
    },

    getCountry: function () {

        SIMON.printr("Getting user country...");

        fetch(
            SIMON.urls.country
        ).then(
            function (r) {
                return r.text();
            }
        ).then(
            function (cc) {
                SIMON.countryCode = cc;
                SIMON.getMyIPAddress(SIMON.urls.ipv6ResolveURL);
            }
        );
    },

    getTestsConfigs: function () {

        /*
         * get the test configs from the server
         */
        SIMON.log("Fetching tests configurations...");

        fetch(SIMON.urls.configs).then(
            function (r) {
                return r.json();
            }
        ).then(
            function (data) {
                if (data.configs.run == 1) {
                    SIMON.workflow.run = true;
                } else {
                    SIMON.printr("Stopping script execution...");
                    return;
                }

                if (data.configs.latency == 1) {
                    SIMON.workflow.latency = true;
                } else {
                    SIMON.workflow.latency = false;
                }

                if (data.configs.throughput == 1) {
                    SIMON.workflow.throughput = true;
                } else {
                    SIMON.workflow.throughput = false;
                }

                if (SIMON.ipv6Address != "")
                    SIMON.getPoints(6);
                else
                    SIMON.getPoints(4);
            }
        )

    },

    getPoints: function (ipVersion) {

        fetch(
            SIMON.urls.home + "web_points?" +
            "amount=" + SIMON.params.amount +
            "&ip_version=" + ipVersion +
            "&countrycode=" + SIMON.countryCode +
            "&protocol=" + SIMON.params.protocol
        ).then(
            function (r) {
                return r.json();
            }
        ).then(
            function (data) {

                SIMON.points = new Array();

                /*
                 * callback when the points are loaded from the server
                 */

                for (i in data.points) {
                    var jsonPoint = data.points[i];
                    var testPoint = {
                        "ip": jsonPoint.ip,
                        "url": jsonPoint.url,
                        "country": jsonPoint.country,
                        "countryName": jsonPoint.countryName,
                        "city": jsonPoint.city,
                        "region": jsonPoint.region,
                        "results": [],  // holds the results of latency tests
                        "throughputResults": [],
                        "online": false,
                        "onlineFinished": false
                    };

                    SIMON.points.push(testPoint);
                }

                SIMON.after_points();
                SIMON.siteOnLine(SIMON.points[0]);

            }
        );

    },

    siteOnLine: function (testPoint) {

        const endpoint = SIMON.params.protocol == "https" && testPoint.url.split("://")[1].split("/")[0] || testPoint.ip;

        SIMON.printr("Checking site " + endpoint + " (" + testPoint.country + ") via " + SIMON.params.protocol.toUpperCase());

        /*
         * get the '/' directory
         */
        var url;
        if (SIMON.getIPversion(testPoint.ip) == 4)
            url = SIMON.params.protocol + "://" + endpoint + "/";
        else if (SIMON.getIPversion(testPoint.ip) == 6)
            url = SIMON.params.protocol + "://[" + endpoint + "]/";

        $.ajax({
            url: url,
            dataType: 'jsonp',
            crossDomain: true,
            context: this,
            timeout: SIMON.siteOnLineTimeout,
            complete: function (jqXHR, textStatus) {

                testPoint.onlineFinished = true;
                /*
                 * (useful) HTTP errors 2XX - Success 500-504 Server Error 401
                 * Unauthorized 407 Authentication required
                 */
                var pattern = /2[0-9]{2}|50[01234]|401|407/;

                if (pattern.test(jqXHR.status)) {
                    testPoint.online = true;
                } else {
                    testPoint.online = false;
                    /*
                     * report offline point
                     */
                    var array = [];
                    array.push(testPoint);
                    var xml = SIMON.buildOfflineXML(array);
                    SIMON.printr("Reporting offline test point...");
                    SIMON.postResults(SIMON.urls.offline, xml);
                }

                /*
                 * store results in global variable
                 */
                SIMON.saveTestPoint(testPoint);
                SIMON.startPointTest(testPoint);
            }
        });
    },

    saveTestPoint: function (testPoint) {
        /*
         * save test point to global variable 'points'
         */
        var index = this.getTestPointIndex(testPoint);
        SIMON.points[index] = testPoint;
    },

    startPointTest: function (testPoint) {
        if (testPoint.online) {
            // schedule latency tests
            var that = this;
            for (var i = 0; i < SIMON.params.numTests; i++) {
                setTimeout(function () {
                    SIMON.latencyTest(testPoint);
                }, SIMON.latencyTimeout * i);
            }
        } else {
            SIMON.abortTestPointTest(testPoint);
            var nextTestPoint = SIMON.getNextPoint(testPoint);
            if (nextTestPoint != -1) {
                SIMON.siteOnLine(nextTestPoint);
            }
        }
    },

    latencyTest: function (testPoint) {

        var ts, rtt;

        var url;

        const endpoint = SIMON.params.protocol == "https" && testPoint.url.split("://")[1].split("/")[0] || testPoint.ip;

        if (SIMON.getIPversion(testPoint.ip) == '6') {
            url = SIMON.params.protocol + "://[" + endpoint + "]?" + 'resource=' + Math.random();
        } else {
            url = SIMON.params.protocol + "://" + endpoint + "?" + 'resource=' + Math.random();
        }

        SIMON.before_each();

        $.jsonp({
            type: 'HEAD', //'GET', makes no difference :(
            url: url,
            dataType: 'jsonp',
            timeout: SIMON.latencyTimeout,
            xhrFields: {
                withCredentials: true
            },

            beforeSend: function (xhr) {
                if (xhr.overrideMimeType)
                    xhr.setRequestHeader("Connection", "close");
            },

            success: function () {

                SIMON.log('success');

            },

            error: function (jqXHR, textStatus) {
                if (textStatus == 'timeout') {
                    testPoint.results.push('timeout');

                } else {
                    /*
                     * If there is an error and the site is up, we can suppose
                     * it is due to 404
                     */
                    rtt = (+new Date - ts);
                    testPoint.results.push(rtt);
                    SIMON.log(rtt);
                    SIMON.after_each(rtt);
                }

                SIMON.saveTestPoint(testPoint);  // store results in global
                // variable

                if (SIMON.testerFinished(testPoint)) {  // post results

                    var array = [];
                    array.push(testPoint);

                    var xml;
                    if (SIMON.getIPversion(testPoint.ip) == '4') {
                        xml = SIMON.buildXML(array, SIMON.ipv4Address);

                    } else if (SIMON.getIPversion(testPoint.ip) == '6') {
                        xml = SIMON.buildXML(array, SIMON.ipv6Address);

                    }
                    SIMON.postResults(SIMON.urls.post, xml);

                    var nextTestPoint = SIMON.getNextPoint(testPoint);
                    if (nextTestPoint != -1) {

                        SIMON.siteOnLine(nextTestPoint);// ... and next tests

                    } else {
                        SIMON.after_end();
                        var thanks = "Thank you!";
                        SIMON.log(thanks);
                        SIMON.printr(thanks);
                    }
                }

            }
        });

        ts = +new Date;
    },

    abortTestPointTest: function (testPoint) {
        /*
         * fill remaining results with 'aborted'
         */

        for (var i = testPoint.results.length; i < SIMON.params.numTests; i++) {
            testPoint.results.push('aborted');
        }

        for (i in testPoint.throughputResults) {
            if (testPoint.throughputResults[i].time == SIMON.DEFAULT_TIME) {
                testPoint.throughputResults[i].time = 'aborted';
            }
        }
    },

    buildOfflineXML: function (offlinePoints) {
        if (offlinePoints instanceof Array) {

            var date = new Date();

            var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
            xml = xml
                + "<report xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">";

            for (i in offlinePoints) {
                xml = xml + "<point>";
                xml = xml + "<destination_ip>" + offlinePoints[i].ip
                    + "</destination_ip>";
                /*
                 * timezone?
                 */
                xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>";
                xml = xml + "</point>";

            }
            xml = xml + "</report>";

            return xml;
        }
        /*
         * error
         */
        return 1;
    },

    getMyIPAddress: function (url) {

        fetch(
            url
        ).then(
            function (r) {
                return r.json();
            }
        ).then(
            function (data) {
                SIMON.log('data ' + typeof data.ip);
                if (SIMON.getIPversion(data.ip) == '4') {
                    SIMON.ipv4Address = data.ip;
                    SIMON.getTestsConfigs();// exit

                } else if (SIMON.getIPversion(data.ip) == '6') {
                    SIMON.ipv6Address = data.ip;
                    SIMON.getMyIPAddress(SIMON.urls.ipv4ResolveURL);
                }
            },
            function (err) {
                SIMON.log('err ' + typeof err.ip);
                if (SIMON.ipv4Address == "")
                    SIMON.getMyIPAddress(SIMON.urls.ipv4ResolveURL);
            }
        );
    },

    getTestPointIndex: function (testPoint) {
        for (i in SIMON.points) {
            if (SIMON.points[i].ip == testPoint.ip) {
                return i;
            }
        }
        return null;
    },

    getNextPoint: function (testPoint) {
        var index = this.getTestPointIndex(testPoint);
        index++;
        if (index < SIMON.points.length) {
            return SIMON.points[index];
        } else {
            return -1;
        }
    },

    getPrintTimeWithOffset: function (date) {

        var hh = date.getHours().toString();
        var mm = date.getMinutes().toString();
        var ss = date.getSeconds().toString();

        while (hh.length < 2) {
            hh = '0' + hh;
        }
        while (mm.length < 2) {
            mm = '0' + mm;
        }
        while (ss.length < 2) {
            ss = '0' + ss;
        }

        var time = hh + ':' + mm + ':' + ss;
        var offset = SIMON.getPrintOffset(date);
        return time + offset;
    },

    buildXML: function (testPoints, origin_ip) {

        SIMON.printr("Building XML");

        if (testPoints instanceof Array && testPoints.length > 0) {
            var date = new Date();

            var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
            xml = xml + "<simon xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">";
            xml = xml + "<version>2</version>";
            xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>";
            xml = xml + "<time>" + SIMON.getPrintTimeWithOffset(date) + "</time>";
            xml = xml + "<local_country>" + SIMON.countryCode + "</local_country>";

            for (var i = 0; i < testPoints.length; i++) {

                var cleanResults = SIMON.quartiles.filter(SIMON.getNumericalValues(testPoints[i].results));
                if (testPoints[i].results.length != cleanResults.length) {
                    var diff = testPoints[i].results.length - cleanResults.length;
                    SIMON.log("Stripped " + diff + " outliers...");
                }
                SIMON.log(SIMON.summary(cleanResults));

                xml = xml + "<test>";
                xml = xml + "<destination_ip>" + testPoints[i].ip
                    + "</destination_ip>";
                xml = xml + "<origin_ip>" + origin_ip + "</origin_ip>";
                xml = xml + "<testtype>" + SIMON.testType + "</testtype>";

                xml = xml + "<number_probes>" + cleanResults.length
                    + "</number_probes>";
                xml = xml + "<min_rtt>"
                    + Math.floor(SIMON.getMin(cleanResults)) + "</min_rtt>";
                xml = xml + "<max_rtt>"
                    + Math.floor(SIMON.getMax(cleanResults)) + "</max_rtt>";
                xml = xml + "<ave_rtt>"
                    + Math.floor(SIMON.getMean(cleanResults))
                    + "</ave_rtt>";
                xml = xml + "<dev_rtt>"
                    + Math.floor(SIMON.getStdDev(cleanResults))
                    + "</dev_rtt>";
                xml = xml + "<median_rtt>"
                    + Math.floor(SIMON.getMedian(cleanResults))
                    + "</median_rtt>";
                xml = xml + "<packet_loss>"
                    + SIMON.getLost(testPoints[i].results)
                    + "</packet_loss>";
                xml = xml + "<ip_version>"
                    + SIMON.getIPversion(testPoints[i].ip)
                    + "</ip_version>";
                xml = xml + "</test>";
            }

            xml = xml + "<tester>JavaScript</tester>";
            xml = xml + "<tester_version>1</tester_version>";
            xml = xml + "<user_agent>" + navigator.userAgent + "</user_agent>";
            xml = xml + "<url>" + window.location.hostname + "</url>";
            xml = xml + "</simon>";

            SIMON.log("XML built");
            return xml;
        } else {
            SIMON.log("Trying to build Results XML with 0 points or points is not an array instance");
        }
    },

    getPrintOffset: function (date) {
        /*
         * Check if positive timezone offsets have the '+' sign...
         */
        var offset = date.getTimezoneOffset() * -1;
        var sign;
        if (offset <= 0) {
            sign = '-';
        } else {
            sign = '+';
        }
        var hh = (Math.floor(offset / 60)).toString();
        hh = hh.replace(/[+-]/, '');
        var mm = (offset % 60).toString();

        /*
         * -3:0 --> -03:00
         */
        while (mm.length < 2) {
            mm = '0' + mm;
        }
        while (hh.length < 2) {
            hh = '0' + hh;
        }

        return sign + hh + ":" + mm;
    },

    getNumericalValues: function (dataSet) {
        /*
         * Gets numerical and positive values only
         */
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
    },

    sortfunction: function (a, b) {
        /*
         * Causes an array to be sorted numerically and ascending.
         */
        return (a - b);
    },

    getMin: function (dataSet) {
        if (dataSet instanceof Array && dataSet.length > 0) {
            dataSet.sort(function (a, b) {
                return a - b;
            });
            return dataSet[0];
        }
        return 0;
    },

    getMax: function (dataSet) {
        if (dataSet instanceof Array && dataSet.length > 0) {
            dataSet.sort(function (a, b) {
                return a - b;
            });
            dataSet.reverse();
            return dataSet[0];
        }
        return 0;
    },

    getMedian: function (dataSet) {

        if (dataSet instanceof Array && dataSet.length > 0) {
            /*
             * numeric comparator. Returns negative number if a < b, positive if
             * a > b and 0 if they're equal used to sort an array numerically
             */
            dataSet.sort(function (a, b) {
                return a - b;
            });

            var half = Math.floor(dataSet.length / 2);

            if (dataSet.length % 2) {
                return dataSet[half];
            } else {
                return (dataSet[half - 1] + dataSet[half]) / 2.0;
            }
        }
        return 0;
    },

    getStdDev: function (dataSet) {
        if (dataSet instanceof Array && dataSet.length > 0) {
            var deviations = new Array(dataSet.length);
            var mean = this.getMean(dataSet);
            for (i in dataSet) {
                deviations.push(Math.pow((dataSet[i] - mean), 2));
            }
            if ((deviations.length - 1) != 0) {
                return Math.round(Math.sqrt(this.sum(deviations)
                    / (deviations.length - 1)));
            }
        }
        return 0;
    },

    getMean: function (dataSet) {
        if (dataSet instanceof Array && dataSet.length > 0) {

            return Math.floor(SIMON.sum(dataSet) / dataSet.length);
        }
        return 0;
    },

    quartiles: {
        q1: function (dataSet) {
            dataSet.sort(function (a, b) {
                return a - b;
            });
            return dataSet[Math.floor(0.25 * dataSet.length)];
        },

        q3: function (dataSet) {
            dataSet.sort(function (a, b) {
                return a - b;
            });
            return dataSet[Math.floor(0.75 * dataSet.length)];
        },

        iqr: function (dataSet) {
            return SIMON.quartiles.q3(dataSet) - SIMON.quartiles.q1(dataSet);
        },

        filter: function (dataSet) {
            var q1 = SIMON.quartiles.q1(dataSet);
            var q3 = SIMON.quartiles.q3(dataSet);
            var iqr = q3 - q1;
            return SIMON.stats.grater_than(SIMON.stats.lower_than(dataSet, q3 + 1.5 * iqr), q1 - 1.5 * iqr);
        }
    },

    stats: {
        grater_than: function (dataSet, value) {
            var res = [];
            for (i in dataSet) {
                if (dataSet[i] > value) {
                    res.push(dataSet[i]);
                }
            }
            return res;
        },

        lower_than: function (dataSet, value) {
            var res = [];
            for (i in dataSet) {
                if (dataSet[i] < value) {
                    res.push(dataSet[i]);
                }
            }
            return res;
        },

        log: function (dataSet) {
            var res = [];
            for (i in dataSet) {
                res.push(Math.log(dataSet[i]));
            }
            return res;
        },

        exp: function (dataSet) {
            var res = [];
            for (i in dataSet) {
                res.push(Math.exp(dataSet[i]));
            }
            return res;
        }
    },

    sum: function (dataSet) {
        var sum = 0;
        if (dataSet instanceof Array) {
            for (i in dataSet) {
                if (typeof dataSet[i] == 'number') {
                    sum += dataSet[i];
                }
            }
        }
        return sum;
    },

    getLost: function (dataSet) {
        var lost = 0;
        if (dataSet instanceof Array && dataSet.length > 0) {
            for (i in dataSet) {
                if (typeof dataSet[i] != 'number') {
                    lost++;
                }
            }
        }
        return lost;
    },

    getIPversion: function (ip) {
        if (ip.indexOf(":") > -1) {
            return '6';
        } else if (ip.indexOf(".") > -1) {
            return '4';
        }
        return -1;// error
    },

    testerFinished: function (testPoint) {
        if (testPoint.results.length == SIMON.params.numTests) {
            return true;
        }
        return false;
    },

    postResults: function (url, data) {

        if (!SIMON.params.post) {
            return false;
        }

        SIMON.printr("Posting results...");

        $.ajax({
            type: 'POST',
            url: url,
            data: data,
            success: function (xml) {
                return true;
            },
            error: function (xhr, status, error) {
                return false;
            }
        });
    },

    printr: function (text) {

        SIMON.log(text);

        if (SIMON.params.print && document.getElementById(SIMON.params.console) != null) {
            cur_html = $('#' + SIMON.params.console).html();
            $('#' + SIMON.params.console).html(cur_html + text + "<br>");
            var y = $('#' + SIMON.params.console).scrollTop();
            $('#' + SIMON.params.console).scrollTop(y + 30);
        }
    },

    log: function (text) {
        var HEADING = "[INFO] [" + new Date() + "] ";
        return console.log(HEADING + text);
    },

    warn: function (text) {
        var HEADING = "[WARN] [" + new Date() + "] ";
        return console.warn(HEADING + text);
    },

    error: function (text) {
        var HEADING = "[ERROR] [" + new Date() + "] ";
        return console.error(HEADING + text);
    },

    summary: function (dataSet) {
        return 'min=' + Math.floor(SIMON.getMin(dataSet)) + ' ms max=' + Math.floor(SIMON.getMax(dataSet)) + ' ms mean='
            + Math.floor(SIMON.getMean(dataSet)) + ' ms std. dev.=' + Math.floor(SIMON.getStdDev(dataSet)) + ' ms';
    }
};

var dateFormat = function () {
    var l = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g,
        m = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g,
        v = /[^-+\dA-Z]/g, d = function (a, c) {
            a = String(a);
            for (c = c || 2; a.length < c;)a = "0" + a;
            return a
        };
    return function (a, c, h) {
        var f = dateFormat;
        1 != arguments.length || "[object String]" != Object.prototype.toString.call(a) || /\d/.test(a) || (c = a, a = void 0);
        a = a ? new Date(a) : new Date;
        if (isNaN(a))throw SyntaxError("invalid date");
        c = String(f.masks[c] || c || f.masks["default"]);
        "UTC:" == c.slice(0, 4) && (c = c.slice(4), h = !0);
        var b = h ? "getUTC" : "get", g = a[b + "Date"](), p = a[b + "Day"](), k = a[b + "Month"](),
            q = a[b + "FullYear"](), e = a[b + "Hours"](), r = a[b + "Minutes"](), t = a[b + "Seconds"](),
            b = a[b + "Milliseconds"](), n = h ? 0 : a.getTimezoneOffset(), u = {
                d: g,
                dd: d(g),
                ddd: f.i18n.dayNames[p],
                dddd: f.i18n.dayNames[p + 7],
                m: k + 1,
                mm: d(k + 1),
                mmm: f.i18n.monthNames[k],
                mmmm: f.i18n.monthNames[k + 12],
                yy: String(q).slice(2),
                yyyy: q,
                h: e % 12 || 12,
                hh: d(e % 12 || 12),
                H: e,
                HH: d(e),
                M: r,
                MM: d(r),
                s: t,
                ss: d(t),
                l: d(b, 3),
                L: d(99 < b ? Math.round(b / 10) : b),
                t: 12 > e ? "a" : "p",
                tt: 12 > e ? "am" : "pm",
                T: 12 > e ? "A" : "P",
                TT: 12 > e ? "AM" : "PM",
                Z: h ? "UTC" : (String(a).match(m) || [""]).pop().replace(v, ""),
                o: (0 < n ? "-" : "+") + d(100 * Math.floor(Math.abs(n) / 60) + Math.abs(n) % 60, 4),
                S: ["th", "st", "nd", "rd"][3 < g % 10 ? 0 : (10 != g % 100 - g % 10) * g % 10]
            };
        return c.replace(l, function (a) {
            return a in u ? u[a] : a.slice(1, a.length - 1)
        })
    }
}();
dateFormat.masks = {
    "default": "ddd mmm dd yyyy HH:MM:ss",
    shortDate: "m/d/yy",
    mediumDate: "mmm d, yyyy",
    longDate: "mmmm d, yyyy",
    fullDate: "dddd, mmmm d, yyyy",
    shortTime: "h:MM TT",
    mediumTime: "h:MM:ss TT",
    longTime: "h:MM:ss TT Z",
    isoDate: "yyyy-mm-dd",
    isoTime: "HH:MM:ss",
    isoDateTime: "yyyy-mm-dd'T'HH:MM:ss",
    isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"
};
dateFormat.i18n = {
    dayNames: "Sun Mon Tue Wed Thu Fri Sat Sunday Monday Tuesday Wednesday Thursday Friday Saturday".split(" "),
    monthNames: "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec January February March April May June July August September October November December".split(" ")
};
Date.prototype.format = function (l, m) {
    return dateFormat(this, l, m)
};
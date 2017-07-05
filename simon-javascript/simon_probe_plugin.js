/*
 * JavaScript probe that is hosted in different sites and harvests data as users visit that site.
 * LACNIC Labs - 2017
 * agustin at lacnic dot net
 */

define(function () {

    _$ = require('jquery');

    var simon = {}

    simon.params = {
        percentage: 1.0,// 100%
        amount: 5,// amount of points
        numTests: 10,// amount of tests per point. Greater numTests --> less
        // error
        protocol: location.protocol === 'https:' && "https" || "http",
        post: true,
        log: false,
        print: false,
        console: 'console'
    };

    simon.urls = {
        home: "https://simon.lacnic.net/",
        configs: "https://simon.lacnic.net/web_configs/",
        offline: "https://simon.lacnic.net/postxmlresult/offline/",
        post: "https://simon.lacnic.net/postxmlresult/latency/",
        country: "https://simon.lacnic.net/getCountry/",
        ipv6ResolveURL: "https://simon.v6.labs.lacnic.net/cemd/getip/jsonp/",
        ipv4ResolveURL: "https://simon.v4.labs.lacnic.net/cemd/getip/jsonp/"
    };

    simon.debug = function () {
        this.urls = {
            home: "http://127.0.0.1:8000/",
            configs: "http://127.0.0.1:8000/web_configs/",
            offline: "http://127.0.0.1:8000/postxmlresult/offline/",
            post: "http://127.0.0.1:8000/postxmlresult/latency/",
            country: "http://127.0.0.1:8000/getCountry/",
            ipv6ResolveURL: "https://simon.v6.labs.lacnic.net/cemd/getip/jsonp/",
            ipv4ResolveURL: "http://127.0.0.1:8002/getip/"
        };

        this.params.log = true;
        this.params.print = true;
    }

    simon.messages = {
        thanks: "Thanks!"
    }

    simon.workflow = {
        latency: false,// TODO
        throughput: false
    };

    simon.points = [],

        simon.running = false,

        simon.siteOnLineTimeout = 3000,
        simon.latencyTimeout = 1000,
        simon.testType = 'tcp_web',
        simon.countryCode = "",
        simon.ipv4Address = "",
        simon.ipv6Address = "",
        simon.DEFAULT_TIME = -1,

        simon.before_start = function () {

        };

    simon.after_end = function () {

    };

    simon.before_each = function () {

    };

    simon.after_each = function (rtt) {

    };

    simon.after_points = function () {

    };

    simon.init = function (opts) {

        if (Math.random() < simon.params.percentage && simon.running == false) {
            simon.running = true;
            simon.before_start();
            return simon.getCountry();
        } else {
            simon.log("N/A");
        }
    };

    simon.stop = function () {
        simon.printr("Stopping tests...it may take a while");
        simon.running = false;
    };

    simon.getCountry = function () {

        simon.printr("Getting user country...");

        fetch(
            simon.urls.country
        ).then(
            function (r) {
                return r.text();
            }
        ).then(
            function (cc) {
                simon.countryCode = cc;
                simon.getMyIPAddress(simon.urls.ipv6ResolveURL);
            }
        );
    };

    simon.getTestsConfigs = function () {

        /*
         * get the test configs from the server
         */
        simon.log("Fetching tests configurations...");

        fetch(simon.urls.configs).then(
            function (r) {
                return r.json();
            }
        ).then(
            function (data) {
                if (data.configs.run == 1) {
                    simon.workflow.run = true;
                } else {
                    simon.printr("Stopping script execution...");
                    return;
                }

                if (data.configs.latency == 1) {
                    simon.workflow.latency = true;
                } else {
                    simon.workflow.latency = false;
                }

                if (data.configs.throughput == 1) {
                    simon.workflow.throughput = true;
                } else {
                    simon.workflow.throughput = false;
                }

                if (simon.ipv6Address != "")
                    simon.getPoints(6);
                else
                    simon.getPoints(4);
            }
        )

    };

    simon.getPoints = function (ipVersion) {

        fetch(
            simon.urls.home + "web_points?" +
            "amount=" + simon.params.amount +
            "&ip_version=" + ipVersion +
            "&countrycode=" + simon.countryCode +
            "&protocol=" + simon.params.protocol
        ).then(
            function (r) {
                return r.json();
            }
        ).then(
            function (data) {

                simon.points = new Array();

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

                    simon.points.push(testPoint);
                }

                simon.after_points();
                simon.siteOnLine(simon.points[0]);

            }
        );

    };

    simon.siteOnLine = function (testPoint) {

        const endpoint = simon.params.protocol == "https" && testPoint.url.split("://")[1].split("/")[0] || testPoint.ip;

        simon.printr("Checking site " + endpoint + " (" + testPoint.country + ") via " + simon.params.protocol.toUpperCase());

        /*
         * get the '/' directory
         */
        var url;
        if (simon.getIPversion(testPoint.ip) == 4)
            url = simon.params.protocol + "://" + endpoint + "/";
        else if (simon.getIPversion(testPoint.ip) == 6)
            url = simon.params.protocol + "://[" + endpoint + "]/";

        _$.ajax({
            url: url,
            type: 'HEAD',
            dataType: 'jsonp',
            crossDomain: true,
            context: this,
            timeout: simon.siteOnLineTimeout,
            error: function (jqXHR, textStatus, errorThrown) {

            },
            complete: function (jqXHR, textStatus) {

                testPoint.onlineFinished = true;
                testPoint.online = true;  // will be used later...

                /*
                 * (useful) HTTP errors 2XX - Success 500-504 Server Error 401
                 * Unauthorized 407 Authentication required
                 */

                if (jqXHR.status != 200) {

                    testPoint.online = false;

                    var array = [];
                    array.push(testPoint);
                    var xml = simon.buildOfflineXML(array);
                    simon.printr("Reporting offline test point...");
                    simon.postResults(simon.urls.offline, xml);

                }


                // var pattern = /2[0-9]{2}|50[01234]|401|407/;

                // if (pattern.test(jqXHR.status)) {
                // testPoint.online = true;
                // } else {

                // testPoint.online = false;
                // /*
                //  * report offline point
                //  */
                // var array = [];
                // array.push(testPoint);
                // var xml = simon.buildOfflineXML(array);
                // simon.printr("Reporting offline test point...");
                // simon.postResults(simon.urls.offline, xml);
                // }

                /*
                 * store results in global variable
                 */
                simon.saveTestPoint(testPoint);
                simon.startPointTest(testPoint);
            }
        });
    };

    simon.saveTestPoint = function (testPoint) {
        /*
         * save test point to global variable 'points'
         */
        var index = this.getTestPointIndex(testPoint);
        simon.points[index] = testPoint;
    };

    simon.startPointTest = function (testPoint) {
        if (testPoint.online) {
            // schedule latency tests
            var that = this;
            for (var i = 0; i < simon.params.numTests; i++) {
                setTimeout(function () {
                    simon.latencyTest(testPoint);
                }, simon.latencyTimeout * i);
            }
        } else {
            simon.abortTestPointTest(testPoint);
            var nextTestPoint = simon.getNextPoint(testPoint);
            if (nextTestPoint != -1) {
                simon.siteOnLine(nextTestPoint);
            }
        }
    };

    simon.latencyTest = function (testPoint) {

        var ts, rtt;

        var url;

        const endpoint = simon.params.protocol == "https" && testPoint.url.split("://")[1].split("/")[0] || testPoint.ip;

        if (simon.getIPversion(testPoint.ip) == '6') {
            url = simon.params.protocol + "://[" + endpoint + "]?" + 'resource=' + Math.random();
        } else {
            url = simon.params.protocol + "://" + endpoint + "?" + 'resource=' + Math.random();
        }

        simon.before_each();

        _$.jsonp({
            type: 'HEAD', //'GET', makes no difference :(
            url: url,
            crossDomain: true,
            cache: false,
            dataType: 'html',  // 'jsonp',
            timeout: simon.latencyTimeout,
            xhrFields: {
                withCredentials: true
            },

            beforeSend: function (xhr) {
                if (xhr.overrideMimeType)
                    xhr.setRequestHeader("Connection", "close");

                // xhr.setRequestHeader("Accept", "text/html");
            },

            success: function () {

                simon.log('success');

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
                    simon.after_each(rtt);
                }

                simon.saveTestPoint(testPoint);  // store results in global
                // variable

                if (simon.testerFinished(testPoint)) {  // post results

                    var array = [];
                    array.push(testPoint);

                    var xml;
                    if (simon.getIPversion(testPoint.ip) == '4') {
                        xml = simon.buildXML(array, simon.ipv4Address);

                    } else if (simon.getIPversion(testPoint.ip) == '6') {
                        xml = simon.buildXML(array, simon.ipv6Address);

                    }
                    simon.postResults(simon.urls.post, xml);

                    var nextTestPoint = simon.getNextPoint(testPoint);
                    if (nextTestPoint != -1) {

                        simon.siteOnLine(nextTestPoint);// ... and next tests

                    } else {
                        simon.after_end();
                        simon.printr(simon.messages.thanks);
                    }
                }

            }
        });

        ts = +new Date;
    };

    simon.abortTestPointTest = function (testPoint) {
        /*
         * fill remaining results with 'aborted'
         */

        for (var i = testPoint.results.length; i < simon.params.numTests; i++) {
            testPoint.results.push('aborted');
        }

        for (i in testPoint.throughputResults) {
            if (testPoint.throughputResults[i].time == simon.DEFAULT_TIME) {
                testPoint.throughputResults[i].time = 'aborted';
            }
        }
    };

    simon.buildOfflineXML = function (offlinePoints) {
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
    };

    simon.getMyIPAddress = function (url) {

        fetch(
            url
        ).then(
            function (r) {
                return r.json();
            }
        ).then(
            function (data) {
                if (simon.getIPversion(data.ip) == '4') {
                    simon.ipv4Address = data.ip;
                    simon.getTestsConfigs();// exit

                } else if (simon.getIPversion(data.ip) == '6') {
                    simon.ipv6Address = data.ip;
                    simon.getMyIPAddress(simon.urls.ipv4ResolveURL);
                }
            },
            function (err) {
                if (simon.ipv4Address == "")
                    simon.getMyIPAddress(simon.urls.ipv4ResolveURL);
            }
        );
    };

    simon.getTestPointIndex = function (testPoint) {
        for (i in simon.points) {
            if (simon.points[i].ip == testPoint.ip) {
                return i;
            }
        }
        return null;
    };

    simon.getNextPoint = function (testPoint) {
        var index = this.getTestPointIndex(testPoint);
        index++;
        if (index < simon.points.length) {
            return simon.points[index];
        } else {
            return -1;
        }
    };

    simon.getPrintTimeWithOffset = function (date) {

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
        var offset = simon.getPrintOffset(date);
        return time + offset;
    };

    simon.buildXML = function (testPoints, origin_ip) {

        simon.printr("Building XML");

        if (testPoints instanceof Array && testPoints.length > 0) {
            var date = new Date();

            var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
            xml = xml + "<simon xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">";
            xml = xml + "<version>2</version>";
            xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>";
            xml = xml + "<time>" + simon.getPrintTimeWithOffset(date) + "</time>";
            xml = xml + "<local_country>" + simon.countryCode + "</local_country>";

            for (var i = 0; i < testPoints.length; i++) {

                var cleanResults = simon.quartiles.filter(simon.getNumericalValues(testPoints[i].results));
                if (testPoints[i].results.length != cleanResults.length) {
                    var diff = testPoints[i].results.length - cleanResults.length;
                    simon.log("Stripped " + diff + " outliers...");
                }
                simon.log(simon.summary(cleanResults));

                xml = xml + "<test>";
                xml = xml + "<destination_ip>" + testPoints[i].ip
                    + "</destination_ip>";
                xml = xml + "<origin_ip>" + origin_ip + "</origin_ip>";
                xml = xml + "<testtype>" + simon.testType + "</testtype>";

                xml = xml + "<number_probes>" + cleanResults.length
                    + "</number_probes>";
                xml = xml + "<min_rtt>"
                    + Math.floor(simon.getMin(cleanResults)) + "</min_rtt>";
                xml = xml + "<max_rtt>"
                    + Math.floor(simon.getMax(cleanResults)) + "</max_rtt>";
                xml = xml + "<ave_rtt>"
                    + Math.floor(simon.getMean(cleanResults))
                    + "</ave_rtt>";
                xml = xml + "<dev_rtt>"
                    + Math.floor(simon.getStdDev(cleanResults))
                    + "</dev_rtt>";
                xml = xml + "<median_rtt>"
                    + Math.floor(simon.getMedian(cleanResults))
                    + "</median_rtt>";
                xml = xml + "<packet_loss>"
                    + simon.getLost(testPoints[i].results)
                    + "</packet_loss>";
                xml = xml + "<ip_version>"
                    + simon.getIPversion(testPoints[i].ip)
                    + "</ip_version>";
                xml = xml + "</test>";
            }

            xml = xml + "<tester>JavaScript</tester>";
            xml = xml + "<tester_version>1</tester_version>";
            xml = xml + "<user_agent>" + navigator.userAgent + "</user_agent>";
            xml = xml + "<url>" + window.location.hostname + "</url>";
            xml = xml + "</simon>";

            simon.log("XML built");
            return xml;
        } else {
            simon.log("Trying to build Results XML with 0 points or points is not an array instance");
        }
    };

    simon.getPrintOffset = function (date) {
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
    };

    simon.getNumericalValues = function (dataSet) {
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
    };

    simon.sortfunction = function (a, b) {
        /*
         * Causes an array to be sorted numerically and ascending.
         */
        return (a - b);
    };

    simon.getMin = function (dataSet) {
        if (dataSet instanceof Array && dataSet.length > 0) {
            dataSet.sort(function (a, b) {
                return a - b;
            });
            return dataSet[0];
        }
        return 0;
    };

    simon.getMax = function (dataSet) {
        if (dataSet instanceof Array && dataSet.length > 0) {
            dataSet.sort(function (a, b) {
                return a - b;
            });
            dataSet.reverse();
            return dataSet[0];
        }
        return 0;
    };

    simon.getMedian = function (dataSet) {

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
    };

    simon.getStdDev = function (dataSet) {
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
    };

    simon.getMean = function (dataSet) {
        if (dataSet instanceof Array && dataSet.length > 0) {

            return Math.floor(simon.sum(dataSet) / dataSet.length);
        }
        return 0;
    };

    simon.quartiles = {
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
            return simon.quartiles.q3(dataSet) - simon.quartiles.q1(dataSet);
        },

        filter: function (dataSet) {
            var q1 = simon.quartiles.q1(dataSet);
            var q3 = simon.quartiles.q3(dataSet);
            var iqr = q3 - q1;
            return simon.stats.grater_than(simon.stats.lower_than(dataSet, q3 + 1.5 * iqr), q1 - 1.5 * iqr);
        }
    };

    simon.stats = {
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
    };

    simon.sum = function (dataSet) {
        var sum = 0;
        if (dataSet instanceof Array) {
            for (i in dataSet) {
                if (typeof dataSet[i] == 'number') {
                    sum += dataSet[i];
                }
            }
        }
        return sum;
    };

    simon.getLost = function (dataSet) {
        var lost = 0;
        if (dataSet instanceof Array && dataSet.length > 0) {
            for (i in dataSet) {
                if (typeof dataSet[i] != 'number') {
                    lost++;
                }
            }
        }
        return lost;
    };

    simon.getIPversion = function (ip) {
        if (ip.indexOf(":") > -1) {
            return '6';
        } else if (ip.indexOf(".") > -1) {
            return '4';
        }
        return -1;// error
    };

    simon.testerFinished = function (testPoint) {
        if (testPoint.results.length == simon.params.numTests) {
            return true;
        }
        return false;
    };

    simon.postResults = function (url, data) {

        if (!simon.params.post) {
            return false;
        }

        simon.printr("Posting results...");

        _$.ajax({
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
    };

    simon.printr = function (text) {

        simon.log(text);

        if (simon.params.print && document.getElementById(simon.params.console) != null) {
            cur_html = _$('#' + simon.params.console).html();
            _$('#' + simon.params.console).html(cur_html + text + "<br>");
            var y = _$('#' + simon.params.console).scrollTop();
            _$('#' + simon.params.console).scrollTop(y + 30);
        }
    };

    simon.log = function (text) {

        if (simon.params.log) {
            var HEADING = "[INFO] [" + new Date() + "] ";
            console.log(HEADING + text);
        }
    };

    simon.warn = function (text) {

        if (simon.params.log) {
            var HEADING = "[WARN] [" + new Date() + "] ";
            console.warn(HEADING + text);
        }
    };

    simon.error = function (text) {

        if (simon.params.log) {
            var HEADING = "[ERROR] [" + new Date() + "] ";
            console.error(HEADING + text);
        }
    };

    simon.summary = function (dataSet) {
        return 'min=' + Math.floor(simon.getMin(dataSet)) + ' ms max=' + Math.floor(simon.getMax(dataSet)) + ' ms mean='
            + Math.floor(simon.getMean(dataSet)) + ' ms std. dev.=' + Math.floor(simon.getStdDev(dataSet)) + ' ms';
    }

    return simon;
});
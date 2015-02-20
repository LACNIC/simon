/**
 * Latency measurement code.
 * LACNIC 2012
 */

var numTests = 5; // Tests per test point.
numTests = numTests + 1; // DNS
var testType = 'tcp_web';
var points = new Array();// global variable. Holds the test points.
var local_country;
var latencyTimeout = 1000; // ms
var iframe;
var auxTestPoint;// dirty dirty...sorry :-(

//var base_url = window.location.host;
//var postLatencyURL = "http://" + base_url + "/simon/postxmlresult/latency";
var postLatencyURL = "http://127.0.0.1:8000/postxmlresult/latency"; // "http://simon.labs.lacnic.net/simon/postxmlresult"
var ipv6ResolveURL = "http://simon.v6.labs.lacnic.net/cemd/getip";
var ipv4ResolveURL = "http://simon.v4.labs.lacnic.net/cemd/getip";

/* hook code to onLoad event */
$(document).ready(function () {

    $('#tabs').hide();// wait for preprocessing of the table data
    getTestsConfigs();
    jQuery.support.cors = true;

    // iframe where images are loaded
    iframe = document.createElement("iframe");// global variable
    iframe.id = "iframe";
    iframe.style.display = "none";
    document.body.appendChild(iframe);
});

/*function startLatencyTests() {
 // Starts latency testers for all points

 if(setCountry()){
 // Schedule tests
 // points = removeSameCountryTestPoints(points, local_country);
 for (j in points){
 for (var i=0; i<numTests; i++){
 setTimeout(latencyTest, latencyTimeout 500  * (i + j * numTests) + 10, points[j]);// 10 milliseconds to process each test
 }
 }
 }
 }*/

function latencyTest(testPoint) {

    printr("Measuring latency to " + testPoint.url + " (" + testPoint.country + ")");

    var ts, rtt;
    var url = "http://" + testPoint.ip + "/" + Math.random();

    $.jsonp({
        type: 'GET',
        url: url,
        dataType: 'jsonp',
        timeout: latencyTimeout,
        xhrFields: {
            withCredentials: true
        },

        beforeSend: function (xhr) {
            if (xhr.overrideMimeType) {
                xhr.setRequestHeader("Connection", "close");
            }
        },

        error: function (xhr, textStatus, errorThrown) {
            if (textStatus == 'timeout') {

                testPoint.results.push('timeout');
            } else {
                // If there is an error and the site is up, we can suppose it
                // is due to 404
                rtt = (+new Date - ts);
                testPoint.results.push(rtt);

                updateLatency(testPoint);// graphical
            }
            saveTestPoint(testPoint);// store results in global variable


            if (testerFinished(testPoint)) {
                //post test point results
                auxTestPoint = testPoint;

                //Force to get the v4 or v6 IP address
                // getMyIPAddress triggers the POST and next point test
                if (getIPversion(testPoint.ip) == '4') {
                    getMyIPAddress(ipv4ResolveURL + '/jsonp/getMyIPAddressCallback');
                } else if (getIPversion(testPoint.ip) == '6') {
                    getMyIPAddress(ipv6ResolveURL + '/jsonp/getMyIPAddressCallback');
                }
            }

        }
    });

    ts = +new Date;
}

function saveTestPoint(testPoint) {
    //save test point to global variable 'points'

    var index = getTestPointIndex(testPoint);
    points[index] = testPoint;
}

function getTestPointIndex(testPoint) {
    for (i in points) {
        if (points[i].ip == testPoint.ip) {
            return i;
        }
    }
    return null;
}

function getNextPoint(testPoint) {
    var index = getTestPointIndex(testPoint);
    index++;
    return points[index];
}

function getTestPointByIp(ip) {
    for (i in points) {
        if (points[i].ip == ip) {
            return points[i];
        }
    }
}

/*function endTests() {
 var xml = buildXML(points);
 postResults(postURL, xml);

 // Start the throughput tests.......
 if(runThroughput){
 startThroughputTests();
 }else{
 alert("All tests finished. Thank you!");
 }
 }*/

function removeSameCountryTestPoints(testPoints, country) {
    /*
     * Not working properly
     */
    for (i in testPoints) {
        if (testPoints[i].country == country) {
            testPoints.splice(i, 1);
        }
    }
    return testPoints;
}

function testersFinished() {
    /*
     * Latency testers....
     */
    for (i in points) {
        if (!testerFinished(points[i])) {
            return false;
        }
    }
    return true;
}

function testerFinished(testPoint) {
    if (testPoint.results.length == numTests) {
        return true;
    }
    return false;
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
        // numeric comparator. Returns negative number if a < b, positive if a > b
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
            return Math.round(Math.sqrt(sum(deviations) / (deviations.length - 1)));
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

function getMeanWithoutDNSQuery(dataSet) {
    if (dataSet instanceof Array && dataSet.length > 0) {
        var aux = [];
        for (i in dataSet) {
            if (i != 0) {
                // Exclude DNS Query (1st result)
                aux[i - 1] = dataSet[i];
            }
        }
        return Math.floor(sum(aux) / aux.length);
    }
    return 0;
}

function getCountryMean(countryCode) {
    // Latency mean
    var res = 0;
    var totalSamples = 0;
    var countryPoints = getCountryPoints(countryCode);

    for (i in countryPoints) {
        var pointSamples = countryPoints[i].results.length - 1;
        var pointMean = 0;
        if (pointSamples > 0) {
            // NaN
            pointMean = getMeanWithoutDNSQuery(countryPoints[i].results);
            res = res + pointSamples * pointMean;
            totalSamples = totalSamples + pointSamples;
        }

    }
    return Math.floor(res / totalSamples);
}

function getCountryThroughputMean(countryCode) {
    var res = 0;
    var totalSamples = 0;
    var countryPoints = getCountryPoints(countryCode);

    for (i in countryPoints) {
        var pointSamples = countryPoints[i].throughputResults.length;
        var pointMean = 0;
        if (pointSamples > 0) {
            // NaN
            pointMean = getMean(countryPoints[i].throughputResults);
            res = res + pointSamples * pointMean;
            totalSamples = totalSamples + pointSamples;
        }

    }
    return Math.floor(res / totalSamples);
}

function isEven(value) {
    if (value % 2 == 0)
        return true;
    else
        return false;
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

function getCount(dataSet) {
    if (dataSet instanceof Array && dataSet.length > 0) {
        return numTests - getLost(dataSet);
    }
    return 0;
}

function getCountryLatencyPercentage(countryCode) {

    var countryPoints = getCountryPoints(countryCode);
    // countryPoints = getOnlinePoints( countryPoints );

    var done = 0;
    for (i in countryPoints) {
        done = done + countryPoints[i].results.length;
    }
    return Math.floor(done * 100 / (numTests * countryPoints.length));
}


function getIPversion(ip) {
    var ipv6regex = /([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:([0-9A-Fa-f]{1,4}:[0-9A-Fa-f]{0,4}|:[0-9A-Fa-f]{1,4})?|(:[0-9A-Fa-f]{1,4}){0,2})|(:[0-9A-Fa-f]{1,4}){0,3})|(:[0-9A-Fa-f]{1,4}){0,4})|:(:[0-9A-Fa-f]{1,4}){0,5})((:[0-9A-Fa-f]{1,4}){2}|:(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])(\.(25[0-5]|(2[0-4]|1[0-9]|[1-9])?[0-9])){3})|(([0-9A-Fa-f]{1,4}:){1,6}|:):[0-9A-Fa-f]{0,4}|([0-9A-Fa-f]{1,4}:){7}:/g;
    var ipv4regex = /(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/g;
    if (ipv4regex.test(ip)) {
        return '4';
    } else if (ipv6regex.test(ip)) {
        return '6';
    }
    return 1;// error
}

function clean(dataSet) {
    /*
     * Removes greatest value (DNS query) and non-numerical values (timeout,
     * etc)
     */
    if (dataSet instanceof Array && dataSet.length > 0) {
        for (i in dataSet) {
            if (!(typeof dataSet[i] === 'number')) {
                dataSet.splice(i, 1);
            }
        }
        dataSet.sort(function (a, b) {
            return a - b;
        });
        dataSet.reverse();
        dataSet.splice(0, 1);
        return dataSet;
    }
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

function getPrintTimeWithOffset(date) {
    var time = date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();//date.toLocaleTimeString();
    var offset = getPrintOffset(date);
    return time + offset;
}

function getPrintOffset(date) {
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

    // -3:0 --> -03:00
    while (mm.length < 2) {
        mm = '0' + mm;
    }
    while (hh.length < 2) {
        hh = '0' + hh;
    }

    return sign + hh + ":" + mm;
}

function buildXML(testPoints, origin_ip) {
    if (testPoints instanceof Array && testPoints.length > 0) {
        var date = new Date();

        var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
        xml = xml + "<simon xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n";
        xml = xml + "<version>2</version>\n";
        xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>\n";
        xml = xml + "<time>" + getPrintTimeWithOffset(date) + "</time>\n";
        xml = xml + "<local_country>" + local_country + "</local_country>\n";

        for (var i = 0; i < testPoints.length; i++) {

            // var lost = getLost(testPoints[i].results);
            var cleanResults = getNumericalValues(testPoints[i].results);// calculate
            // with
            // "clean"
            // values


            xml = xml + "<test>\n";
            xml = xml + "<destination_ip>" + testPoints[i].ip + "</destination_ip>\n";
            xml = xml + "<origin_ip>" + origin_ip + "</origin_ip>\n";
            xml = xml + "<testtype>" + testType + "</testtype>\n";
            // xml = xml + "<number_probes>" + getCount(testPoints[i].results) +
            // "</number_probes>\n";
            xml = xml + "<number_probes>" + testPoints[i].results.length + "</number_probes>\n";
            xml = xml + "<min_rtt>" + getMin(cleanResults) + "</min_rtt>\n";
            xml = xml + "<max_rtt>" + getMax(cleanResults) + "</max_rtt>\n";
            xml = xml + "<ave_rtt>" + getMean(cleanResults) + "</ave_rtt>\n";
            xml = xml + "<dev_rtt>" + getStdDev(cleanResults) + "</dev_rtt>\n";
            xml = xml + "<median_rtt>" + getMedian(cleanResults) + "</median_rtt>\n";
            xml = xml + "<packet_loss>" + getLost(testPoints[i].results) + "</packet_loss>\n";
            xml = xml + "<ip_version>" + getIPversion(testPoints[i].ip) + "</ip_version>\n";
            xml = xml + "</test>\n";
        }

        xml = xml + "<tester>JavaScript</tester>\n";
        xml = xml + "<tester_version>1</tester_version>\n";
        xml = xml + "</simon>\n\n";

        return xml;
    }
}

function postResults(url, data) {
    $.ajax({
        type: 'POST',
        url: url,
        data: data,
        success: function (xml) {
            printr("Results were posted successfully!");
            return true;
        },
        error: function (xhr, status, error) {
            printr("Error while posting the test results on the server.");
            return false;
        }
    });
}
/**
 * Throughput measurement code.
 * LACNIC 2012
 */

var timeoutHandler;
var busy = false;// global variable to determine if a tester is working
// (using resources) or not
var imagesIndex = 0;

var base_url = window.location.host;
var postThroughputURL = "http://" + base_url + "/simon/postxmlresult/throughput";
//var postThroughputURL = "http://127.0.0.1:8000/postxmlresult/throughput";

function throughputTest(testPoint, index) {

    busy = true;// locks resources

    printr("Measuring throughput to " + testPoint.url + " (" + testPoint.country + ")");

    if (location.protocol == 'https') {
        // SSL delay would result in more time ==> less bandwith
        printr("The connection with the URL " + testPoint.url + " (" + testPoint.country + ") was over HTTPS, canceling test...");
        endThroughputTest(testPoint, 'error', index);
    }

    timeoutHandler = setTimeout(function () {
        // set timeout
        endThroughputTest(testPoint, 'timeout', index);
    }, /* throughputTestTimeout */testPoint.throughputResults[index].timeout);


    iframe.onload = function () { // Define the callback method.
        iframe.onload = null;
        iframe.onerror = null;
        endThroughputTest(testPoint, startTime, index);
    };

    iframe.onerror = function () {
        // Error callback
        // triggered by a real network timeout
        // the image stops downloading. The testers frees resources and lets the
        // next tester start
        iframe.onload = null;
        iframe.onerror = null;
        endThroughputTest(testPoint, 'error', index);
    };
    // reload.
    var url = "http://" + testPoint.ip + testPoint.throughputResults[index].path + '/' + testPoint.throughputResults[index].name;
    var startTime = new Date();
    iframe.src = url;
}

function endThroughputTest(testPoint, startTime, index/* result index */) {

    var endTime = new Date();
    clearTimeout(timeoutHandler);

    if (startTime == 'timeout') {

        // Timeout does not abort the download of the current image.
        // We still need to wait for the onload or onerror events fire for the
        // current download to end.
        // That way only one image uses bandwidth at any given time.


        testPoint.throughputResults[index].time = 'timeout';
    } else if (startTime == 'error') {
        // true error (resource may be unavailable)
        // triggered by the onerror event

        busy = false;// free resources

    } else {
        // normal flow
        // triggered by the onload event
        busy = false;// free resources
        iframe.src = null;
        //iframe.src = '';

        var time = endTime - startTime - getMean(testPoint.results);// throughput
        // RTT minus
        // one
        // latency
        // RTT
        if (testPoint.throughputResults[index].time == DEFAULT_TIME) {// save only
            // if test
            // proceeded
            // correctly,
            // else is a
            // late test
            testPoint.throughputResults[index].time = time;
        }
    }

    saveTestPoint(testPoint);// save to global variable

    updateThroughput(testPoint);// graphical

    if (throughputTesterFinished(testPoint) && !busy) {// not busy --> if last
        // test timed out and is
        // waiting for error...

        // post test point results
        var array = [];
        array.push(testPoint);// post 1-point 'simon' array
        var xml = buildThroughputXML(array);
        postResults(postThroughputURL, xml);

        // Next test point
        imagesIndex = 0;// reset images

        var newTestPoint = getNextPoint(testPoint);
        siteOnLine(newTestPoint);
    } else if (!busy) {

        // next image
        imagesIndex++;

        throughputTest(testPoint, imagesIndex);
    }
    // wait for finish or callback... :-P
}

function throughputTesterFinished(testPoint) {
    for (i in testPoint.throughputResults) {
        if (testPoint.throughputResults[i].time == DEFAULT_TIME) {
            return false;
        }
    }
    return true;
}


function getTestPointThroughputTimes(testPoint) {
    // returns array of times
    var res = [];
    for (i in testPoint.throughputResults) {
        res.push(testPoint.throughputResults[i].time);
    }
    return res;
}
function getNonZeroSamples(testPoint) {
    // returns the non zero times
    var array = getTestPointThroughputTimes(testPoint);
    for (i in array) {
        if (array[i] == DEFAULT_TIME) {
            array.splice(i, 1);
            i--;// consider the shift
        }
    }
    return array;
}
function getTestPointThroughputSizes(testPoint) {
    var res = [];
    for (i in testPoint.throughputResults) {
        res.push(testPoint.throughputResults[i].byteSize);
    }
    return res;
}
function getNonZeroThroughputSizes(testPoint) {
    // returns the sizes correspondig to non zero times
    var array = getTestPointThroughputSizes(testPoint);
    for (i in array) {
        if (array[i] == 0) {
            array.splice(i, 1);
            i--;
        }
    }
    return array;
}
function getMeanThroughput(testPoint) {
    // Bytes / milliseconds
    var time = 0
    var size = 0;
    for (i in testPoint.throughputResults) {
        var thput = testPoint.throughputResults[i];
        if ((typeof thput.time === 'number') && (thput.time > 0)) {
            //alert(thput.time + ' ms - ' + thput.byteSize + ' B');
            time += thput.time;
            size += thput.byteSize;
        }
    }
    /*var time = sum(getTestPointThroughputTimes(testPoint));
     var size = sum(getTestPointThroughputSizes(testPoint));*/
    return Math.floor(size / time);
}

/*function getCountryThroughputMean(countryCode){
 // time mean, not bps mean
 var times = [];
 //var res = 0;
 //var totalSamples = 0;
 var countryPoints = getCountryPoints(countryCode);

 for(i in countryPoints){
 var pointSamples = getNonZeroSamples(countryPoints[i]);
 for(j in pointSamples){
 times.push(pointSamples[j]);
 }
 }
 return sum(times) / times.length;
 }*/
function getCountryThroughputSizes(countryCode) {
    // array of image sizes corresponding to non zero results

    var res = [];
    var countryPoints = getCountryPoints(countryCode);
    for (i in countryPoints) {
        var pointSizes = getNonZeroThroughputSizes(countryPoints[i]);// filters 0
        pointSizes = getNumericalValues(pointSizes);// filters 'timeout' or 'aborted'
        for (j in pointSizes) {
            res.push(pointSizes[j]);
        }
    }
    return res;
}
function getCountryThroughputTimes(countryCode) {
// array of times corresponding to non zero results
    var res = [];
    var countryPoints = getCountryPoints(countryCode);
    for (i in countryPoints) {
        var pointTimes = getNonZeroSamples(countryPoints[i]);
        for (j in pointTimes) {
            res.push(pointTimes[j]);
        }
    }
    return res;
}
function getCountryThroughputPercentage(countryCode) {
    var countryPoints = getCountryPoints(countryCode);
    var done = 0;
    var numTests = getCountryPoints(countryCode).length * 3;// CAMBIAR
    for (i in countryPoints) {
        /* done = done + countryPoints[i].throughputResults.length; */
        done += getNonZeroSamples(countryPoints[i]).length
        // done = done + getTestPointThroughputTimes(countryPoints[i]).length;
    }
    return Math.floor(done * 100 / ( numTests ));
    // return Math.floor( done * 100 / (imageSizes.length *
    // countryPoints.length) );
}

function bps2KMG(bps) {
    // returns string
    // 1000 bps = 1Kbps
    var K = 1000;
    var M = K * K;
    var G = K * M;
    var T = K * G;

    if (bps > K * T) {
        return "N/A";
    }
    if (bps > T) {
        return Math.floor(bps / T) + " Tbps";
    }
    if (bps > G) {
        return Math.floor(bps / G) + " Gbps";
    }
    if (bps > M) {
        return Math.floor(bps / M) + " Mbps";
    }
    if (bps > K) {
        return Math.floor(bps / K) + " Kbps";
    }

    if (bps < 0) {
        return "N/A";
    }

    return bps;
}

function buildThroughputXML(testPoints) {
    if (testPoints instanceof Array) {

        var date = new Date();

        var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
        xml = xml + "<simon xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n";
        xml = xml + "<version>2</version>\n";
        xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>\n";
        xml = xml + "<time>" + getPrintTimeWithOffset(date) + "</time>\n";
        xml = xml + "<local_country>" + local_country + "</local_country>\n";

        for (var i = 0; i < testPoints.length; i++) {

            for (j in testPoints[i].throughputResults) {
                // timeout (lost samples) or aborted points don't really matter
                // for throughput
                /* if(typeof testPoints[i].throughputResults[j] == 'number'){ */
                if (/* typeof */testPoints[i].throughputResults[j].time != DEFAULT_TIME) {
                    xml = xml + "<test>\n";
                    xml = xml + "<destination_ip>" + testPoints[i].ip + "</destination_ip>\n";
                    xml = xml + "<testtype>" + testType + "</testtype>\n";
                    xml = xml + "<time>" + testPoints[i].throughputResults[j].time + "</time>\n";
                    xml = xml + "<size>" + testPoints[i].throughputResults[j].byteSize + "</size>\n";
                    xml = xml + "<ip_version>" + getIPversion(testPoints[i].ip) + "</ip_version>\n";
                    xml = xml + "</test>\n";
                }
            }
        }

        xml = xml + "<tester>JavaScript</tester>\n";
        xml = xml + "<tester_version>1</tester_version>\n";
        xml = xml + "</simon>\n";

        return xml;
    }
}
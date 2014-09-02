/*
 * JavaScript probe that is hosted in different sites and harvests data as users visit that site.
 * LACNIC Labs - 2014
 */

if (typeof simonURL === "undefined")
	simonURL = "http://simon.labs.lacnic.net/simon/"
if (typeof ipv6ResolveURL === "undefined")
	ipv6ResolveURL = "http://simon.labs.lacnic.net/simon/"
if (typeof ipv4ResolveURL === "undefined")
	ipv4ResolveURL = "http://simon.labs.lacnic.net/simon/"
var pointsURL = simonURL + "web_points/getPointsCallback/";

var params = {
	percentage : 1.0,
	amount : 4
};
var SIMON = {
	params : params
};

// var amount = 4;
var testsConfigsURL = simonURL + "web_configs/";
var reportOfflineURL = simonURL + "postxmlresult/offline";
var postLatencyURL = simonURL + "postxmlresult/latency";

var siteOnLineTimeout = 6000;
var latencyTimeout = 1000;
var testType = 'tcp_web';
var countryCode = "";
var ipv4Address = "";
var ipv6Address = "";

/*
 * default time for throughput results
 */
var DEFAULT_TIME = -1;
var runLatency = false;
var runThroughput = false;
var runJitter = false;
var points;
var numTests = 5;

/*
 * COUNTRY request from server
 */
var COUNTRY = {

	getCountry : function() {

		printr("Getting user country...");

		var url = simonURL + "getCountry/";

		$.ajax({
			type : 'GET',
			url : url,
			success : function(cc) {

				countryCode = cc;
				getMyIPAddress(ipv6ResolveURL);
			},
			error : function(xhr, status, error) {

			}
		});
	}
};

function printr(text) {
	if (document.URL === simonURL) {

		cur_html = $('#console').html();
		$('#console').html(cur_html + text + "<br>");
		var y = $('#console').scrollTop();
		$('#console').scrollTop(y + 30);
	}
}

function getTestsConfigs() {

	/*
	 * get the test configs from the server
	 */
	printr("Fetching tests configurations...");

	$.ajax({
		url : testsConfigsURL,
		dataType : "jsonp",
		crossDomain : true,
		success : function(data, textStatus, jqXHR) {

			if (data.configs.latency == 1) {
				runLatency = true;
			} else {
				runLatency = false;
			}
			if (data.configs.throughput == 1) {
				runThroughput = true;
			} else {
				runThroughput = false;
			}
			if (data.configs.jitter == 1) {
				runJitter = true
			} else {
				runJitter = false;
			}

			if (ipv6Address != "")
				getPoints(6);
			else
				getPoints(4);
		}
	});
}

function getPoints(ipVersion) {

	$.ajax({
		url : simonURL + "web_points/" + SIMON.params.amount + "/" + ipVersion,
		dataType : 'jsonp',
		crossDomain : true
	}).success(function(data) {

		points = new Array();

		/*
		 * callback when the points are loaded from the server
		 */
		for (i in data.points) {
			var jsonPoint = data.points[i];
			var testPoint = {
				"ip" : jsonPoint.ip,
				"url" : jsonPoint.url,
				"country" : jsonPoint.country,
				"countryName" : jsonPoint.countryName,
				"city" : jsonPoint.city,
				"region" : jsonPoint.region,
				/*
				 * holds the results of latency tests
				 */
				"results" : [],
				"throughputResults" : [],
				"online" : false,
				"onlineFinished" : false,
			};

			var jsonImages = $.parseJSON(jsonPoint.images);
			for (j in jsonImages) {
				var jsonImage = jsonImages[j];
				var image = {
					"path" : jsonImage.path,
					"width" : jsonImage.width,
					"height" : jsonImage.height,
					"byteSize" : jsonImage.size,
					"name" : jsonImage.name,
					"timeout" : jsonImage.timeout,
					"type" : jsonImage.type,
					/*
					 * holds the results of throughput tests
					 */
					"time" : DEFAULT_TIME,
				};

				testPoint.throughputResults.push(image);
			}

			points.push(testPoint);
		}

		siteOnLine(points[0]);

	}).complete();
}

/*
 * SITE ON-LINE
 */

function siteOnLine(testPoint) {

	printr("Checking site " + testPoint.ip + " (" + testPoint.country + ")");

	/*
	 * get the '/' directory
	 */
	var url;
	if (getIPversion(testPoint.ip) == 4) {
		url = "http://" + testPoint.ip + "/";
	} else if (getIPversion(testPoint.ip) == 6) {
		url = "http://[" + testPoint.ip + "]/";
	}

	$.ajax({
		type : 'GET',
		url : url,
		dataType : 'jsonp',
		timeout : siteOnLineTimeout,
		xhrFields : {
			withCredentials : true
		},
		beforeSend : function(xhr) {
			if (xhr.overrideMimeType) {
				xhr.setRequestHeader("Connection", "close");
			}
		},

		complete : function(jqXHR, textStatus) {

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
				var xml = buildOfflineXML(array);
				printr("Reporting offline test point...");
				postResults(reportOfflineURL, xml);
			}

			/*
			 * store results in global variable
			 */
			saveTestPoint(testPoint);
			startPointTest(testPoint);
		},

		error : function(jqXHR, textStatus, errorThrown) {
			/*
			 * error included in complete function
			 */
		}
	});
}

function saveTestPoint(testPoint) {
	/*
	 * save test point to global variable 'points'
	 */

	var index = getTestPointIndex(testPoint);
	points[index] = testPoint;
}

function startPointTest(testPoint) {
	if (testPoint.online) {
		/*
		 * schedule latency tests
		 */
		for (var i = 0; i < numTests; i++) {
			setTimeout(latencyTest, latencyTimeout * i, testPoint);
		}
	} else {
		abortTestPointTest(testPoint);
		var nextTestPoint = getNextPoint(testPoint);
		if (nextTestPoint != -1) {
			/*
			 * test next testpoint
			 */
			siteOnLine(nextTestPoint);
		}

		/*
		 * end tests
		 */
	}
}

function abortTestPointTest(testPoint) {
	/*
	 * fill remaining results with 'aborted'
	 */

	for (var i = testPoint.results.length; i < numTests; i++) {
		testPoint.results.push('aborted');
	}

	for (i in testPoint.throughputResults) {
		if (testPoint.throughputResults[i].time == DEFAULT_TIME) {
			testPoint.throughputResults[i].time = 'aborted';
		}
	}
}

function buildOfflineXML(offlinePoints) {
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
}

/*
 * LATENCY
 */

function latencyTest(testPoint) {

	var ts, rtt;

	var url;
	if (getIPversion(testPoint.ip) == 6) {
		url = "http://[" + testPoint.ip + "]/" + Math.random();
	} else {
		url = "http://" + testPoint.ip + "/" + Math.random();
	}
	
//	$.ajax({
//	url : url,
//	dataType : 'jsonp',
//	crossDomain : true,
	
	$.jsonp({
	type : 'GET',
	url : url,
	dataType : 'jsonp',
	timeout : latencyTimeout,
		xhrFields : {
			withCredentials : true
		},

		beforeSend : function(xhr) {
			if (xhr.overrideMimeType)
				xhr.setRequestHeader("Connection", "close");
		},
		error : function(jqXHR, textStatus) {

			if (textStatus == 'timeout') {

				testPoint.results.push('timeout');
			} else {
				/*
				 * If there is an error and the site is up, we can suppose it is
				 * due to 404
				 */
				rtt = (+new Date - ts);
				testPoint.results.push(rtt);
				printr("Measuring latency to " + testPoint.ip + " (" + getMean(testPoint.results) + " ms)");
			}

			saveTestPoint(testPoint);// store results in global variable

			if (testerFinished(testPoint)) {// post results

				var array = [];
				array.push(testPoint);

				var xml;
				if (getIPversion(testPoint.ip) == '4')
					xml = buildXML(array, ipv4Address);
				else if (getIPversion(testPoint.ip) == '6')
					xml = buildXML(array, ipv6Address);
				postResults(postLatencyURL, xml);

				var nextTestPoint = getNextPoint(testPoint);
				if (nextTestPoint != -1) {
					siteOnLine(nextTestPoint);// ... and next tests

				} else {

					if (document.URL === simonURL) {
						/*
						 * if the probe is located at the Simon site, keep doing
						 * tests indefinitely
						 */
						if (ipv6Address != "")
							getPoints(6);
						else
							getPoints(4);
					} else {
						printr("Thank you!");
					}
				}
			}

		}
	});

	ts = +new Date;
}

function getIPversion(ip) {
	if (ip.indexOf(":") > -1) {
		return '6';
	} else {
		return '4';
	}
	return -1;// error
}

function testerFinished(testPoint) {
	if (testPoint.results.length == numTests) {
		return true;
	}
	return false;
}

function postResults(url, data) {

	printr("Posting results...");

	$.ajax({
		type : 'POST',
		url : url,
		data : data,
		success : function(xml) {
			return true;
		},
		error : function(xhr, status, error) {
			return false;
		}
	});
}

/**
 * Lacnic's what-is-my-ip service
 * 
 * @param url
 */
function getMyIPAddress(url) {

	$.ajax({
		url : url,
		dataType : 'jsonp',
		crossDomain : true
	}).success(function(data) {

		if (getIPversion(data.ip) == '4') {
			ipv4Address = data.ip;
			getTestsConfigs();

		} else if (getIPversion(data.ip) == '6') {
			ipv6Address = data.ip;
			getMyIPAddress(ipv4ResolveURL);
		}
	});
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
	if (index < points.length) {
		return points[index];
	} else {
		return -1;
	}
}

/*
 * XML
 */
function buildXML(testPoints, origin_ip) {

	printr("Building data...");

	if (testPoints instanceof Array && testPoints.length > 0) {
		var date = new Date();

		var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
		xml = xml
				+ "<simon xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">";
		xml = xml + "<version>2</version>";
		xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>";
		xml = xml + "<time>" + getPrintTimeWithOffset(date) + "</time>";
		xml = xml + "<local_country>" + countryCode + "</local_country>";

		for (var i = 0; i < testPoints.length; i++) {

			/*
			 * var lost = getLost(testPoints[i].results);
			 */
			var cleanResults = getNumericalValues(testPoints[i].results);
			/*
			 * with clean values
			 */

			xml = xml + "<test>";
			xml = xml + "<destination_ip>" + testPoints[i].ip
					+ "</destination_ip>";
			xml = xml + "<origin_ip>" + origin_ip + "</origin_ip>";
			xml = xml + "<testtype>" + testType + "</testtype>";

			xml = xml + "<number_probes>" + testPoints[i].results.length
					+ "</number_probes>";
			xml = xml + "<min_rtt>" + Math.floor(getMin(cleanResults))
					+ "</min_rtt>";
			xml = xml + "<max_rtt>" + Math.floor(getMax(cleanResults))
					+ "</max_rtt>";
			xml = xml + "<ave_rtt>" + Math.floor(getMean(cleanResults))
					+ "</ave_rtt>";
			xml = xml + "<dev_rtt>" + Math.floor(getStdDev(cleanResults))
					+ "</dev_rtt>";
			xml = xml + "<median_rtt>" + Math.floor(getMedian(cleanResults))
					+ "</median_rtt>";
			xml = xml + "<packet_loss>" + getLost(testPoints[i].results)
					+ "</packet_loss>";
			xml = xml + "<ip_version>" + getIPversion(testPoints[i].ip)
					+ "</ip_version>";
			xml = xml + "</test>";
		}

		xml = xml + "<tester>JavaScript</tester>";
		xml = xml + "<tester_version>1</tester_version>";
		xml = xml + "<user_agent>" + navigator.userAgent + "</user_agent>";
		xml = xml + "</simon>";
		
		return xml;
	}
}

function getPrintTimeWithOffset(date) {

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
}

function getNumericalValues(dataSet) {
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
}

function sortfunction(a, b) {
	/*
	 * Causes an array to be sorted numerically and ascending.
	 */
	return (a - b);
}

function getMin(dataSet) {
	if (dataSet instanceof Array && dataSet.length > 0) {
		dataSet.sort(function(a, b) {
			return a - b;
		});
		return dataSet[0];
	}
	return 0;
}

function getMax(dataSet) {
	if (dataSet instanceof Array && dataSet.length > 0) {
		dataSet.sort(function(a, b) {
			return a - b;
		});
		dataSet.reverse();
		return dataSet[0];
	}
	return 0;
}

function getMedian(dataSet) {

	if (dataSet instanceof Array && dataSet.length > 0) {
		/*
		 * numeric comparator. Returns negative number if a < b, positive if a >
		 * b and 0 if they're equal used to sort an array numerically
		 */
		dataSet.sort(function(a, b) {
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

/*
 * TRIGGER
 */

$(document).ready(function() {
	NProgress.start();
	if (Math.random() < SIMON.params.percentage) {
		NProgress.done();
		COUNTRY.getCountry();
		jQuery.support.cors = true;
		
	}
});
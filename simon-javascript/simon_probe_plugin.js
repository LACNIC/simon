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
	percentage : 1.0,// 100%
	amount : 4
};

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

SIMON = {
	params : params,

	init : function() {
		if (Math.random() < this.params.percentage)
			return this.getCountry();
		else
			printr("N/A");
	},

	getCountry : function() {
		this.printr("Getting user country...");

		$.ajax({
			type : 'GET',
			context : this,
			url : simonURL + "getCountry/",
			success : function(cc) {
				countryCode = cc;
				SIMON.getMyIPAddress(ipv6ResolveURL);
			}
		});
	},

	getTestsConfigs : function() {

		/*
		 * get the test configs from the server
		 */
		this.printr("Fetching tests configurations...");

		$.ajax({
			url : testsConfigsURL,
			dataType : 'jsonp',
			crossDomain : true,
			context : this
		}).success(function(data) {

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
				this.getPoints(6);
			else
				this.getPoints(4);
		});
	},

	getPoints : function(ipVersion) {

		$.ajax(
				{
					url : simonURL + "web_points/" + SIMON.params.amount + "/"
							+ ipVersion,
					dataType : 'jsonp',
					crossDomain : true,
					context : this
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

			this.siteOnLine(points[0]);

		}).complete();
	},

	siteOnLine : function(testPoint) {

		this.printr("Checking site " + testPoint.ip + " (" + testPoint.country
				+ ")");

		/*
		 * get the '/' directory
		 */
		var url;
		if (this.getIPversion(testPoint.ip) == 4)
			url = "http://" + testPoint.ip + "/";
		else if (this.getIPversion(testPoint.ip) == 6)
			url = "http://[" + testPoint.ip + "]/";

		$.ajax({
			url : url,
			dataType : 'jsonp',
			crossDomain : true,
			context : this,
			timeout : siteOnLineTimeout,
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
					this.printr("Reporting offline test point...");
					this.postResults(reportOfflineURL, xml);
				}

				/*
				 * store results in global variable
				 */
				this.saveTestPoint(testPoint);
				this.startPointTest(testPoint);
			}
		});
	},

	saveTestPoint : function(testPoint) {
		/*
		 * save test point to global variable 'points'
		 */
		var index = this.getTestPointIndex(testPoint);
		points[index] = testPoint;
	},

	startPointTest : function(testPoint) {
		if (testPoint.online) {
			// schedule latency tests
			var that = this;
			for (var i = 0; i < numTests; i++) {
				setTimeout(function() {
					SIMON.latencyTest(testPoint);
				}, latencyTimeout * i);
			}
		} else {
			this.abortTestPointTest(testPoint);
			var nextTestPoint = this.getNextPoint(testPoint);
			if (nextTestPoint != -1) {
				this.siteOnLine(nextTestPoint);
			}
		}
	},
	
	latencyTest : function(testPoint) {

		var ts, rtt;

		var url;
		if (this.getIPversion(testPoint.ip) == '6') {
			url = "http://[" + testPoint.ip + "]/" + Math.random();
		} else {
			url = "http://" + testPoint.ip + "/" + Math.random();
		}
		
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
					SIMON.printr("Measuring latency to " + testPoint.ip + " - " + rtt + " ms " + "(" + SIMON.getMean(testPoint.results)+ " ms)");
				}

				SIMON.saveTestPoint(testPoint);// store results in global variable

				if (SIMON.testerFinished(testPoint)) {// post results

					var array = [];
					array.push(testPoint);

					var xml;
					if (SIMON.getIPversion(testPoint.ip) == '4')
						xml = SIMON.buildXML(array, ipv4Address);
					else if (SIMON.getIPversion(testPoint.ip) == '6')
						xml = SIMON.buildXML(array, ipv6Address);
					SIMON.postResults(postLatencyURL, xml);

					var nextTestPoint = SIMON.getNextPoint(testPoint);
					if (nextTestPoint != -1) {
						SIMON.siteOnLine(nextTestPoint);// ... and next tests

					} else {

						if (document.URL === simonURL) {
							/*
							 * if the probe is located at the Simon site, keep doing
							 * tests indefinitely
							 */
							if (ipv6Address != "")
								SIMON.getPoints(6);
							else
								SIMON.getPoints(4);
						} else {
							SIMON.printr("Thank you!");
						}
					}
				}

			}
		});

		ts = +new Date;
	},

	abortTestPointTest : function(testPoint) {
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
	},

	buildOfflineXML : function(offlinePoints) {
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

	getMyIPAddress : function(url) {

		$.ajax({
			url : url,
			dataType : 'jsonp',
			crossDomain : true,
			context : this
		}).success(function(data) {

			if (this.getIPversion(data.ip) == '4') {
				ipv4Address = data.ip;
				this.getTestsConfigs();

			} else if (this.getIPversion(data.ip) == '6') {
				ipv6Address = data.ip;
				this.getMyIPAddress(ipv4ResolveURL);
			}
		});
	},

	getTestPointIndex : function(testPoint) {
		for (i in points) {
			if (points[i].ip == testPoint.ip) {
				return i;
			}
		}
		return null;
	},

	getNextPoint : function(testPoint) {
		var index = this.getTestPointIndex(testPoint);
		index++;
		if (index < points.length) {
			return points[index];
		} else {
			return -1;
		}
	},

	getPrintTimeWithOffset : function(date) {

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
	
	buildXML : function(testPoints, origin_ip) {

		SIMON.printr("Building data...");

		if (testPoints instanceof Array && testPoints.length > 0) {
			var date = new Date();

			var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";
			xml = xml
					+ "<simon xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">";
			xml = xml + "<version>2</version>";
			xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>";
			xml = xml + "<time>" + SIMON.getPrintTimeWithOffset(date) + "</time>";
			xml = xml + "<local_country>" + countryCode + "</local_country>";
			
			for (var i = 0; i < testPoints.length; i++) {
				
				var cleanResults = SIMON.getNumericalValues(testPoints[i].results);
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
				xml = xml + "<min_rtt>" + Math.floor(SIMON.getMin(cleanResults))
						+ "</min_rtt>";
				xml = xml + "<max_rtt>" + Math.floor(SIMON.getMax(cleanResults))
						+ "</max_rtt>";
				xml = xml + "<ave_rtt>" + Math.floor(SIMON.getMean(cleanResults))
						+ "</ave_rtt>";
				xml = xml + "<dev_rtt>" + Math.floor(SIMON.getStdDev(cleanResults))
						+ "</dev_rtt>";
				xml = xml + "<median_rtt>"
						+ Math.floor(SIMON.getMedian(cleanResults)) + "</median_rtt>";
				xml = xml + "<packet_loss>" + SIMON.getLost(testPoints[i].results)
						+ "</packet_loss>";
				xml = xml + "<ip_version>" + SIMON.getIPversion(testPoints[i].ip)
						+ "</ip_version>";
				xml = xml + "</test>";
			}

			xml = xml + "<tester>JavaScript</tester>";
			xml = xml + "<tester_version>1</tester_version>";
			xml = xml + "</simon>";

			return xml;
		}
	},

	getPrintOffset : function(date) {
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

	getNumericalValues : function(dataSet) {
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

	sortfunction : function(a, b) {
		/*
		 * Causes an array to be sorted numerically and ascending.
		 */
		return (a - b);
	},

	getMin : function(dataSet) {
		if (dataSet instanceof Array && dataSet.length > 0) {
			dataSet.sort(function(a, b) {
				return a - b;
			});
			return dataSet[0];
		}
		return 0;
	},

	getMax : function(dataSet) {
		if (dataSet instanceof Array && dataSet.length > 0) {
			dataSet.sort(function(a, b) {
				return a - b;
			});
			dataSet.reverse();
			return dataSet[0];
		}
		return 0;
	},

	getMedian : function(dataSet) {

		if (dataSet instanceof Array && dataSet.length > 0) {
			/*
			 * numeric comparator. Returns negative number if a < b, positive if
			 * a > b and 0 if they're equal used to sort an array numerically
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
	},

	getStdDev : function(dataSet) {
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

	getMean : function(dataSet) {
		if (dataSet instanceof Array && dataSet.length > 0) {

			return Math.floor(this.sum(dataSet) / dataSet.length);
		}
		return 0;
	},

	sum : function(dataSet) {
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

	getLost : function(dataSet) {
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

	getIPversion : function(ip) {
		if (ip.indexOf(":") > -1) {
			return '6';
		} else {
			return '4';
		}
		return -1;// error
	},

	testerFinished : function(testPoint) {
		if (testPoint.results.length == numTests) {
			return true;
		}
		return false;
	},

	postResults : function(url, data) {

		SIMON.printr("Posting results...");

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
	},

	printr : function(text) {
		if (document.URL === simonURL) {

			cur_html = $('#console').html();
			$('#console').html(cur_html + text + "<br>");
			var y = $('#console').scrollTop();
			$('#console').scrollTop(y + 30);
		}
	},

};

$(document).ready(function() {

	NProgress.start();

	if (Math.random() < SIMON.params.percentage) {
		NProgress.done();
		SIMON.init();
		jQuery.support.cors = true;

	}
});
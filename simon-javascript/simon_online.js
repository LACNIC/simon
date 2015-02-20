/**
 * Online test code.
 * LACNIC 2012
 */


//var base_url = window.location.host;
//var reportOfflineURL = "http://" + base_url + "/simon/postxmlresult/offline";
var reportOfflineURL = "http://127.0.0.1:8000/postxmlresult/offline";
var siteOnLineTimeout = 6000;//ms

//var offlinePoints = [];// holds the points that didn't pass the siteOnLine() test

function startSiteTests() {
	for (i in points) {
		setTimeout(siteOnLine, siteOnLineTimeout * i, points[i]);
	}
}

function sitesChecked() {
	
	for (i in points) {
		if (! points[i].onlineFinished ){
			return false;
		}
	}
	return true;
}

function getOnlinePoints(testPoints){
	var res = [];
	for(i in testPoints){
		if(testPoints[i].online){
			res.push(testPoints[i]);
		}
	}
	return res;
}

function siteOnLine(testPoint) {
	
	// get the '/' directory
	var ip = "http://" + testPoint.ip + "/";
	
	printr("Checking " + testPoint.country + " points status....");
	
	$.ajax({
		type : 'GET',
		url : ip,
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
		
		complete: function(jqXHR, textStatus) {
			
			testPoint.onlineFinished = true;
			/*(useful) HTTP errors
			 * 2XX - Success
			 * 500-504 Server Error
			 * 401 Unauthorized
			 * 407 Authentication required
			 */
			var pattern = /2[0-9]{2}|50[01234]|401|407/;
			
			if(pattern.test(jqXHR.status)) {
				testPoint.online = true;
			}else{
				testPoint.online = false;
				// report offline point
				//offlinePoints.push(testPoint);
				var array = [];
				array.push(testPoint);
				var xml = buildOfflineXML(array);
				postResults(reportOfflineURL, xml);
			}

			addOnlineStatus(testPoint);//graphical
			saveTestPoint(testPoint);// store results in global variable
			startPointTest(testPoint);
		},
		
		error: function(jqXHR, textStatus, errorThrown){
			// error included in complete function
		}
	});
}

function buildOfflineXML(offlinePoints) {
	if (offlinePoints instanceof Array) {

		var date = new Date();

		var xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
		xml = xml + "<report xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\">\n";
		
		for (i in offlinePoints) {
			xml = xml + "<point>\n";
			xml = xml + "<destination_ip>" + offlinePoints[i].ip + "</destination_ip>\n";
			xml = xml + "<date>" + date.format("yyyy-mm-dd") + "</date>\n";//timezone?
			xml = xml + "</point>\n";
			
		}
		xml = xml + "</report>\n\n";

		return xml;
	}
	return 1;//error
}
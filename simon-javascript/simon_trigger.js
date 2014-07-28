/**
 * 'Trigger' file. Gets the test points, the test configurations, and waits for
 * the user to filter by country or amount of points.
 * LACNIC 2012
 */


//var base_url = window.location.host;

//var testsConfigsURL = "http://" + base_url + "/simon/web_configs/";
var testsConfigsURL = "http://127.0.0.1:8000/web_configs/";
//var testsConfigsURL = "http://simon.labs.lacnic.net/simon/web_configs/";

//var pointsURL = "http://" + base_url + "/simon/web_points/jsonpLatencyCallback";
//var pointsURL = "http://127.0.0.1:8000/web_points/jsonpLatencyCallback";
var pointsURL = "http://simon.labs.lacnic.net/simon/web_points/jsonpLatencyCallback";

var DEFAULT_TIME = -1;// default time for throughput results
var runLatency = false;
var runThroughput = false;
var runJitter = false;

function getTestsConfigs() {
	
	// gets the test configs from the server
	printr("Getting the test configurations....");
	
	$.ajax({
		  url: testsConfigsURL,
		  dataType : "json",
		  success : function(data, textStatus, jqXHR){
			  
			  if(data.configs.latency == 1) {
				  runLatency = true;
			  }else{
				  runLatency = false;
			  }
			  if(data.configs.throughput == 1) {
				  runThroughput = true;
			  }else{
				  runThroughput = false;
			  }
			  if(data.configs.jitter == 1) {
				  runJitter = true
			  }else{
				  runJitter = false;
			  }
			  getPoints();
			  // nothing will execute here...
		  }
	  });
}

function getPoints(){
	printr("Getting the test points....");
	  $.ajax({
		  url: pointsURL,
		  dataType : "jsonp",
	  });
}

function jsonpLatencyCallback(data){
	
	// callback when the points are loaded from the server
	// Build the points....
	printr("Building the data structures....");
	
	for (i in data.points){
		var jsonPoint = data.points[i];
		var testPoint = {
				"ip" : jsonPoint.ip,
				"url" : jsonPoint.url,
				"country" : jsonPoint.country,
				"countryName" : jsonPoint.countryName,
				"city" : jsonPoint.city,
				"region" : jsonPoint.region,
				"results" : [], // holds the results of latency tests
				"throughputResults" : [],
				"online" : false,
				"onlineFinished" : false,
		};
		
		var jsonImages = $.parseJSON(jsonPoint.images);
		for(j in jsonImages){
			var jsonImage = jsonImages[j];
			var image = {
					"path" : jsonImage.path,
					"width" : jsonImage.width,
					"height" : jsonImage.height,
					"byteSize" : jsonImage.size,
					"name" : jsonImage.name,
					"timeout" : jsonImage.timeout,
					"type" : jsonImage.type,
					"time" : DEFAULT_TIME,// holds the results of throughput tests
					};

			testPoint.throughputResults.push(image);
		}
		points.push(testPoint);
		/////////////////////////////////////
		/*points = []
		var testPoint = {
				"ip" : '190.102.252.138',
				"url" : 'mundopacifico.cl',
				"country" : 'CL',
				"countryName" : 'Chile',
				"city" : 'BsAs',
				"region" : '2',
				"results" : [], // holds the results of latency tests
				"throughputResults" : [],
				"online" : true,
				"onlineFinished" : true,
		};
		for(i=0; i<=6; i++){
			var image = {
					"path" : '/simon/',
					"width" : '0',
					"height" : '0',
					"byteSize" : '111488',
					"name" : 'simon-' + i + '.png',
					"timeout" : '20000',
					"type" : 'png',
					"time" : DEFAULT_TIME,// holds the results of throughput tests
					};
			//$('#console').html($('#console').html() + testPoint.url + image.path);

			testPoint.throughputResults.push(image);
		}
		
		points.push(testPoint);*/
		/////////////////////////////////////
	}
	
	/*
	 * Build initial UI prior to the tables
	 */
	
	$('#numpoints').html( points.length );
	
	$( "#slider" ).slider({
		value:points.length,
		min: 1,
		max: points.length,
		step: 1,
		slide: function( event, ui ) {
			$('#numpoints').html( ui.value );
		}
	});

	// Select box
	var uniqueCountries = getUniqueCountries();
	uniqueCountries.sort();// diplay the checklist ordered. points are still
							// scrambled
	for(i in uniqueCountries){
		$("#countrySelect").append('<option value=' + uniqueCountries[i] + '>' + uniqueCountries[i] + '</option>');
	}
	$("#countrySelect").multiselect({
			// header : 'Please select the destination countries',
			height : 300,
			checkAllText : "Select all",
			uncheckAllText : "Deselect all",
			show : ['fade', 500],// fancy effect
	});
	$("#countrySelect").change(function(){
        // change the max amounts of points in the slider as the user changes
		// the countries
		
		var selectedCountries = $("#countrySelect").multiselect("getChecked");
		var countryPoints = getCountryArrayPoints(selectedCountries);
		
		$("#slider").slider( "option", "max" , countryPoints.length );
		$("#slider").slider("value", $("#slider").slider("value"));// redraw
																	// the
																	// current
																	// value (as
																	// the max
																	// value
																	// changes
																	// the
																	// slider
																	// must
																	// shift to
																	// its new
																	// position)
    })

	$("#countrySelect").multiselect("checkAll");
}

function getMyIPAddress(url){
	$.ajax({
		url : url,
		dataType : 'jsonp'
	});
}
function getMyIPAddressCallback(data){
	var testPoint = auxTestPoint;
	auxTestPoint = null;// empty global variable
	var array = [];
	array.push(testPoint);
	var xml = buildXML(array, data.ip);
	postResults(postLatencyURL, xml);
	
	if(runThroughput){
		// Start throughput tests

		/*throughputTest(testPoint, imageSizes[imagesIndex]);*/
		throughputTest(testPoint, imagesIndex);
	}else if(runJitter){
		
		// jitter code
		
	}else if(runLatency){
		var nextTestPoint = getNextPoint(testPoint);
		siteOnLine(nextTestPoint);// startPointTest(nextTestPoint);
	}
}

function setCountry(){
	// called from the Start Tests button
	
	local_country = $('#country :selected').val();
	if(confirm("Please confirm that you are in " + local_country + ". This is very important for the test accuracy.")){
		$( "#runTestButton" ).button( "option", "disabled", true );
		return true;
	}
	return false;
}

function startPointTest(testPoint){
	if(testPoint.online){
		// schedule latency tests
		for (var i=0; i<numTests; i++){
			setTimeout(latencyTest, latencyTimeout * i, testPoint);
		}
	}else{
		abortTestPointTest(testPoint);
		var nextTestPoint = getNextPoint(testPoint);
		siteOnLine(nextTestPoint);// restart
	}
}

function abortTestPointTest(testPoint){
	//fill remaining results with 'aborted'

	for(var i = testPoint.results.length; i < numTests; i++){
		testPoint.results.push('aborted');
		
	}
	updateLatency(testPoint);// graphical
	
	for(i in testPoint.throughputResults){
		if(testPoint.throughputResults[i].time == DEFAULT_TIME){
			testPoint.throughputResults[i].time = 'aborted';
		}
		
	}
	updateThroughput(testPoint);// graphical
}
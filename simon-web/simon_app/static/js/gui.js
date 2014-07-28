/**
 * Graphical User Interface code. Draws the datatables and loads them with info.
 * LACNIC 2012
 */
	
	
var table;
// ///////////////////////viejo....
var columns = {
		"country" : 0,
		"latencyProgress" : 1,
		"throughputProgress" : 2,
		"latency" : 3,
		"throughput" : 4,
}
var latencyColumns = {
		"ip" : 0,
		"min" : 1,
		"median" : 2,
		"avg" : 3,
		"max" : 4,
		"samples" : 5,
		"lost" : 6,
		"stddev" : 7,
		"online" : 8,
}
var throughputColumns = {
		"ip" : 0,
		"mean" : 1,
		"online" : 2,
}

function println(text) {
	cur_html = $('#result').html();
	$('#result').html(cur_html + text + "<br>");
}

function printr(text) {
	cur_html = $('#result').html();
	$('#result').html(text + "<br>");
}

function buildGUI() {
	printr("Building the Graphical User Interface....");
	
	/*
	 * Select the first X (randomized) points filtered by country
	 */
	
	var selectedCountries = $("#countrySelect").multiselect("getChecked");
	var temp = getCountryArrayPoints(selectedCountries);
	
	points = temp;// override
	
	
	var numPoints = $("#slider").slider("value");
	$("#init").remove();
	points.splice(numPoints - 1, points.length - numPoints);
	
	/*
	 * Easy table...
	 */
	
	/*
     * Insert a 'details' column to the table
     */
    var nCloneTh = document.createElement( 'th' );
    var nCloneTd = document.createElement( 'td' );
    nCloneTd.innerHTML = '<img src="./media/images/details_open.png">';
    nCloneTd.className = "center";
     
    $('#table thead tr').each( function () {
        this.insertBefore( nCloneTh, this.childNodes[0] );
    } );
     
    $('#table tbody tr').each( function () {
        this.insertBefore(  nCloneTd.cloneNode( true ), this.childNodes[0] );
    } );
     
    /*
     * Initialse DataTables, with no sorting on the 'details' column
     */
    /*var oTable = $('#example').dataTable( {
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] }
        ],
        "aaSorting": [[1, 'asc']]
    });*/
     
    

	table = $('#table').dataTable({
		"bJQueryUI": true,
		"bPaginate": false,
		"bAutoWidth": false,// prevents progress bar from expanding the column
		"aoColumns": [
		              { "sTitle": "Country", "sClass": "left"  },
		              { "sTitle": "Latency progress (%)", "sClass": "left", "sWidth" : "300px"  },
		              { "sTitle": "Throughput progress (%)", "sClass": "left", "sWidth" : "300px"  },
		              { "sTitle": "Average latency (ms)", "sClass": "center"  },
		              { "sTitle": "Average throughput (bps)", "sClass": "center"  },
		],
		"fnInitComplete": function(oSettings, json) {
		      
		      },
	});
	/* Add event listener for opening and closing details
     * Note that the indicator for showing which row is open is not controlled by DataTables,
     * rather it is done here
     */
    /*$('#table tbody td img').live('click', function () {
        var nTr = $(this).parents('tr')[0];
        if ( table.fnIsOpen(nTr) )
        {
             This row is already open - close it 
            this.src = "./media/images/details_open.png";
            table.fnClose( nTr );
        }
        else
        {
             Open this row 
            this.src = "./media/images/details_close.png";
            table.fnOpen( nTr, fnFormatDetails(table, nTr), 'details' );
        }
    } );*/
	
	

	var uniqueCountries = getUniqueCountries();

	for(i in uniqueCountries){
		// Inserts rows...
		var latencyDiv = document.createElement('div');
		var id = "LAT" + uniqueCountries[i];
		latencyDiv.setAttribute('id', id);
		latencyDiv.style.width = "80%";
		latencyDiv.style.height = "10px";
		
		$("#" + id).progressbar();
		
		var throughputDiv = document.createElement('div');
		var id = "TH" + uniqueCountries[i];
		throughputDiv.setAttribute('id', id);
		throughputDiv.style.width = "300px";
		throughputDiv.style.height = "10px";
		
		$("#" + id).progressbar();
		

		addRow(table, uniqueCountries[i], "", "","","");
	}
	
	$("#tabs").tabs();
	

	
	
	
	/*
	 * Advanced tables
	 */
	// Latency
	$('#tabs-2').append('<ul></ul>');
	var ul = $('#tabs-2 ul')
	
	for(i in uniqueCountries){
		 ul.append("<li><a href='#tabs-2" + uniqueCountries[i] + "'>" + uniqueCountries[i] + "</a></li>");
		 $('#tabs-2').append("<div id='tabs-2" + uniqueCountries[i] + "'></div>");
		 var tableString = getCountryLatencyTableString(uniqueCountries[i]);
		 $('#tabs-2').append(tableString);
		 $('#advancedLatencyTable' + uniqueCountries[i]).appendTo('#tabs-2' + uniqueCountries[i]);// Move
																									// each
																									// table
																									// to
																									// its
																									// country
		 
		 // Table styles...
		 advancedLatencyTable = $('#advancedLatencyTable' + uniqueCountries[i]).dataTable({
				"bJQueryUI": true,
				"bPaginate": false,
				"aoColumns": [
				              { "sTitle": "IP", "sClass": "left", "sWidth" : "225px"  },
				              { "sTitle": "Min (ms)", "sClass": "center"  },
				              { "sTitle": "Median (ms)", "sClass": "center"  },
				              { "sTitle": "Avg. (ms)", "sClass": "center"  },
				              { "sTitle": "Max (ms)", "sClass": "center"  },
				              { "sTitle": "Samples", "sClass": "center"  },
				              { "sTitle": "Lost", "sClass": "center"  },
				              { "sTitle": "Std. Dev. (ms)", "sClass": "center"  },
				              { "sTitle": "Online", "sClass": "center", "sWidth" : "40px"  },
				              ],
			});
		 var countryPoints = getCountryPoints(uniqueCountries[i]);
		 for(j in countryPoints){
			 addLatencyRow(countryPoints[j].country, countryPoints[j].ip, "", "", "", "", "", "", "", "");
			 // countryCode, ip, min, median, avg, max, samples, lost, stddev
		 }
	}
	
	$('#tabs-2').tabs();
	
	
	// Throughput
	$('#tabs-3').append('<ul></ul>');
	var ul = $('#tabs-3 ul')
	
	for(i in uniqueCountries){
		 ul.append("<li><a href='#tabs-3" + uniqueCountries[i] + "'>" + uniqueCountries[i] + "</a></li>");
		 $('#tabs-3').append("<div id='tabs-3" + uniqueCountries[i] + "'></div>");
		 var tableString = getCountryThroughputTableString(uniqueCountries[i]);
		 $('#tabs-3').append(tableString);
		 $('#advancedThroughputTable' + uniqueCountries[i]).appendTo('#tabs-3' + uniqueCountries[i]);// Move
																										// each
																										// table
																										// to
																										// its
																										// country
		 
		 // Table styles...
		 advancedThroughputTable = $('#advancedThroughputTable' + uniqueCountries[i]).dataTable({
				"bJQueryUI": true,
				"bPaginate": false,
				"aoColumns": [
				            { "sTitle": "IP", "sClass": "left", "sWidth" : "225px"  },
							{ "sTitle": "Mean Troughput (bps)", "sClass": "center"  },
							{ "sTitle": "Online", "sClass": "center", "sWidth" : "40px"  },
							],
			});
		 
		 var countryPoints = getCountryPoints(uniqueCountries[i]);
		 for(j in countryPoints){
			 addThroughputRow(countryPoints[j].country, countryPoints[j].ip, "", "");
		 }
	}
	$('#tabs-3').tabs();

	// $("#tabs").css('visibility', 'visible');// show GUI after loading the
											// content
	$("#tabs").show("slow");
	printr("Tester ready.");
}

function getCountryLatencyTableString(countryCode, id){
	return '<table cellpadding="0" cellspacing="0" border="0" class="display" id="advancedLatencyTable' + countryCode + '"><thead></thead><tbody></tbody></table>';
}

function getCountryThroughputTableString(countryCode, id){
	return '<table cellpadding="0" cellspacing="0" border="0" class="display" id="advancedThroughputTable' + countryCode + '"><thead></thead><tbody></tbody></table>';
}

function addRow(table, country, latencyProgressBar, throughpuProgressBar, latency, throughput){
	$('#table').dataTable().fnAddData( [
	                              		country,
	                              		'<div id="latencyProgressBar' + country + '" style="height : 15px; "></div>',
	                              		'<div id="throughputProgressBar' + country + '" style="height : 15px; "></div>',
	                              		latency,
	                              		throughput] );
	
	$("#latencyProgressBar" + country).progressbar({ value: 0 });
	$("#throughputProgressBar" + country).progressbar({ value: 0 });
}

function addLatencyRow(countryCode, ip, min, median, avg, max, samples, lost, stddev, online){
	$('#advancedLatencyTable' + countryCode).dataTable().fnAddData( [
	                              		ip,
	                              		min,
	                              		median,
	                              		avg,
	                              		max,
	                              		samples,
	                              		lost,
	                              		stddev,
	                              		online] );
}

function addThroughputRow(countryCode, ip, mean, online){
	$('#advancedThroughputTable' + countryCode).dataTable().fnAddData( [
	                              		ip,
	                              		mean,
	                              		online] );
}

function getUniqueCountries(){
	 var res = [];
	 for(i in points){
		 if($.inArray(points[i].country, res) == -1) {
			 res.push(points[i].country);
		 }
	 }
	 return res;
}

function getCountryCount(countryCode){
	var countries = getCountryPoints(countryCode);
	return countries.length;
	/*
	 * var res = 0; for(i in points){ if(points[i].country == countryCode){
	 * res++; } } return res;
	 */
}

function getCountryPoints(countryCode){
	var res = [];
	for(i in points){
		 if(points[i].country == countryCode){
			 res.push(points[i]);
		 }
	 }
	 return res;
}
function getCountryArrayPoints(countryCodeArray){
	// returns points a list of countries
	var res = [];
	var textArray = [];
	
	//change an HTML list into a text array
	for(i in countryCodeArray){
		if(typeof countryCodeArray[i] != 'undefined'){
			textArray.push( countryCodeArray[i].value/*.toString()*/ );
		}	
	}
	
	//select matches
	for(j in points){
		if($.inArray(points[j].country, textArray) > -1){
			res.push(points[j]);
		}
	}
	return res;
}
function fisherYates( myArray ) {
	// shuffle function
	if(myArray instanceof Array){
		var i = myArray.length;
		if ( i == 0 ) return false;
		while( --i ){
			var j = Math.floor( Math.random() * ( i + 1 ) );
			var tempi = myArray[i];
			var tempj = myArray[j];
			myArray[i] = tempj;
			myArray[j] = tempi;
			}
	}
}


function getCountryRow(countryCode){
	return rowPos = table.fnFindCellRowIndexes(countryCode);
}
function getLatencyPointRow(testPoint){
	return $('#advancedLatencyTable' + testPoint.country).dataTable().fnFindCellRowIndexes(testPoint.ip);
}
function getThroughputPointRow(testPoint){
	return $('#advancedThroughputTable' + testPoint.country).dataTable().fnFindCellRowIndexes(testPoint.ip);
}

function updateLatency(testPoint) {
	// Easy
	var countryCode = testPoint.country;
	var countryLatency = getCountryMean(countryCode);
	var rowPos = parseInt(getCountryRow(countryCode));
	var percent = getCountryLatencyPercentage(countryCode);
	
	updateCell(table, countryLatency, rowPos, columns.latency);
	$("#latencyProgressBar" + countryCode).progressbar({ value: percent });
	
	// Advanced
	updateLatencyRow(testPoint);
}
function updateThroughput(testPoint) {
	// Easy
	var countryCode = testPoint.country;
	$('#console').html($('#console').html() + ' UPDATE 1 ');
	var sizes = getMean(getCountryThroughputSizes(countryCode));
	$('#console').html($('#console').html() + ' UPDATE 2 ');
	var mean = getCountryThroughputMean(countryCode);
	$('#console').html($('#console').html() + ' UPDATE 3 ');
	var countryThroughput = Math.floor( sizes * 8 / mean );// bps = 8 * Bps
	$('#console').html($('#console').html() + ' UPDATE 4 ');
	
	var rowPos = parseInt(getCountryRow(countryCode));
	var percent = getCountryThroughputPercentage(countryCode);
	
	updateCell(table, countryThroughput, rowPos, columns.throughput);
	$("#throughputProgressBar" + countryCode).progressbar({ value: percent });
	
	// Advanced
	updateThroughputRow(testPoint);
}

function updateCell(table, newValue, rowPos, columnPos) {
	table.fnUpdate(newValue, rowPos, columnPos, false);// Don't redraw the
														// table....
}
function updateLatencyRow(testPoint){
	
	var rowPos = getLatencyPointRow(testPoint);
	var advancedLatencyTable = $('#advancedLatencyTable' + testPoint.country).dataTable();
	var data = getNumericalValues(testPoint.results);
	/*
	 * var rowColour = getColour(getMean(data)); println(rowColour);
	 */
	// $('#advancedLatencyTable' + testPoint.country + ' tr:eq(' + rowPos +
	// ')').addClass( 'gradeX' );
	
	var row = [testPoint.ip, getMin(data), getMedian(data), getMean(data), getMax(data), testPoint.results.length/* getCount(data) */, getLost(data), getStdDev(data), getOnlineImageTag(testPoint.online)];
	advancedLatencyTable.fnUpdate(row, parseInt(rowPos));// Row
	
	
}
function updateThroughputRow(testPoint){
	var rowPos = getThroughputPointRow(testPoint);
	var advancedThroughputTable = $('#advancedThroughputTable' + testPoint.country).dataTable();
	//var time = sum(getNonZeroSamples(testPoint));//getNumericalValues(testPoint.throughputResults);

	var row = [testPoint.ip, getMeanThroughput(testPoint), getOnlineImageTag(testPoint.online)];
	
	// advancedThroughputTable.fnUpdate( row, parseInt(rowPos),
	// false);//http://datatables.net/api#fnUpdate Redraw?!?!
	advancedThroughputTable.fnUpdate( row, parseInt(rowPos));// Row
}
function addOnlineStatus(testPoint){
	// Adds image to latency and throughput online columns
	var img = getOnlineImageTag(testPoint.online);
	
	var rowPos = getLatencyPointRow(testPoint);
	$('#advancedLatencyTable' + testPoint.country + ' tr:eq(' + rowPos + ') td:eq(' + latencyColumns.online + ')').html(img);
	if(! testPoint.online) $('#advancedLatencyTable' + testPoint.country + ' tr:eq(' + rowPos + ')').addClass( 'gradeX' );
	
	var rowPos = getThroughputPointRow(testPoint);
	$('#advancedThroughputTable' + testPoint.country + ' tr:eq(' + rowPos + ') td:eq(' + throughputColumns.online + ')').html( img );
	if(! testPoint.online) $('#advancedThroughputTable' + testPoint.country + ' tr:eq(' + rowPos + ')').addClass( 'gradeX' );
}
function getOnlineImageTag(online){
	if(online){
		return '<img id="img" src="../static/js/media/images/tick.png" style="width:auto; height:100%; max-height:15px;" />';
	}else{
		return '<img id="img" src="../static/js/media/images/minus.png" style="width:auto; height:100%; max-height:15px;" />';
	}
}

function changeCountryOnlineStatus(testPoint){
	/*
	 * Not used
	 */
	var offlinePoints = 0;
	var countryCode = testPoint.country;
	var points = getCountryPoints(countryCode);
	for(i in points){
		if(! points[i].online){
			offlinePoints ++;
		}
	}
	var percent = Math.floor( 100 * offlinePoints / points.length );
	
	if(0 < percent < 60){
		$('#table tr:eq(' + getCountryRow(countryCode) + ')').addClass( 'gradeX' );
	}else if(61 < percent < 80){
		$('#table tr:eq(' + getCountryRow(countryCode) + ')').addClass( 'gradeC' );
	}else if(81 < percent < 100){
		$('#table tr:eq(' + getCountryRow(countryCode) + ')').addClass( 'gradeA' );
	}
	
}

function getColour(rtt){
	var res = '';
	
	if(mean >= 1200){
		res = '#000000'; // black
	}
	if(mean >= 1000){
		res = '#990000'; // maroon
	}
	if(mean >= 800){
		res = '#FF0000'; // red
	}
	if(mean >= 600){
		res = '#FFCC00'; // orange
	}
	if(mean >= 400){
		res = '#FFFF33'; // yellow
	}
	if(mean >= 200){
		res = '#CCFF00'; // green
	}
	if(mean >= 0){
		res = '#CCFFFF'; // cyan
	}
	
	return res;
}

/* Formating function for row details */
function fnFormatDetails ( oTable, nTr )
{
    var aData = oTable.fnGetData( nTr );
    var sOut = '<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">';
    sOut += '<tr><td>Rendering engine:</td><td>'+aData[1]+'</td></tr>';
    sOut += '<tr><td>Link to source:</td><td>Could provide a link here</td></tr>';
    sOut += '<tr><td>Extra info:</td><td>And any further details here (images etc)</td></tr>';
    sOut += '</table>';
     
    return sOut;
}

function getColumnWidth(tableId, row, column){
	return $('#table tr:eq(' + row + ') td:eq(' + column + ')').width();
}

/*
 * Llevar los plugins a otro archivo
 */

$.fn.dataTableExt.oApi.fnFindCellRowIndexes = function ( oSettings, sSearch, iColumn )
{
    var
        i,iLen, j, jLen,
        aOut = [], aData;
      
    for ( i=0, iLen=oSettings.aoData.length ; i<iLen ; i++ )
    {
        aData = oSettings.aoData[i]._aData;
          
        if ( typeof iColumn == 'undefined' )
        {
            for ( j=0, jLen=aData.length ; j<jLen ; j++ )
            {
                if ( aData[j] == sSearch )
                {
                    aOut.push( i );
                }
            }
        }
        else if ( aData[iColumn] == sSearch )
        {
            aOut.push( i );
        }
    }
      
    return aOut;
};
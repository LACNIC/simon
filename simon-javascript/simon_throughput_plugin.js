/*
 SIMON throughput plugin.
 */


(function (d, s) {
    var js = d.createElement(s),
        sc = d.getElementsByTagName(s)[0];

    js.src = "https://www.google.com/jsapi?autoload={'modules':[{'name':'visualization','version':'1.1','packages':['gauge']}]}";
    js.type = "text/javascript";
    sc.parentNode.insertBefore(js, sc);
    js.onload = js.onreadystatechange = function () {
    };

}(document, "script"));
(function (d, s) {
    var js = d.createElement(s),
        sc = d.getElementsByTagName(s)[0];

    js.src = "http://simon.lacnic.net/simon/static/simon_app/js/simon_probe_plugin.js";
    js.type = "text/javascript";
    sc.parentNode.insertBefore(js, sc);

    js.onload = js.onreadystatechange = function () {
        SIMON.thputCount = 15;
        SIMON.before_start = function () {

            for(var i=0; i<SIMON.thputCount; i++) setTimeout(throughputTest, i*1000);

        };
        SIMON.after_points = function () {
        };
        SIMON.after_each = function () {
        };
        SIMON.print = false;
        SIMON.after_end = function () {

        }

        SIMON.thput = [];

        SIMON.init();
    };

}(document, "script"));

function bps2KMG(bps, leading){
	// returns string
	// 1000 bps = 1Kbps
	var K = 1000;
	var M = K * K;
	var G = K * M;
	var T = K * G;

	if(bps > K * T){
		return "N/A";
	}
	if(bps > T){
		return ( bps / T ) + " Tbps";
	}
	if(bps > G){
		return (  bps / G ) + " Gbps";
	}
	if(bps > M){
		return ( bps / M ) + " Mbps";
	}
	if(bps > K){
		return ( bps / K ) + " Kbps";
	}

	if(bps < 0){
		return "N/A";
	}

	return bps;
}

function throughputTest() {
    $.jsonp({
        type: 'GET',
        url: "http://simon.lacnic.net/simon/static/simon_app/imgs/random350x350.jpg",
        dataType: 'jsonp',
        crossDomain: true,
        context: this,
        cache: false,
        timeout: SIMON.latencyTimeout,
        xhrFields: {
            withCredentials: true
        },

        beforeSend: function (xhr) {
            if (xhr.overrideMimeType)
                xhr.setRequestHeader("Connection", "close");
        },

        error: function (jqXHR, textStatus) {
            /*
             * If there is an error and the site is up, we can suppose
             * it is due to 404
             */
            var rtt = (+new Date - ts);
            var bytes = 245388;
            var thput = 8 * bytes / (rtt * .001); // bps

            SIMON.thput.push(Math.floor(thput));
            SIMON.log(bps2KMG(thput));
        }
    });

    ts = +new Date;
}
/*
 * JavaScript probe that is hosted in different sites and harvests data as users visit that site.
 * LACNIC Labs - 2014
 */
SIMON = {
    init: function () {

        var ts, rtt;

        var url = "http://64.233.177.105/" + Math.random();

        $.jsonp({
            type: 'GET',
            url: url,
            dataType: 'jsonp',
            timeout: 1000,
            xhrFields: {
                withCredentials: true
            },

            beforeSend: function (xhr) {
                if (xhr.overrideMimeType)
                    xhr.setRequestHeader("Connection", "close");
            },

            error: function (jqXHR, textStatus) {
                if (textStatus == 'timeout') {

                } else {
                    /*
                     * If there is an error and the site is up, we can suppose
                     * it is due to 404
                     */
                    rtt = (+new Date - ts);
                    console.log(rtt);
                }
            }
        });

        ts = +new Date;
    }
}
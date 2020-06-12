/*
 *
 */
(function(f, b) {
  var c = f.createElement(b),
    e = f.getElementsByTagName(b)[0];
  c.src = "https://cdn.dev.lacnic.net/require.js";
  c.type = "text/javascript";
  e.parentNode.insertBefore(c, e);
  c.onload = c.onreadystatechange = function() {
    // Require libraries loaded
    requirejs.config({
      "paths": {
        "jquery": "https://cdn.dev.lacnic.net/jquery-1.11.1.min",
        "jquery-private": 'https://cdn.dev.lacnic.net/jquery-private',
        "jsonp": "https://cdn.dev.lacnic.net/jsonp",
        "date-format": "https://cdn.dev.lacnic.net/date.format",
        "simon": "https://rawgit.com/LACNIC/simon/master/simon-javascript/simon_probe_plugin",
        "stun": "https://rawgit.com/LACNIC/natmeter/master/stun/app/static/app/js/stun",
        "monitor": "https://rawgit.com/LACNIC/monitor/master/monitor/app/static/app/js/monitor"
      },

      'map': {
        '*': {
          'jquery': 'jquery-private'
        },

        'jquery-private': {
          'jquery': 'jquery'
        }
      },
    });

    require(["jquery", "monitor"], function(jQ, MONITOR) {
      // Configuration loaded now, safe to do other require calls
      // that depend on that config.

      MONITOR.init();

      if (Math.random() < 1 / 2) {
        require(["simon", "jsonp", "date-format"], function(SIMON, jsonp, dateFormat) {
          SIMON.init();
        });
      } else {
        require(['stun'], function(STUN) {
          STUN.init();
        });
      }
    });
  }
}(document, "script"));

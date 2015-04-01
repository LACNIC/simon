(function (e) {
    function t() {
    }

    function n(e) {
        C = [e]
    }

    function r(e, t, n) {
        return e && e.apply && e.apply(t.context || t, n)
    }

    function i(e) {
        return/\?/.test(e) ? "&" : "?"
    }

    function O(c) {
        function Y(e) {
            z++ || (W(), j && (T[I] = {s: [e]}), D && (e = D.apply(c, [e])), r(O, c, [e, b, c]), r(_, c, [c, b]))
        }

        function Z(e) {
            z++ || (W(), j && e != w && (T[I] = e), r(M, c, [c, e]), r(_, c, [c, e]))
        }

        c = e.extend({}, k, c);
        var O = c.success, M = c.error, _ = c.complete, D = c.dataFilter, P = c.callbackParameter, H = c.callback, B = c.cache, j = c.pageCache, F = c.charset, I = c.url, q = c.data, R = c.timeout, U, z = 0, W = t, X, V, J, K, Q, G;
        return S && S(function (e) {
            e.done(O).fail(M), O = e.resolve, M = e.reject
        }).promise(c), c.abort = function () {
            !(z++) && W()
        }, r(c.beforeSend, c, [c]) === !1 || z ? c : (I = I || u, q = q ? typeof q == "string" ? q : e.param(q, c.traditional) : u, I += q ? i(I) + q : u, P && (I += i(I) + encodeURIComponent(P) + "=?"), !B && !j && (I += i(I) + "_" + (new Date).getTime() + "="), I = I.replace(/=\?(&|$)/, "=" + H + "$1"), j && (U = T[I]) ? U.s ? Y(U.s[0]) : Z(U) : (E[H] = n, K = e(y)[0], K.id = l + N++, F && (K[o] = F), L && L.version() < 11.6 ? (Q = e(y)[0]).text = "document.getElementById('" + K.id + "')." + p + "()" : K[s] = s, A && (K.htmlFor = K.id, K.event = h), K[d] = K[p] = K[v] = function (e) {
            if (!K[m] || !/i/.test(K[m])) {
                try {
                    K[h] && K[h]()
                } catch (t) {
                }
                e = C, C = 0, e ? Y(e[0]) : Z(a)
            }
        }, K.src = I, W = function (e) {
            G && clearTimeout(G), K[v] = K[d] = K[p] = null, x[g](K), Q && x[g](Q)
        }, x[f](K, J = x.firstChild), Q && x[f](Q, J), G = R > 0 && setTimeout(function () {
            Z(w)
        }, R)), c)
    }

    var s = "async", o = "charset", u = "", a = "error", f = "insertBefore", l = "_jqjsp", c = "on", h = c + "click", p = c + a, d = c + "load", v = c + "readystatechange", m = "readyState", g = "removeChild", y = "<script>", b = "success", w = "timeout", E = window, S = e.Deferred, x = e("head")[0] || document.documentElement, T = {}, N = 0, C, k = {callback: l, url: location.href}, L = E.opera, A = !!e("<div>").html("<!--[if IE]><i><![endif]-->").find("i").length;
    O.setup = function (t) {
        e.extend(k, t)
    }, e.jsonp = O
})(jQuery)

var dateFormat = function () {
    var l = /d{1,4}|m{1,4}|yy(?:yy)?|([HhMsTt])\1?|[LloSZ]|"[^"]*"|'[^']*'/g, m = /\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\d{4})?)\b/g, u = /[^-+\dA-Z]/g, d = function (a, c) {
        a = String(a);
        for (c = c || 2; a.length < c;)a = "0" + a;
        return a
    };
    return function (a, c, h) {
        var f = dateFormat;
        1 != arguments.length || "[object String]" != Object.prototype.toString.call(a) || /\d/.test(a) || (c = a, a = void 0);
        a = a ? new Date(a) : new Date;
        if (isNaN(a))throw SyntaxError("invalid date");
        c = String(f.masks[c] || c || f.masks["default"]);
        "UTC:" == c.slice(0, 4) && (c = c.slice(4), h = !0);
        var b = h ? "getUTC" : "get", g = a[b + "Date"](), p = a[b + "Day"](), k = a[b + "Month"](), q = a[b + "FullYear"](), e = a[b + "Hours"](), r = a[b + "Minutes"](), s = a[b + "Seconds"](), b = a[b + "Milliseconds"](), n = h ? 0 : a.getTimezoneOffset(), t = {d: g, dd: d(g), ddd: f.i18n.dayNames[p], dddd: f.i18n.dayNames[p + 7], m: k + 1, mm: d(k + 1), mmm: f.i18n.monthNames[k], mmmm: f.i18n.monthNames[k + 12], yy: String(q).slice(2), yyyy: q, h: e % 12 || 12, hh: d(e % 12 || 12), H: e, HH: d(e), M: r, MM: d(r), s: s,
            ss: d(s), l: d(b, 3), L: d(99 < b ? Math.round(b / 10) : b), t: 12 > e ? "a" : "p", tt: 12 > e ? "am" : "pm", T: 12 > e ? "A" : "P", TT: 12 > e ? "AM" : "PM", Z: h ? "UTC" : (String(a).match(m) || [""]).pop().replace(u, ""), o: (0 < n ? "-" : "+") + d(100 * Math.floor(Math.abs(n) / 60) + Math.abs(n) % 60, 4), S: ["th", "st", "nd", "rd"][3 < g % 10 ? 0 : (10 != g % 100 - g % 10) * g % 10]};
        return c.replace(l, function (a) {
            return a in t ? t[a] : a.slice(1, a.length - 1)
        })
    }
}();
dateFormat.masks = {"default": "ddd mmm dd yyyy HH:MM:ss", shortDate: "m/d/yy", mediumDate: "mmm d, yyyy", longDate: "mmmm d, yyyy", fullDate: "dddd, mmmm d, yyyy", shortTime: "h:MM TT", mediumTime: "h:MM:ss TT", longTime: "h:MM:ss TT Z", isoDate: "yyyy-mm-dd", isoTime: "HH:MM:ss", isoDateTime: "yyyy-mm-dd'T'HH:MM:ss", isoUtcDateTime: "UTC:yyyy-mm-dd'T'HH:MM:ss'Z'"};
dateFormat.i18n = {dayNames: "Sun Mon Tue Wed Thu Fri Sat Sunday Monday Tuesday Wednesday Thursday Friday Saturday".split(" "), monthNames: "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec January February March April May June July August September October November December".split(" ")};
Date.prototype.format = function (l, m) {
    return dateFormat(this, l, m)
};

SIMON = {params: {percentage: 1, amount: 5, numTests: 5, post: !0, print: !0, console: "console"}, urls: {home: "http://simon.lacnic.net/simon/", configs: "http://simon.lacnic.net/simon/web_configs/", offline: "http://simon.lacnic.net/simon/postxmlresult/offline", post: "http://simon.lacnic.net/simon/postxmlresult/latency", ipv6ResolveURL: "http://simon.v6.labs.lacnic.net/cemd/getip/jsonp/", ipv4ResolveURL: "http://simon.v4.labs.lacnic.net/cemd/getip/jsonp/"}, workflow: {latency: !1, throughput: !1}, points: [], running: !0, siteOnLineTimeout: 6E3,
    latencyTimeout: 1E3, testType: "tcp_web", countryCode: "", ipv4Address: "", ipv6Address: "", DEFAULT_TIME: -1, before_start: function () {
    }, after_end: function () {
    }, before_each: function () {
    }, after_each: function (a) {
    }, after_points: function () {
    }, init: function () {
        if (Math.random() < SIMON.params.percentage)return SIMON.running = !0, SIMON.before_start(), SIMON.getCountry();
        SIMON.printr("N/A")
    }, stop: function () {
        SIMON.printr("Stopping tests...it may take a while");
        SIMON.running = !1
    }, getCountry: function () {
        SIMON.printr("Getting user country...");
        $.ajax({type: "GET", url: SIMON.urls.home + "getCountry", contentType: "text/javascript", dataType: "jsonp", crossDomain: !0, context: this, success: function (a) {
            SIMON.countryCode = a.cc;
            SIMON.getMyIPAddress(SIMON.urls.ipv6ResolveURL)
        }})
    }, getTestsConfigs: function () {
        SIMON.printr("Fetching tests configurations...");
        $.ajax({url: SIMON.urls.configs, dataType: "jsonp", crossDomain: !0, context: this}).success(function (a) {
            SIMON.workflow.latency = 1 == a.configs.latency ? !0 : !1;
            SIMON.workflow.throughput = 1 == a.configs.throughput ? !0 : !1;
            "" != SIMON.ipv6Address ? this.getPoints(6) : this.getPoints(4)
        })
    }, getPoints: function (a) {
        $.ajax({url: SIMON.urls.home + "web_points/" + SIMON.params.amount + "/" + a, dataType: "jsonp", crossDomain: !0, context: this}).success(function (a) {
            SIMON.points = [];
            for (i in a.points) {
                var c = a.points[i], d = {ip: c.ip, url: c.url, country: c.country, countryName: c.countryName, city: c.city, region: c.region, results: [], throughputResults: [], online: !1, onlineFinished: !1}, c = $.parseJSON(c.images);
                for (j in c) {
                    var e = c[j];
                    d.throughputResults.push({path: e.path,
                        width: e.width, height: e.height, byteSize: e.size, name: e.name, timeout: e.timeout, type: e.type, time: SIMON.DEFAULT_TIME})
                }
                SIMON.points.push(d)
            }
            SIMON.after_points();
            SIMON.siteOnLine(SIMON.points[0])
        }).complete()
    }, siteOnLine: function (a) {
        SIMON.printr("Checking site " + a.ip + " (" + a.country + ")");
        var b;
        4 == this.getIPversion(a.ip) ? b = "http://" + a.ip + "/" : 6 == this.getIPversion(a.ip) && (b = "http://[" + a.ip + "]/");
        $.ajax({url: b, dataType: "jsonp", crossDomain: !0, context: this, timeout: SIMON.siteOnLineTimeout, complete: function (b, d) {
            a.onlineFinished = !0;
            if (/2[0-9]{2}|50[01234]|401|407/.test(b.status))a.online = !0; else {
                a.online = !1;
                var e = [];
                e.push(a);
                e = SIMON.buildOfflineXML(e);
                SIMON.printr("Reporting offline test point...");
                SIMON.postResults(SIMON.urls.offline, e)
            }
            SIMON.saveTestPoint(a);
            SIMON.startPointTest(a)
        }})
    }, saveTestPoint: function (a) {
        var b = this.getTestPointIndex(a);
        SIMON.points[b] = a
    }, startPointTest: function (a) {
        if (a.online)for (var b = 0; b < SIMON.params.numTests; b++)setTimeout(function () {
            SIMON.latencyTest(a)
        }, SIMON.latencyTimeout * b); else SIMON.abortTestPointTest(a),
            b = SIMON.getNextPoint(a), -1 != b && SIMON.siteOnLine(b)
    }, latencyTest: function (a) {
        var b, c, d;
        d = "6" == this.getIPversion(a.ip) ? "http://[" + a.ip + "]/" + Math.random() : "http://" + a.ip + "/" + Math.random();
        SIMON.before_each();
        $.jsonp({type: "GET", url: d, dataType: "jsonp", timeout: SIMON.latencyTimeout, xhrFields: {withCredentials: !0}, beforeSend: function (a) {
            a.overrideMimeType && a.setRequestHeader("Connection", "close")
        }, error: function (d, h) {
            "timeout" == h ? a.results.push("timeout") : (c = +new Date - b, a.results.push(c), SIMON.printr("Measuring latency to " +
                a.ip + " - " + c + " ms"), SIMON.after_each(c));
            SIMON.saveTestPoint(a);
            if (SIMON.testerFinished(a)) {
                var f = [];
                f.push(a);
                var g;
                "4" == SIMON.getIPversion(a.ip) ? g = SIMON.buildXML(f, SIMON.ipv4Address) : "6" == SIMON.getIPversion(a.ip) && (g = SIMON.buildXML(f, SIMON.ipv6Address));
                SIMON.postResults(SIMON.urls.post, g);
                f = SIMON.getNextPoint(a);
                -1 != f ? SIMON.siteOnLine(f) : (SIMON.after_end(), SIMON.printr("Thank you!"))
            }
        }});
        b = +new Date
    }, abortTestPointTest: function (a) {
        for (var b = a.results.length; b < SIMON.params.numTests; b++)a.results.push("aborted");
        for (b in a.throughputResults)a.throughputResults[b].time == SIMON.DEFAULT_TIME && (a.throughputResults[b].time = "aborted")
    }, buildOfflineXML: function (a) {
        if (a instanceof Array) {
            var b = new Date, c;
            c = '<?xml version="1.0" encoding="UTF-8"?><report xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">';
            for (i in a)c += "<point>", c = c + "<destination_ip>" + a[i].ip + "</destination_ip>", c = c + "<date>" + b.format("yyyy-mm-dd") + "</date>", c += "</point>";
            return c + "</report>"
        }
        return 1
    }, getMyIPAddress: function (a) {
        $.ajax({type: "GET",
            url: a, dataType: "jsonp", timeout: 5E3, crossDomain: !0, context: this, success: function (a) {
                "4" == this.getIPversion(a.ip) ? (SIMON.ipv4Address = a.ip, SIMON.getTestsConfigs()) : "6" == this.getIPversion(a.ip) && (SIMON.ipv6Address = a.ip, SIMON.getMyIPAddress(SIMON.urls.ipv4ResolveURL))
            }, error: function (a, c, d) {
                "" == SIMON.ipv4Address && SIMON.getMyIPAddress(SIMON.urls.ipv4ResolveURL)
            }, complete: function () {
            }})
    }, getTestPointIndex: function (a) {
        for (i in SIMON.points)if (SIMON.points[i].ip == a.ip)return i;
        return null
    }, getNextPoint: function (a) {
        a =
            this.getTestPointIndex(a);
        a++;
        return a < SIMON.points.length ? SIMON.points[a] : -1
    }, getPrintTimeWithOffset: function (a) {
        for (var b = a.getHours().toString(), c = a.getMinutes().toString(), d = a.getSeconds().toString(); 2 > b.length;)b = "0" + b;
        for (; 2 > c.length;)c = "0" + c;
        for (; 2 > d.length;)d = "0" + d;
        b = b + ":" + c + ":" + d;
        a = SIMON.getPrintOffset(a);
        return b + a
    }, buildXML: function (a, b) {
        SIMON.printr("Building data...");
        if (a instanceof Array && 0 < a.length) {
            var c = new Date, d;
            d = '<?xml version="1.0" encoding="UTF-8"?><simon xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><version>2</version>';
            d = d + "<date>" + c.format("yyyy-mm-dd") + "</date>";
            d = d + "<time>" + SIMON.getPrintTimeWithOffset(c) + "</time>";
            d = d + "<local_country>" + SIMON.countryCode + "</local_country>";
            for (c = 0; c < a.length; c++) {
                var e = SIMON.quartiles.filter(SIMON.getNumericalValues(a[c].results));
                a[c].results.length != e.length && SIMON.printr("Stripped " + (a[c].results.length - e.length) + " outliers...");
                SIMON.printr(SIMON.summary(e));
                d += "<test>";
                d = d + "<destination_ip>" + a[c].ip + "</destination_ip>";
                d = d + "<origin_ip>" + b + "</origin_ip>";
                d = d + "<testtype>" +
                    SIMON.testType + "</testtype>";
                d = d + "<number_probes>" + e.length + "</number_probes>";
                d = d + "<min_rtt>" + Math.floor(SIMON.getMin(e)) + "</min_rtt>";
                d = d + "<max_rtt>" + Math.floor(SIMON.getMax(e)) + "</max_rtt>";
                d = d + "<ave_rtt>" + Math.floor(SIMON.getMean(e)) + "</ave_rtt>";
                d = d + "<dev_rtt>" + Math.floor(SIMON.getStdDev(e)) + "</dev_rtt>";
                d = d + "<median_rtt>" + Math.floor(SIMON.getMedian(e)) + "</median_rtt>";
                d = d + "<packet_loss>" + SIMON.getLost(a[c].results) + "</packet_loss>";
                d = d + "<ip_version>" + SIMON.getIPversion(a[c].ip) + "</ip_version>";
                d += "</test>"
            }
            d += "<tester>JavaScript</tester>";
            d += "<tester_version>2</tester_version>";
            d = d + "<user_agent>" + navigator.userAgent + "</user_agent>";
            d = d + "<url>" + window.location.hostname + "</url>";
            return d += "</simon>"
        }
    }, getPrintOffset: function (a) {
        var b = -1 * a.getTimezoneOffset();
        a = 0 >= b ? "-" : "+";
        for (var c = Math.floor(b / 60).toString(), c = c.replace(/[+-]/, ""), b = (b % 60).toString(); 2 > b.length;)b = "0" + b;
        for (; 2 > c.length;)c = "0" + c;
        return a + c + ":" + b
    }, getNumericalValues: function (a) {
        if (a instanceof Array && 0 < a.length) {
            var b = [];
            for (i in a)"number" == typeof a[i] && b.push(a[i]);
            return b
        }
        return 0
    }, sortfunction: function (a, b) {
        return a - b
    }, getMin: function (a) {
        return a instanceof Array && 0 < a.length ? (a.sort(function (a, c) {
            return a - c
        }), a[0]) : 0
    }, getMax: function (a) {
        return a instanceof Array && 0 < a.length ? (a.sort(function (a, c) {
            return a - c
        }), a.reverse(), a[0]) : 0
    }, getMedian: function (a) {
        if (a instanceof Array && 0 < a.length) {
            a.sort(function (a, b) {
                return a - b
            });
            var b = Math.floor(a.length / 2);
            return a.length % 2 ? a[b] : (a[b - 1] + a[b]) / 2
        }
        return 0
    }, getStdDev: function (a) {
        if (a instanceof
            Array && 0 < a.length) {
            var b = Array(a.length), c = this.getMean(a);
            for (i in a)b.push(Math.pow(a[i] - c, 2));
            if (0 != b.length - 1)return Math.round(Math.sqrt(this.sum(b) / (b.length - 1)))
        }
        return 0
    }, getMean: function (a) {
        return a instanceof Array && 0 < a.length ? Math.floor(SIMON.sum(a) / a.length) : 0
    }, quartiles: {q1: function (a) {
        a.sort(function (a, c) {
            return a - c
        });
        return a[Math.floor(.25 * a.length)]
    }, q3: function (a) {
        a.sort(function (a, c) {
            return a - c
        });
        return a[Math.floor(.75 * a.length)]
    }, iqr: function (a) {
        return SIMON.quartiles.q3(a) - SIMON.quartiles.q1(a)
    },
        filter: function (a) {
            var b = SIMON.quartiles.q1(a), c = SIMON.quartiles.q3(a), d = c - b;
            return SIMON.stats.grater_than(SIMON.stats.lower_than(a, c + 1.5 * d), b - 1.5 * d)
        }}, stats: {grater_than: function (a, b) {
        var c = [];
        for (i in a)a[i] > b && c.push(a[i]);
        return c
    }, lower_than: function (a, b) {
        var c = [];
        for (i in a)a[i] < b && c.push(a[i]);
        return c
    }, log: function (a) {
        var b = [];
        for (i in a)b.push(Math.log(a[i]));
        return b
    }, exp: function (a) {
        var b = [];
        for (i in a)b.push(Math.exp(a[i]));
        return b
    }}, sum: function (a) {
        var b = 0;
        if (a instanceof Array)for (i in a)"number" == typeof a[i] && (b += a[i]);
        return b
    }, getLost: function (a) {
        var b = 0;
        if (a instanceof Array && 0 < a.length)for (i in a)"number" != typeof a[i] && b++;
        return b
    }, getIPversion: function (a) {
        return-1 < a.indexOf(":") ? "6" : -1 < a.indexOf(".") ? "4" : -1
    }, testerFinished: function (a) {
        return a.results.length == SIMON.params.numTests ? !0 : !1
    }, postResults: function (a, b) {
        if (!SIMON.params.post)return!1;
        SIMON.printr("Posting results...");
        $.ajax({type: "POST", url: a, data: b, success: function (a) {
            return!0
        }, error: function (a, b, e) {
            return!1
        }})
    }, printr: function (a) {
        SIMON.params.print &&
            null != document.getElementById(SIMON.params.console) && (cur_html = $("#" + SIMON.params.console).html(), $("#" + SIMON.params.console).html(cur_html + a + "<br>"), a = $("#" + SIMON.params.console).scrollTop(), $("#" + SIMON.params.console).scrollTop(a + 30))
    }, summary: function (a) {
        return"min=" + Math.floor(SIMON.getMin(a)) + " ms max=" + Math.floor(SIMON.getMax(a)) + " ms mean=" + Math.floor(SIMON.getMean(a)) + " ms std. dev.=" + Math.floor(SIMON.getStdDev(a)) + " ms"
    }};

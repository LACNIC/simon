# Simon
The Simon Project was created to shed some light over Latin American and Caribbean (LAC) Internet connectivity. LAC countries are sometimes geographically close to each other, but network-wise very distanced. This logical distance that separates LAC countries has a considerable impact on Internet quality, and therefore on the region's economical development.

The project aims to provide enough information about regional connectivity in order for infrastructure investors, content providers, Internet Service Providers, and other agents to have more agreements. A rise of this kind of agreements will undoubtedly end in a better Ineternet for end-users.

Visit [the site](http://simon.lacnic.net "Proyecto Simón")! By visiting the site you help us by automatically generating measurements.

## Join us!
If you have not visited [the site](http://simon.lacnic.net "Proyecto Simón"), check it out now!

You can also help the project just by adding our JavaScript probe in your own website. It's dead simple, just include the following:
```javascript
<script src="https://cdn.dev.lacnic.net/lacnic-net-measurements.js"></script>
```

## The web project
There's a website that holds tests results, reports, charts, an API for data consumption, and more. It is a Django-based project and is located under `django/`.

## Tools
The tools used for measuring connectivity are based on a simple principle: the greater the latency between two networks, the more distanced they are apart. Under that principle the project counts with two specific tools:

- A Java Applet, located under `applet/`. It performs NTP measurements to several servers.

- JavaScript file that resides as a static file inside the Django project. It is located under `django/simon_app/static/js/simon_probe.js`. It depends on `django/simon_app/static/js/dateFormatter.js`, `Google JSONP`, and `jQuery`
 so ensure you include the three of them in your main HTML file before using the JavaScript probe. It performs TCP measurements to several web servers.


## API Reference
### Syntax
You can get the latest test results by visiting parametrised URLs. You have to follow the following syntax:
`api/latency/<country_code>/[<IP_version>]/[<YYYY>]/[<MM>]`<br>
where

- **country_code**: <a href="http://en.wikipedia.org/wiki/ISO_3166-1">ISO 3166-1</a> country code for the country to inspect the results. A country is considered part of a test if it is either the country originating or receiving a measurement.
- **IP_version**: IP protocol version  used for the tests. It can be `4` or `6`. Default value : `4`
- **YYYY**: year since. Starting year of the results. Default value: `2009`
- **MM**: month since. Default value: `01` (January)
#### Examples
Querying for

`api/latency/UY` will return all results involving Uruguay.

`api/latency/UY/2013` will return results involving Uruguay since January 2013.

`api/latency/UY/2013/06` will return results involving Uruguay since June 2013.

`api/latency/UY/6` will return all results involving Uruguay, over IPv6.

`api/latency/UY/6/2013` will return results involving Uruguay since January 2013, over IPv6.

`api/latency/UY/6/2013/06` will return results involving Uruguay since June 2013, over IPv6.



### Result object
The result is a JSON array object with the following JSON objects inside:

```
{
  `country_destination` : 2 digit ISO country code of the country targeted by the test,
  `country_origin` : 2 digit ISO country code of the country originating the test,
  `max_rtt` : maximum RTT sampled in that test,
  `date_test` : date time with time zone when the test was performed,
  `median_rtt` : test result's median value (ms),
  `min_rtt` : test result's minimum value (ms),
  `ave_rtt` : test result's average value (ms),
  `dev_rtt` : test result's standard deviation value (ms)
}
```
### Example
```
[
  {
  "country_destination": "CL",
  "country_origin": "UY",
  "max_rtt": 445,
  "date_test": "2012-11-05 19:40:19+00:00",
  "median_rtt": 411,
  "min_rtt": 403,
  "ave_rtt": 415,
  "dev_rtt": 10
  },
...
]
```

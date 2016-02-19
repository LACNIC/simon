# Simon

The Simon Project was created to shed some light over Latin American and Caribbean (LAC) Internet connectivity. LAC countries are sometimes geographically close to each other, but network-wise very distanced. This logical distance that separates LAC countries has a considerable impact on Internet quality, and therefore on the region's economical development.

The project aims to provide enough information about regional connectivity in order for infrastructure investors, content providers, Internet Service Providers, and other agents to have more agreements. A rise of this kind of agreements will undoubtedly end in a better Ineternet for end-users.

## Collaborate

```javascript
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>

<script async type="application/javascript">

(function (f, b) {
    var c = f.createElement(b), e = f.getElementsByTagName(b)[0];
    c.src = "http://simon.lacnic.net/simon/static/simon_app/js/simon_probe_plugin.js";
    c.type = "text/javascript";
    e.parentNode.insertBefore(c, e);
    c.onload = c.onreadystatechange = function () {
        SIMON.init()
    }
}(document, "script"));

</script>
```

Visit [the site](http://simon.labs.lacnic.net "Proyecto Simón")! By visiting the site you help us by automatically generating measurements.

![Build status](https://travis-ci.org/LACNIC/simon.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/LACNIC/simon/badge.svg?branch=master&service=github)](https://coveralls.io/github/LACNIC/simon?branch=master)


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/LACNIC/simon/trend.png)](https://bitdeli.com/free "Bitdeli Badge")


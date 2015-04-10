#!/usr/bin/env bash

# type traceroute6 >/dev/null 2>&1 && echo si || echo no && exit 1
type traceroute >/dev/null 2>&1 || (echo "Traceroute not installed. Aborting." && exit 1)

HOST=199.7.83.42

output=$(traceroute $HOST)
curl --data "output=$output" http://simon.lacnic.net/simon/post/traceroute/
exit 0
#!/usr/bin/env bash

# TODO obtener dirección por la cual hace el traceroute efectivamente

HOST4=199.7.83.42
HOST6=2001:500:3::42
postEndpoint=http://127.0.0.1:8000/post/traceroute/

measure() {
    protocol=$2
    ipversion=$1

    case $ipversion in
        "4")
            case $protocol in
                "icmp")
                ;;
    #            "tcp")
    #            ;;
    #            "udp")
    #            ;;
                *)
                    exit 1
                ;;
            esac
        ;;
        "6")
        ;;
        *)
            exit 1
        ;;
    esac



    echo "Running $protocol v$ipversion tests..."
    if (( $ipversion == "4" ))
    then
        output=$(traceroute -P $protocol -q 3 $HOST4)
    else
        output=$(traceroute6 -q 3 $HOST6)
     fi

    echo "Posting results..."
    curl --data "output=$output" $postEndpoint
#    exit 0
}

type traceroute >/dev/null 2>&1 || (echo "Traceroute not installed. Aborting." && exit 1)
measure "4" "icmp"


type traceroute6 >/dev/null 2>&1 || (echo "Traceroute 6 not installed. Aborting." && exit 0)
measure "6"

exit 0
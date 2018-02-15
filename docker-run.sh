#!/bin/sh

apk add --no-cache --upgrade nmap nmap-nselibs nmap-scripts

python3 /network-monitoring.py/network-monitoring.py "$@"
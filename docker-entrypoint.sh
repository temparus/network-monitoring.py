#!/bin/sh

if [[ "x$MONITORING_DAEMON" == "x1" ]]; then
  crond -f
else
  /network-monitoring.py/docker-run.sh "$@"
fi
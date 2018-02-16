#!/bin/sh

if [[ "x$MONITORING_DAEMON" != "x" ]]; then
  crond -f
else
  /network-monitoring.py/docker-run.sh "$@"
fi
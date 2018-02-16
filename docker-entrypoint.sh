#!/bin/sh

if [[ "x$MONITORING_DAEMON" != "x" ]]; then
  crontab /crontab.txt
  crond -f
else
  /network-monitoring.py/docker-run.sh "$@"
fi
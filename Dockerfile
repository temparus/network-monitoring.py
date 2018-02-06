FROM alpine:3.5

MAINTAINER Sandro Lutz code@temparus.ch

RUN apk add --no-cache nmap python3

ADD . /network-monitor.py/

WORKDIR /network-monitor.py

ENTRYPOINT ["/bin/sh"]
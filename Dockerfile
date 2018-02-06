FROM alpine:3.5

MAINTAINER Sandro Lutz code@temparus.ch

RUN apk add --no-cache nmap python3

ADD . /network-monitoring.py/

WORKDIR /network-monitoring.py

ENTRYPOINT ["/bin/sh"]
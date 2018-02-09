FROM alpine:3.5

MAINTAINER Sandro Lutz code@temparus.ch

RUN apk add --no-cache python3 nmap nmap-nselibs nmap-scripts

ADD . /network-monitoring.py/

WORKDIR /network-monitoring.py

RUN chmod 755 network-monitoring.py

ENTRYPOINT ["./network-monitoring.py"]
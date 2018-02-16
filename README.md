# Network Monitoring Tool

This tool monitors whole subnets (IP-Address ranges) for hardware changes (MAC address) and vulnerabilities.

## Requirements

* python 3.x
* nmap version 7.00 or higher
* sendmail *(optional, needed only for email notifications)*
* cron *(optional, needed only for regular checks)*

*Please note that all requirements are met automatically when using the docker container.*

## Setup

1. Get source files
    * **Docker** Use the official image (<https://hub.docker.com/r/temparus/network-monitoring-py/>)
    * **Standalone** Just clone this repository to a directory on your machine.
2. Run network-monitoring.py once
    * **Docker**
      ```bash
      docker run --net=host --volume /path/to/config.json:/network-monitor.py/config.json -ti \
      temparus/network-monitoring-py:latest
      ```
    * **Docker-Compose**
      ```yaml
      version: "3"
      services:
        network-monitoring-py:
          image: temparus/network-monitoring-py:latest
          network_mode: "host"
          volumes:
            - /path/to/config.json:/network-monitor.py/config.json
      ```
    * **Standalone**
      ```bash
      python3 /path/to/network-monitoring.py/network-monitoring.py --config /path/to/config.json
      ```
3. Run network-monitoring.py wiht `cron`
    * **Docker-Compose** Create a valid crontab and set the environment variable `MONITORING_DAEMON = 1`.

      Crontab example:
      ```cron
      0    3 * * * /network-monitoring.py/docker-run.sh vulnerability-scan all --email
      */10 * * * * /network-monitoring.py/docker-run.sh network-scan all --email
      ```
      ```yaml
      version: "3"
      services:
        network-monitoring-py:
          image: temparus/network-monitoring-py:latest
          network_mode: "host"
          environment:
            - MONITORING_DAEMON=1
          volumes:
            - /path/to/config.json:/network-monitor.py/config.json
            - /path/to/crontab.txt:/crontab.txt
      ```
    * **Standalone** execute `crontab -e` and add the following lines there *(adapt to your requirements)*
      ```cron
      0    3 * * * /path/to/network-monitoring.py/network-monitoring.py vulnerability-scan all --email
      */10 * * * * /path/to/network-monitoring.py/network-monitoring.py network-scan all --email
      ```
> The option `net=host` is necessary because the ARP packets are not forwarded by the docker bridge network.

> Please make sure to whitelist your monitoring server on your monitored devices if you are using `fail2ban`.

## Configuration File

The default configuration file is `./config.json`. It needs to have the following structure:

```json
{
    "name": "net_name",
    "description": "Network Name",
    "subnet": "ip range in CIDR notation",
    "email": "network administrator's email address",
    "notifications": ["unknown-device", "wrong-hostname", "vulnerability"],
    "monitoring": "all",
    "hosts": [
      {
        "hostname": "hostname",
        "ip": "ip address (must be within the declared subnet above!)",
        "mac": "device MAC address",
        "exclude": ["vulnerability", "mac", "hostname"]
      }
    ]
}
```

### Explanation of keys

* `name`: needed to specify this network as action parameter
* `monitoring`: can be `all` (scan complete subnet for unkown devices) or `list-only` (only scan specified hosts).
* `exclude`: must be an array containing at most `vulnerability` (skip vulnerability scan for this host) and `mac` (do not check if MAC address matches).

## Usage

```bash
usage: network-monitoring.py [-h] [--email] [--verbose] [--config config.json]
                             [--version]
                             {network-scan,vulnerability-scan} param

Monitors whole subnets (IP-Address ranges) for hardware changes (MAC address)
and vulnerabilities.

positional arguments:
  {network-scan,vulnerability-scan}
                        action to be performed
  param                 parameter for the choosen action

optional arguments:
  -h, --help            show this help message and exit
  --email, -e           send email notifications instead of printing to the
                        console
  --verbose, -v         prints more output to the console
  --config config.json, -c config.json
                        path to the configuration file
  --version             show program's version number and exit

```

## License

Copyright (C) 2018 Sandro Lutz \<code@temparus.ch\>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Network Monitoring Tool
=======================

This tool monitors whole subnets (IP-Address ranges) for hardware changes (MAC address) and vulnerabilities.

## Requirements
* nmap version 7.00 or higher
* cron (optional, needed only for regular checks)

## Setup
Just copy the source files to a directory on your machine.

## Configuration File

The default configuration file is `./config.json`. It needs to have the following structure:

```
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
        "mac": "device MAC address"
        "exclude": ["vulnerability", "mac", "hostname"]
      }
    ]
}
```

#### Explanation of keys:
* `name`: needed to specify this network as action parameter
* `monitoring`: can be `all` (scan complete subnet for unkown devices) or `list-only` (only scan specified hosts).
* `exclude`: must be an array containing at most `vulnerability` (skip vulnerability scan for this host) and `mac` (do not check if MAC address matches).

## Usage
< to be added soon >

## License
Copyright (C) 2018 Sandro Lutz \<<code@temparus.ch>\>

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import argparse
import ipaddress
import json
from config import *
from utils import *
from network_scan import *
from host_scan import *

ACTIONS = ['network-scan', 'vulnerability-scan']

parser = argparse.ArgumentParser(prog='network-monitoring.py',
          description='Monitors whole subnets (IP-Address ranges) for hardware changes (MAC address) and vulnerabilities.')
parser.add_argument('action', nargs=1, choices=ACTIONS, help='action to be performed')
parser.add_argument('param', nargs=1, help='parameter for the choosen action')
parser.add_argument('--email', '-e', action="store_true",
                   help='send email notifications instead of printing to the terminal')
parser.add_argument('--config', '-c', metavar='config.json', nargs=1, type=argparse.FileType('r'),
                   default='config.json', help='path to the configuration file')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

# Check dependencies first
if not hasNmap():
  print("nmap is not installed. Please install nmap version 7.00 or newer.")
  exit(3)

data = json.load(args.config)

#if args.action is not None and len(args.action) not in (0, 2):
#    parser.error('Either give no values for action, or two, not {}.'.format(len(args.action)))

# Perform requested action
result = None
if type(args.action) is list: args.action = args.action[0]
if type(args.param) is list: args.param = args.param[0]

if args.action == 'network-scan':
  if args.param == 'all':
    result = network_scan(data)
  else:
    try:
      ip_net = ipaddress.ip_network(args.param)
      result = network_scan({'subnet': str(ip_net), 'monitoring': 'all'})
    except ValueError:
      # Not a valid subnet -> maybe a network name?
      for network in data:
        if network.get('name', '') == args.param:
          result = network_scan(network)
      if result is None:
        parser.error('network param "' + args.param + '" is invalid.')
elif args.action == 'vulnerability-scan':
  if args.param == 'all':
    hosts = []
    for network in data:
      hosts += network.get('hosts', [])
    result = host_scan(hosts)
  else:
    try:
      ip = ipaddress.ip_address(args.param)
      result = host_scan({'ip': str(ip)})
    except ValueError:
      # Not a valid ip address -> maybe a host name?
      for network in data:
        for host in network.get('hosts', []):
          if host.get('name', '') == args.param:
            result = host_scan(host)
            break;
        if result is not None:
          break;
      if result is None:
        # No host configuration found.
        # Just try to scan as it may be a hostname
        print('Scanning unknown host ' + args.param)
        result = host_scan({'hostname': args.param})

if result is not None:
  if args.email:
    for key, value in result.items():
      if key != 'none':
        if type(value.get('message', [])) is not list:
          value['message'] = [ value.get('message', []) ]
        for message in value.get('message', []):
          message = '############ Network Monitoring ############\n' + \
                     message + \
                    '############## End of report ###############\n'
          sendEmail(key, value.get('subject', 'Alert: Network Monitoring'), message)
  else:
    print('############ Network Monitoring ############\n')
    if type(value.get('none', '')) is list:
      for message in value.get('none', []):
        print(message)
    else:
      print(result.get('none', ''))
    print('############## End of report ###############\n')
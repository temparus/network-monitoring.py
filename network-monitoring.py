#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import argparse
import ipaddress
import json
from utils import *
from network_scan import *
from host_scan import *

ACTIONS = ['network-scan', 'vulnerability-scan']

parser = argparse.ArgumentParser(prog='network-monitoring.py',
          description='Monitors whole subnets (IP-Address ranges) for hardware changes (MAC address) and vulnerabilities.')
parser.add_argument('action', nargs=1, choices=ACTIONS, help='action to be performed')
parser.add_argument('param', nargs=1, help='parameter for the choosen action')
parser.add_argument('--email', '-e', action="store_true",
                   help='send email notifications instead of printing to the console')
parser.add_argument('--verbose', '-v', action="store_true",
                   help='prints more output to the console')
parser.add_argument('--config', '-c', metavar='config.json', nargs=1, type=argparse.FileType('r'),
                   default='config.json', help='path to the configuration file')
parser.add_argument('--version', action='version', version='%(prog)s 0.1')
args = parser.parse_args()

# Check dependencies first
if not hasNmap():
  print("network-monitoring.py: error: nmap is not installed. Please install nmap version 7.00 or newer.")
  exit(3)

# Read configuration file
data = json.load(args.config)
for network in data:
  for host in network.get('hosts', []):
    hostExcludeSet = set(host.get('exclude', []))
    networkExcludeSet = set(network.get('exclude', []))
    newExcludes = networkExcludeSet - hostExcludeSet
    
    host['exclude'] = host.get('exclude', []) + list(newExcludes)

# Perform requested action
result = None
if type(args.action) is list: args.action = args.action[0]
if type(args.param) is list: args.param = args.param[0]

if args.action == 'network-scan':
  if args.param == 'all':
    if args.verbose:
      print('Scanning all known networks (' + str(len(data)) + ' networks)\n')
    result = network_scan(data)
  else:
    try:
      ip_net = ipaddress.ip_network(args.param)
      if args.verbose:
        print('Scanning network ' + str(ip_net) +'\n')
      result = network_scan({'subnet': str(ip_net), 'monitoring': 'all'})
    except ValueError:
      # Not a valid subnet -> maybe a network name?
      for network in data:
        if network.get('name', '') == args.param:
          if args.verbose:
            print('Scanning network "' + args.param +'"\n')
          result = network_scan(network)
      if result is None:
        parser.error('network param "' + args.param + '" is invalid.')
elif args.action == 'vulnerability-scan':
  if args.param == 'all':
    hosts = []
    for network in data:
      hosts += network.get('hosts', [])
    if args.verbose: 
      print('Scanning all known hosts (' + str(len(hosts)) + ' hosts)\n\n')
    result = host_scan(hosts)
  else:
    try:
      ip = ipaddress.ip_address(args.param)
      if args.verbose: 
        print('Scanning host ' + str(ip) + '\n')
      result = host_scan({'ip': str(ip)})
    except ValueError:
      # Not a valid ip address -> maybe a host name?
      for network in data:
        for host in network.get('hosts', []):
          if host.get('hostname', '') == args.param:
            if args.verbose: 
              print('Scanning known host ' + args.param + '\n')
            result = host_scan(host)
            break;
        if result is not None:
          break;
      if result is None:
        # No host configuration found.
        # Just try to scan as it may be a hostname
        if args.verbose: 
          print('Scanning unknown host ' + args.param + '\n')
        result = host_scan({'hostname': args.param})

if result is not None:
  if args.email:
    for key, value in result.items():
      if key != 'none':
        if type(value) is not list:
          value = [ value ]
        for email in value:
          message = '########## network-monitoring.py ###########\n' + \
                     email.get('message', '') + \
                    '############## End of report ###############\n'
          sendEmail(key, email.get('subject', 'Alert: Network Monitoring') + ' [network-monitoring.py]', message)
      if args.verbose:
        print(len(value) + ' emails sent to ' + key + '\n')
  else:
    print('########## network-monitoring.py ###########\n')
    if type(result.get('none', '')) is list:
      for message in value.get('none', []):
        print(message)
    else:
      print(result.get('none', ''))
    print('############## End of report ###############\n')

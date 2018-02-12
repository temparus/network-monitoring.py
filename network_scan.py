# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import os
import sys
import socket
import ipaddress
import subprocess
from utils import *

def network_scan(networks):
  if type(networks) is not list: networks = [ networks ]

  messages = {'none': ''}

  for network in networks:
    problemsKnownHosts = list()
    problemsUnknownHosts = list()

    if 'notifications' not in network or network['notifications'] == 'all':
      network['notifications'] = ['unknown-device', 'wrong-hostname']
    # config conflict will always generate a notification
    network['notifications'].append('config-conflict')

    counter = 0
    output = None
    while (counter < 3 and output is None):
      try:
        if type(ipaddress.ip_network(network['subnet'])) is ipaddress.IPv6Network:
          options = '-6sP'
        else:
          options = '-sP'
        proc = subprocess.Popen(['nmap', options, network['subnet']], stdout=subprocess.PIPE)
        output = proc.communicate()[0].decode()
      except KeyboardInterrupt:
        proc.kill()
        return {'none': 'KeyboardInterrupt received! Network scan stopped.\n'}
      except:
        counter += 1
        output = None

    if (output is not None):
      outputNmap = output.split('\n')

      hostProblems = list()
      current_host = None
      configured_host = None
      configured_host_conflict = False

      for line in outputNmap:
        if line.startswith('Nmap'):
          if current_host is not None:
            if configured_host is None:
              if network.get('monitoring', 'all') == 'all':
                problemsUnknownHosts.append({'hostname': current_host['hostname'], 'ip': current_host['ip'], 'mac': current_host['mac']})
            else:
              if ('wrong-hostname' in network['notifications'] and
                'hostname' not in configured_host.get('exclude', []) and
                current_host['hostname'] != configured_host.get('hostname', current_host['hostname'])):
                  hostProblems.append({'problem': 'wrong-hostname', 'hostname': current_host['hostname']})
              if ('unknown-device' in network['notifications'] and
                'mac' not in configured_host.get('exclude', []) and
                current_host['mac'] != configured_host.get('mac', current_host['mac']) and
                current_host['mac'] != 'unknown'):
                hostProblems.append({'problem': 'unknown-device', 'mac': current_host['mac']})

              if len(hostProblems) > 0:
                configured_host['problems'] = hostProblems
                problemsKnownHosts.append(configured_host)

          current_host = None
          configured_host = None
          configured_host_conflict = False
          hostProblems = list()

          tmpStrings = line[21:].split(' ')
          if len(tmpStrings) == 2:
            current_host = {
              'hostname': tmpStrings[0],
              'ip': tmpStrings[1][1:-1],
              'mac': 'unknown',
            }

            for host in network['hosts']:
              if current_host['ip'] == host['ip']:
                if configured_host is not None:
                  configured_host = None
                  configured_host_conflict = True
                  hostProblems.append({'problem': 'config-conflict', 'host': host})
                else:
                  configured_host = host

        elif current_host is not None and line.startswith('MAC Address: '):
          current_host['mac'] = line[13:30]

    message = '--------------------------------------------\n' \
               '# Network name: ' + network.get('description', 'not specified') + \
                 ' (' + network.get('name', 'not specified') + ')\n' \
               '# Subnet: ' + network.get('subnet', 'not specified') + '\n' \
               '# Administrator: ' + network.get('email', 'not specified') + '\n' \
               '--------------------------------------------\n\n' \

    if len(problemsKnownHosts) > 0:
      message += 'There are problems with ' + str(len(problemsKnownHosts)) + ' known host(s):\n\n'
      for knownHost in problemsKnownHosts:
        message += '* Host "' + knownHost.get('hostname', 'not specified') + \
          '" (' + knownHost.get('ip', '') + ') with registered MAC: ' + \
          knownHost.get('mac', 'none') + '\n'
        for problem in knownHost.get('problems', []):
          if problem['problem'] == 'config-conflict':
            conflictingHost = problem.get('host', {})
            message += '  - Conflicting configuration with Host "' + \
              conflictingHost.get('hostname', 'not specified') + \
              '" with register MAC: ' + conflictingHost.get('mac', 'none') + '\n'
          elif problem['problem'] == 'wrong-hostname':
            message += '  - Wrong hostname configured (Found "' + problem.get('hostname', 'not specified') + ')"\n'
          elif problem['problem'] == 'unknown-device':
            message += '  - Unknown device (Found MAC: "' + problem.get('mac', 'none') + '")\n'
        message += '\n'
      message += '\n'

    if len(problemsUnknownHosts) > 0:
      message += 'There are ' + str(len(problemsUnknownHosts)) + ' unknown host(s):\n\n'
      for unknownHost in problemsUnknownHosts:
        message += '* Found Host "' + unknownHost.get('hostname', 'not configured') + \
          '" (' + unknownHost.get('ip', '') + ') with MAC ' + \
          unknownHost.get('mac', 'none') + '\n'
      message += '\n\n'

    if output is not None and len(problemsUnknownHosts) == 0 and len(problemsKnownHosts) == 0:
      message += 'There are no detected problems with this network.\n\n'
    elif 'email' in network and len(network['email']) > 0:
      if output is None:
        message += 'Could not perform network scan! Please check the configuration of ' + socket.getfqdn() + '\n\n'
      if network.get('email', 'none') not in messages:
        messages[network.get('email', 'none')] = {'subject': '', 'message': ''}
      if len(messages[network.get('email', 'none')]['subject']) == 0:
        messages[network.get('email', 'none')]['subject'] = 'Alert: Network scan for ' + network.get('name', '')
      elif len(network.get('name', '')) > 0:
        messages[network.get('email', 'none')]['subject'] += ', ' + network.get('name', '')
      messages[network.get('email', 'none')]['message'] += message
    messages['none'] += message

  return messages

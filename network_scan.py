# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import os
import sys
import socket
import subprocess
from utils import *

def network_scan(networks):
  if type(networks) is not list: networks = [ networks ]

  messages = {'none': ''}

  for network in networks:
    problemsKnownHosts = list()
    problemsUnknownHosts = list()

    if 'notifications' not in network:
      network['notifications'] = ['unknown-device', 'wrong-hostname']
    # config conflict will always generate a notification
    network['notifications'].append('config-conflict')

    counter = 0
    output = None
    while (counter < 3 && output is None):
      try:
        output = subprocess.check_output(['nmap', '-sP', network['subnet']])
      except:
        counter += 1
        output = None

    if (output is not None):
      outputNmap = output.split('\n')

      current_host_valid = False
      current_hostname = ''
      current_ip = ''

      for line in outputNmap:
          if line.startswith('Nmap scan report for '):
              tmpStrings = line[21:].split(' ')
              if len(tmpStrings) == 2:
                current_hostname = tmpStrings[0]
                current_ip = tmpStrings[1][1:-1]
                current_host_valid = True
              else:
                current_host_valid = False
          elif current_host_valid and line.startswith('MAC Address: '):
              mac = line[13:30]
              hostConfig = None
              hostProblems = list()

              for host in network['hosts']:
                if current_ip == host['ip']:
                  if hostConfig is not None:
                    hostProblems.append({'problem': 'config-conflict', 'host': host})
                  else:
                    hostConfig = host
                    if ('wrong-hostname' in network['notifications'] and
                      'hostname' not in host.get('exclude', []) and
                      current_hostname != host.get('hostname', current_hostname)):
                      hostProblems.append({'problem': 'wrong-hostname', 'hostname': current_hostname})
                    if ('unknown-device' in network['notifications'] and
                      'mac' not in host.get('exclude', []) and
                      mac != host.get('mac', mac)):
                      hostProblems.append({'problem': 'unknown-device', 'mac': mac})

              if hostConfig is None:
                if network.get('monitoring', 'all') == 'all':
                  problemsUnknownHosts.append({'hostname': current_hostname, 'ip': current_ip, 'mac': mac})
              elif len(hostProblems) > 0:
                hostConfig['problems'] = hostProblems
                problemsKnownHosts.append(hostConfig)

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
            message += '  - Wrong hostname configured (Found "' + problem.get('hostname', 'not specified') + '"\n'
          elif problem['problem'] == 'unknown-device':
            message += '  - Unknown device (Found MAC: "' + problem.get('mac', 'none') + '"\n'
        message += '\n'
      message += '\n'

    if len(problemsUnknownHosts) > 0:
      message += 'There are ' + str(len(problemsUnknownHosts)) + ' unknown host(s):\n\n'
      for unknownHost in problemsUnknownHosts:
        message += '* Found Host "' + unknownHost.get('hostname', 'not configured') + \
          '" (' + unknownHost.get('ip', '') + ') with MAC  ' + \
          unknownHost.get('mac', 'none') + '\n'
      message += '\n\n'

    if output is not None and len(problemsUnknownHosts) == 0 and len(problemsKnownHosts) == 0:
      message += 'There are no detected problems with this network.\n\n'
    elif 'email' in network and len(network['email']) > 0:
      if output is not None:
        message += 'Could not perform network scan! Please check the configuration of ' + socket.getfqdn() + '\n\n'
      if network.get('email', 'none') not in messages:
        messages[network.get('email', 'none')] = {'subject': '', 'message': ''}
      if len(messages[network.get('email', 'none')]['subject']) == 0:
        messages[network.get('email', 'none')]['subject'] = 'Alert: Network scan for ' + network.get('name', '')
      elif len(network.get('name', '')) > 0:
        messages[network.get('email', 'none')]['subject'] += ', ' + network.get('name', '')
      messages[network.get('email', 'none')]['message'] = message
    messages['none'] += message

  return messages

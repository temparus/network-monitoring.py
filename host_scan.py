# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import re
import socket
import subprocess

def host_scan(hosts, verbose):
  if type(hosts) is not list: hosts = [ hosts ]

  messages = {'none': ''}

  for host in hosts:
    if 'vulnerability' in host.get('exclude', []):
      if verbose:
        print('Skipping host ' + host.get('hostname', host.get('ip', 'unknown')))
      continue

    counter = 0
    output = None
    while (counter < 3 and output is None):
      try:
        if verbose:
          print('Scanning host ' + host.get('hostname', host.get('ip', 'unknown')) + '(attempt ' + str(counter+1) + ')')
        output = subprocess.check_output('nmap --script vuln ' + host.get('hostname', host.get('ip', '')), shell=True).decode()
      except:
        counter += 1
        output = None

    message = '--------------------------------------------\n' \
              '# Host: ' + host.get('hostname', 'not specified') + \
                ' (' + host.get('ip', 'not specified') + ')\n' \
              '# MAC-Address: ' + host.get('mac', 'not specified') + '\n' \
              '# Administrator: ' + host.get('email', 'not specified') + '\n' \
              '--------------------------------------------\n\n' \

    if output is None:
      message += 'Failed to scan for vulnerabilities! Please check the configuration of ' + socket.getfqdn() + '\n\n'
    elif re.search('(?<!NOT )VULNERABLE', output) is not None:
      message += output + '\n\n'
      if 'email' in host:
        if host.get('email', 'fake') not in messages or type(messages.get(host.get('email', 'fake'))) is not list:
          messages[host.get('email', 'fake')] = []
        email = {'subject': 'Alert: Vulnerability scan for ' + 
                             host.get('hostname', host.get('ip', 'unknown')),
                 'message': message}
        messages[host.get('email', 'fake')].append(email)
    else:
      message += 'No known vulnerabilities found.\n\n'

    messages['none'] += message

  return messages

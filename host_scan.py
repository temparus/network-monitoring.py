# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import re
import subprocess

def host_scan(hosts):
  if type(hosts) is not list: hosts = [ hosts ]

  messages = {'none': ''}

  for host in hosts:
    if 'vulnerability' in host.get('exclude', []):
      continue

    output = subprocess.check_output('nmap --script vuln ' + host.get('hostname', host.get('ip', '')), shell=True)

    message = '--------------------------------------------\n' \
              '# Host: ' + host.get('hostname', 'not specified') + \
                ' (' + host.get('ip', 'not specified') + ')\n' \
              '# MAC-Address: ' + host.get('mac', 'not specified') + '\n' \
              '# Administrator: ' + host.get('email', 'not specified') + '\n' \
              '--------------------------------------------\n\n' \

    if re.search('(?<!NOT )VULNERABLE', output) is not None:
      message += output + '\n\n'
      if 'email' in host:
        if host.get('email', 'fake') not in messages or type(host.get('email', 'fake')) is not list:
          messages[host.get('email', 'fake')] = []
        email = {'subject': 'Alert: Vulnerability scan for ' + 
                             host.get('hostname', host.get('ip', 'unknown')),
                 'message': message}
        messages[host.get('email', 'fake')].append(email)
    else:
      message += 'No known vulnerabilities found.\n\n'

    messages['none'] += message

  return messages

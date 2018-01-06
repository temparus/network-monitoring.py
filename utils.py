# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Sandro Lutz <code@temparus.ch>
#
# This software is licensed under GPLv3, see LICENSE for details. 

import socket
import smtplib
import subprocess
from email.mime.text import MIMEText

def sendEmail(receiver_email, subject, message):
  sender_email = 'root@' + socket.getfqdn()
  msg = MIMEText(message)
  msg['Subject'] = subject
  msg['From'] = sender_email
  msg['To'] = receiver_email

  s = smtplib.SMTP('localhost')
  s.sendmail(sender_email, [receiver_email], msg.as_string())
  s.quit()

def hasNmap():
  output = subprocess.check_output(['which', 'nmap'])
  return len(output) > 0

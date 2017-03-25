#!/usr/bin/python

import urllib2
import urllib
from cookielib import CookieJar
import os
import sys

# Config
URL = sys.argv[1]
TOLERANCE = sys.argv[2] # in different characters
TEMP_FILE = '/home/me/dev/temp.txt'
SENDMAIL_PATH = "/usr/sbin/sendmail"
SENDER_ADDRESS = 'root@yourserver.com'
RECIPIENT_ADDRESS = 'you@yourserver.com'
MAIL_SUBJECT = 'Something has changed...'

# Read length of old web page version
f = open(TEMP_FILE, 'r')
len1 = len(f.read())
f.close()

# Read length of current web page version
cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
response = opener.open(URL)
html = str(response.read())
len2 = len(html)

# Write new version to file
f = open(TEMP_FILE, 'w')
f.write(html)
f.close()

def sendMail(sender, recipient, subject, text):
    sendmail_location = SENDMAIL_PATH
    p = os.popen("%s -t" % sendmail_location, "w")
    p.write("From: %s\n" % sender)
    p.write("To: %s\n" % recipient)
    p.write("Subject: %s\n" % subject)
    p.write("\n") # blank line separating headers from body
    p.write(text)
    status = p.close()
    if status != None:
           print("Sendmail exit status", status)

diff = abs(len2 - len1)
if diff > TOLERANCE:
        sendMail(SENDER_ADDRESS, RECIPIENT_ADDRESS, MAIL_SUBJECT, 'Difference is %s characters.\n%s' % (str(diff), URL))

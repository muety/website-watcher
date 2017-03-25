#!/usr/bin/python

import requests
import os
import sys
import smtplib

# Config - don't touch
URL = sys.argv[1]
TOLERANCE = int(sys.argv[2])  # in different characters
USE_SMTP = sys.argv[3] == 'true' or sys.argv[3] == 'True' or sys.argv[3] == '1' # use SMTP or not (default is local sendmail)
TEMP_FILE = '/tmp/watcher_cache.txt'

# Config - adapt to your needs!
SENDMAIL_PATH = '/usr/sbin/sendmail' # path to local sendmail binary, SMTP is not going to be used
SENDER_ADDRESS = 'noreply@example.com' # what should be the sender address of the notification mail
RECIPIENT_ADDRESS = 'you@example.com' # where to send the notification mail to
MAIL_SUBJECT = 'Something has changed...' # subject line of the mail you'll receive
SMTP_HOST = 'localhost' # SMTP server hostname or ip
SMTP_PORT = 25 # SMTP server's port, usually 25
SMTP_USERNAME = '' # username to authenticate against SMTP server; leave blank if no auth needed
SMTP_PASSWORD = '' # password to authenticate against SMTP server; leave blank if no auth needed
SMTP_STARTTLS = True # whether or not the SMTP server requires encrypted connection

# Read length of old web page version
try:
    f = open(TEMP_FILE, 'r')
    len1 = len(f.read())
    f.close()
except:
    len1 = 0

# Read length of current web page version
r = requests.get(URL)
if r.status_code is not 200:
    print('Could not fetch %s.' % URL)
    len2 = 0
else:
    len2 = len(r.text)

# Write new version to file
try:
    f = open(TEMP_FILE, 'w')
    f.write(r.text.encode('utf8'))
    f.close()
except Exception as e:
    print('Could not open file %s: %s' % (TEMP_FILE, e))

def send_mail(sender, recipient, subject, text):
    msg = "From: %s\n" % sender
    msg += "To: %s\n" % recipient
    msg += "Subject: %s\n\n" % subject
    msg += text

    if not USE_SMTP:
        sendmail_location = SENDMAIL_PATH
        p = os.popen("%s -t" % sendmail_location, "w")
        status = p.close()
        if status != None:
            print("Sendmail exit status", status)
    else:
        try:
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            smtp.ehlo()
            if SMTP_STARTTLS:
                smtp.starttls()
            smtp.ehlo()
            if SMTP_USERNAME is not None and SMTP_USERNAME is not '':
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.sendmail(SENDER_ADDRESS, [RECIPIENT_ADDRESS], msg)
            print("Successfully sent email")
            smtp.close()
        except smtplib.SMTPException as e:
            print("Error: unable to send email: ", e)


diff = abs(len2 - len1)
if diff > TOLERANCE:
    send_mail(SENDER_ADDRESS, RECIPIENT_ADDRESS, MAIL_SUBJECT,
              'Difference is %s characters.\n%s' % (str(diff), URL))

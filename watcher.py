#!/usr/bin/python
import argparse
import requests
import os
import smtplib
import sys


def send_mail(text, args):
    msg = 'From: %s\n' % args.sender_address
    msg += 'To: %s\n' % args.recipient_address
    msg += 'Subject: %s\n\n' % args.subject
    msg += text

    if not args.smtp:
        sendmail_location = args.sendmail_path
        p = os.popen('%s -t' % sendmail_location, 'w')
        status = p.close()
        if status != None:
            print('Sendmail exit status', status)
    else:
        try:
            smtp = smtplib.SMTP(args.smtp_host, args.smtp_port)
            smtp.ehlo()
            if not args.disable_tls:
                smtp.starttls()
            smtp.ehlo()
            if args.smtp_username is not None and args.smtp_username is not '':
                smtp.login(args.smtp_username, args.smtp_password)
            smtp.sendmail(args.sender_address, [args.recipient_address], msg)
            print('Successfully sent email')
            smtp.close()
        except smtplib.SMTPException as e:
            print('Error: unable to send email: ', e)


def main(args):
    # Read length of old web page version
    try:
        with open(args.tmp_file, 'r') as f:
            len1 = len(f.read())
    except:
        len1 = 0

    # Read length of current web page version
    # 301 and 302 redirections are resolved automatically
    r = requests.get(args.url)
    if r.status_code is not 200:
        print('Could not fetch %s.' % args.url)
        len2 = 0
    else:
        len2 = len(r.text)

    # Write new version to file
    try:
        with open(args.tmp_file, 'w') as f:
            f.write(r.text)
    except Exception as e:
        print('Could not open file %s: %s' % (args.tmp_file, e))

    diff = abs(len2 - len1)
    if diff > args.tolerance:
        send_mail('Difference is %s characters.\n%s' % (str(diff), args.url), args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True, type=str, help='URL to watch')
    parser.add_argument('-t', '--tolerance', default=0, type=int, help='Number of characters which have to differ from the cached and new version to send a notification')
    parser.add_argument('--smtp', action='store_true', help='If set, SMTP is used.')
    parser.add_argument('--sendmail_path', default='/usr/sbin/sendmail', type=str, help='Path to sendmail binary')
    parser.add_argument('--tmp_file', default='/tmp/watcher_cache.txt', type=str, help='path to temporary file which is used for caching and comparison')
    parser.add_argument('--sender_address', default='noreply@example.com', type=str, help='E-mail address of the sender of the mail')
    parser.add_argument('--recipient_address', required=True, type=str, help='E-mail address of the receiver of the mail')
    parser.add_argument('--subject', default='Something has changed', type=str, help='Subject of the mail')
    parser.add_argument('--smtp_host', default='localhost', type=str, help='Address of the SMTP mail server which is used to send the mail')
    parser.add_argument('--smtp_port', default=25, type=int, help='SMTP port of the mailserver')
    parser.add_argument('--smtp_username', default='', type=str, help='SMTP login username')
    parser.add_argument('--smtp_password', default='', type=str, help='SMTP login password')
    parser.add_argument('--disable_tls', action='store_false', help='If set, TLS is disables')
    main(parser.parse_args())

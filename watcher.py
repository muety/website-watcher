#!/usr/bin/python3
import argparse
import requests
import os
import smtplib
import sys
import tempfile
from lxml import html

def get_nodes(exp, page):
    """ Returns lxml nodes corresponding to the XPath expression """
    tree = html.fromstring(page)
    return tree.xpath(exp)

def filter_document(nodes):
    """ Returns the text content of the specified nodes """
    text = ""
    for element in nodes:
        text = text + element.text_content()
    return text

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
            len1 = len( filter_documemt(get_nodes(args.xpath, f.read().encode("utf-8"))))
    except:
        len1 = 0

    # Read length of current web page version
    # 301 and 302 redirections are resolved automatically
    r = requests.get(args.url)
    if r.status_code is not 200:
        print('Could not fetch %s.' % args.url)
        len2 = 0
    else:
        len2 = len( filter_documemt(get_nodes(args.xpath, r.text.encode("utf-8"))))

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

    tmp_dir = tempfile.gettempdir()
    tmp_location = tmp_dir+"/watcher_cache.txt"

    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', required=True, type=str, help='URL to watch')
    parser.add_argument('-s', '--sender_address', default='noreply@example.com', type=str, help='Sender e-mail address')
    parser.add_argument('-r', '--recipient_address', required=True, type=str, help='Receiver e-mail address')
    parser.add_argument('--subject', default='Something has changed', type=str, help='E-Mail subject')
    parser.add_argument('-t', '--tolerance', default=0, type=int, help='Number of characters which have to differ between cached- and new content to trigger a notification')
    parser.add_argument('--sendmail_path', default='/usr/sbin/sendmail', type=str, help='Path to Sendmail binary')
    parser.add_argument('--smtp', action='store_true', help='If set, SMTP is used instead of local Sendmail.')
    parser.add_argument('--smtp_host', default='localhost', type=str, help='SMTP server host name to send mails with – only required of "--smtp" is set to true')
    parser.add_argument('--smtp_port', default=25, type=int, help='SMTP server port – only required of "--smtp" is set to true')
    parser.add_argument('--smtp_username', default='', type=str, help='SMTP server login username – only required of "--smtp" is set to true')
    parser.add_argument('--smtp_password', default='', type=str, help='SMTP server login password – only required of "--smtp" is set to true')
    parser.add_argument('--disable_tls', action='store_false', help='If set, SMTP connection is unencrypted (TLS disabled) – only required of "--smtp" is set to true')
    parser.add_argument('--tmp_file', default=tmp_location, type=str, help='Path to temporary file to be used for caching and comparison')
    parser.add_argument('-x', '--xpath', default='//body', type=str, help="XPath expression designating the elements to watch")
    main(parser.parse_args())

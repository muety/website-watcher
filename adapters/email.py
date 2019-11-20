import argparse
import logging
import os
import re
import smtplib

from . import SendAdapter

EMAIL_REGEX = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')


class EmailSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, text):
        msg = 'From: %s\n' % self.args.sender_address
        msg += 'To: %s\n' % self.args.recipient_address
        msg += 'Subject: %s\n\n' % self.args.subject
        msg += text

        if not self.args.smtp:
            sendmail_location = self.args.sendmail_path
            p = os.popen('%s -t' % sendmail_location, 'w')
            status = p.close()
            if status is not None:
                logging.error('Sendmail exit status', status)
                return False
            return True
        else:
            try:
                smtp = smtplib.SMTP(self.args.smtp_host, self.args.smtp_port)
                smtp.ehlo()
                if not self.args.disable_tls:
                    smtp.starttls()
                if self.args.smtp_username != '' and self.args.smtp_password != '':
                    smtp.login(self.args.smtp_username, self.args.smtp_password)
                smtp.sendmail(self.args.sender_address, [self.args.recipient_address], msg)
                logging.info('Successfully sent email')
                smtp.quit()
                return True
            except smtplib.SMTPException as e:
                logging.error('Error: unable to send email: ', e)
                return False

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter', description=cls.get_description())
        parser.add_argument('-r', '--recipient_address', required=True, type=cls._valid_email, help='Receiver e-mail address')
        parser.add_argument('-s', '--sender_address', default='noreply@example.com', type=cls._valid_email, help='Sender e-mail address')
        parser.add_argument('--subject', default='Something has changed', type=str, help='E-Mail subject')
        parser.add_argument('--sendmail_path', default='/usr/sbin/sendmail', type=str, help='Path to Sendmail binary')
        parser.add_argument('--smtp', action='store_true', help='If set, SMTP is used instead of local Sendmail.')
        parser.add_argument('--smtp_host', default='localhost', type=str, help='SMTP server host name to send mails with – only required of "--smtp" is set to true')
        parser.add_argument('--smtp_port', default=25, type=int, help='SMTP server port – only required of "--smtp" is set to true')
        parser.add_argument('--smtp_username', default='', type=str, help='SMTP server login username – only required of "--smtp" is set to true')
        parser.add_argument('--smtp_password', default='', type=str, help='SMTP server login password – only required of "--smtp" is set to true')
        parser.add_argument('--disable_tls', action='store_true', help='If set, SMTP connection is unencrypted (TLS disabled) – only required of "--smtp" is set to true')
        return parser

    @classmethod
    def get_name(cls):
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls):
        return 'An adapter to send e-mail notifications using local sendmail or an SMTP server.'

    @staticmethod
    def _valid_email(string):
        match = EMAIL_REGEX.fullmatch(string)
        if not match:
            raise argparse.ArgumentTypeError('not a valid e-mail')
        return match.string


adapter = EmailSendAdapter

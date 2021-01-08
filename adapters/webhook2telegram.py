import argparse
import logging
import os
import re

import requests

from . import SendAdapter

TOKEN_REGEX = re.compile(r'[\d\w]{8}-[\d\w]{4}-[\d\w]{4}-[\d\w]{4}-[\d\w]{12}')

class Webhook2TelegramSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, data):
        url = f'{self.args.webhook_url}/api/messages'
        r = requests.post(url, json={
            'recipient_token': self.args.recipient_token,
            'origin': self.args.sender,
            'text': f'Difference is {data.diff} characters\n{data.url}'
        })
        if not 200 <= r.status_code <= 299:
            logging.error(f'Got response status {r.status_code}')
            return False
        return True

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter', description=cls.get_description())
        parser.add_argument('-r', '--recipient_token', required=True, type=cls._valid_token, help='Recipient token')
        parser.add_argument('-s', '--sender', default='Website Watcher Script', type=str, help='Sender name')
        parser.add_argument('--webhook_url', default='https://apps.muetsch.io/webhook2telegram', type=cls._valid_url, help='URL of Webhook2Telegram bot instance')
        return parser

    @classmethod
    def get_name(cls):
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls):
        return 'An adapter to send push messages via Telegram using Webhook2Telegram (https://github.com/muety/webhook2telegram).'

    @staticmethod
    def _valid_token(string):
        match = TOKEN_REGEX.fullmatch(string)
        if not match:
            raise argparse.ArgumentTypeError('not a valid token')
        return match.string


adapter = Webhook2TelegramSendAdapter

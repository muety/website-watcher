import argparse
import logging
import os
import re

import requests

from . import SendAdapter

MIDDLEMAN_TOKEN_REGEX = re.compile(r'[\d\w]{8}-[\d\w]{4}-[\d\w]{4}-[\d\w]{4}-[\d\w]{12}')
URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class MiddlemanSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, text):
        url = f'{self.args.middleman_url}/api/messages'
        r = requests.post(url, json={'recipient_token': self.args.recipient_token, 'origin': self.args.sender, 'text': text})
        if r.status_code != 200:
            logging.error(r.text)
            return False
        return True

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter', description=cls.get_description())
        parser.add_argument('-r', '--recipient_token', required=True, type=cls._valid_token, help='Recipient token')
        parser.add_argument('-s', '--sender', default='Website Watcher Script', type=str, help='Sender name')
        parser.add_argument('--middleman_url', default='https://apps.muetsch.io/middleman', type=cls._valid_url, help='URL of the Telegram Middleman bot instance')
        return parser

    @classmethod
    def get_name(cls):
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls):
        return 'An adapter to send push messages via Telegram using the Middleman bot (https://github.com/n1try/telegram-middleman-bot).'

    @staticmethod
    def _valid_token(string):
        match = MIDDLEMAN_TOKEN_REGEX.fullmatch(string)
        if not match:
            raise argparse.ArgumentTypeError('not a valid token')
        return match.string

    @staticmethod
    def _valid_url(string):
        match = URL_REGEX.fullmatch(string)
        if not match:
            raise argparse.ArgumentTypeError('not a valid url')
        return match.string


adapter = MiddlemanSendAdapter

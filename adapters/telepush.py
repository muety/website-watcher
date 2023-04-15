import argparse
import logging
import os

import requests

from model import WatchResult
from . import SendAdapter


class TelepushSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, data: WatchResult) -> bool:
        url = f'{self.args.webhook_url}/api/messages/{self.args.recipient_token}'
        r = requests.post(url, json={
            'origin': self.args.sender,
            'text': f'Difference is {data.diff} characters.\nCheck [{data.url}]({data.url})'
        })
        if not 200 <= r.status_code <= 299:
            logging.error(f'Got response status {r.status_code}')
            return False
        return True

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter',
                                         description=cls.get_description())
        parser.add_argument('-r', '--recipient_token', required=True, type=str, help='Recipient token')
        parser.add_argument('-s', '--sender', default='Website Watcher Script', type=str, help='Sender name')
        parser.add_argument('--webhook_url', default='https://telepush.dev', type=cls._valid_url,
                            help='URL of Telepush bot instance')
        return parser

    @classmethod
    def get_name(cls) -> str:
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls) -> str:
        return 'An adapter to send push messages via Telegram using Telepush (https://github.com/muety/telepush).'


adapter = TelepushSendAdapter

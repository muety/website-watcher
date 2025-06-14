import argparse
import json
import logging
import os

import requests

from model import WatchResult
from . import SendAdapter


class NtfySendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, data: WatchResult) -> bool:
        headers = { 'content-type': 'application/json' }
        if self.args.ntfy_token:
            headers['Authorization'] = f'Bearer {self.args.ntfy_token}'

        r = requests.post(
            f'{self.args.ntfy_url}',
            data=json.dumps({
                'topic': self.args.ntfy_topic,
                'message': f'Difference is {data.diff} characters. Check {data.url}.',
                'click': data.url,
            }),
            headers=headers,
        )
        if r.status_code != 200:
            logging.error(r.text)
            return False
        return True

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter',
                                         description=cls.get_description())
        #parser.add_argument('--gotify_key', required=True, type=str, help='Gotify app key / token')
        parser.add_argument('--ntfy_topic', required=True, type=str, help='Ntfy topic to publish to')
        parser.add_argument('--ntfy_url', required=False, default='https://ntfy.sh', type=cls._valid_url, help='Ntfy server instance address')
        parser.add_argument('--ntfy_token', required=False, type=str, help='Ntfy access token (if server required authentication)')
        return parser

    @classmethod
    def get_name(cls) -> str:
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls) -> str:
        return 'An adapter to send push messages via Ntfy.sh (https://ntfy.sh).'


adapter = NtfySendAdapter

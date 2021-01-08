import argparse
import logging
import os

import requests

from . import SendAdapter


class WebSubSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, data):
        # https://indieweb.org/How_to_publish_and_consume_WebSub
        r = requests.post(
            self.args.hub_url,
            data={
                'hub.mode': 'publish',
                'hub.url': data.url
            })
        if not 200 <= r.status_code <= 299:
            logging.error(f'Error, got {r.status_code} response – "{r.text}"')
            return False
        return True

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter',
                                         description=cls.get_description())
        parser.add_argument('--hub_url', required=True, type=cls._valid_url, help='WebSub Hub URL to publish to')
        return parser

    @classmethod
    def get_name(cls):
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls):
        return 'An adapter to send push messages to a WebSub Hub (https://w3c.github.io/websub/#hub).'


adapter = WebSubSendAdapter

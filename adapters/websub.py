import argparse
import logging
import os
import re

import requests

from . import SendAdapter

URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class WebSubSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, text, subject_url):
        # https://indieweb.org/How_to_publish_and_consume_WebSub
        r = requests.post(
            self.args.hub_url,
            data={'hub.mode': 'publish', 'hub.url': subject_url},
            )
        if not 200 <= r.status_code <= 299:
            logging.error(f'Error, got {r.status_code} response – "{r.text}"')
            return False
        return True

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter', description=cls.get_description())
        parser.add_argument('--hub_url', required=True, type=cls._valid_url, help='WebSub Hub URL to publish to')
        return parser

    @classmethod
    def get_name(cls):
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls):
        return 'An adapter to send push messages to a WebSub Hub (https://w3c.github.io/websub/#hub).'

    @staticmethod
    def _valid_url(string):
        match = URL_REGEX.fullmatch(string)
        if not match:
            raise argparse.ArgumentTypeError('not a valid url')
        return match.string


adapter = WebSubSendAdapter

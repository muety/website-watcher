import argparse
import json
import os
from enum import Enum

from model import WatchResult
from . import SendAdapter


class LogFormat(Enum):
    # https://stackoverflow.com/a/46385352/3112139
    PLAIN = 'plain'
    JSON = 'json'

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s: str) -> 'LogFormat':
        try:
            return LogFormat[s.upper()]
        except KeyError:
            raise ValueError()


class StdOutSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, data: WatchResult) -> bool:
        if self.args.log_format is LogFormat.PLAIN:
            print(f'Change of {data.diff} characters detected at {data.url}')
            return True
        if self.args.log_format is LogFormat.JSON:
            print(json.dumps(data.__dict__))
            return True
        return False

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter',
                                         description=cls.get_description())
        parser.add_argument('--log_format', required=False, default='plain', type=LogFormat.from_string,
                            choices=list(LogFormat),
                            help='Format of the logged message, either plain text or JSON.')
        return parser

    @classmethod
    def get_name(cls) -> str:
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls) -> str:
        return 'An adapter simply print changes to stdout. Useful when used in combination with systemd, Docker, etc.'


adapter = StdOutSendAdapter

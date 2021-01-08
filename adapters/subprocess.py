import argparse
import logging
import os
import subprocess

from model import WatchResult
from . import SendAdapter


class SubProcessSendAdapter(SendAdapter):
    def __init__(self, args):
        self.args = self._parse_args(args)

    def send(self, data: WatchResult) -> bool:
        result: subprocess.CompletedProcess = subprocess.run(
            args=self.args.cmd,
            shell=True,
            capture_output=True,
            text=True,
            env={
                'WATCHER_URL': data.url,
                'WATCHER_DIFF': str(data.diff)
            }
        )

        if result.returncode > 0:
            logging.error(f'Failed to execute command with exit code {result.returncode}:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}')
            return False
        return True

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog=f'Website Watcher – "{cls.get_name()}" Adapter',
                                         description=cls.get_description())
        parser.add_argument('--cmd', required=True, type=str,
                            help='The command to execute. Environment variables "$WATCHER_URL", "$WATCHER_DIFF" are set accordingly.')
        return parser

    @classmethod
    def get_name(cls) -> str:
        return os.path.basename(__file__)[:-3]

    @classmethod
    def get_description(cls) -> str:
        return 'An adapter to execute arbitrary commands as sub-processes as a result to a change.'


adapter = SubProcessSendAdapter

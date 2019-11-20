import importlib
import logging
from abc import ABC, abstractmethod

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


class SendAdapterFactory:
    @classmethod
    def get(cls, name, args):
        return cls.get_class(name).adapter(args)

    @classmethod
    def get_class(cls, name):
        try:
            return importlib.import_module(f'.{name}', package='adapters')
        except ModuleNotFoundError:
            logging.error(f'No adapter found with name {name}')
            return None


class SendAdapter(ABC):
    def _parse_args(self, args):
        parser = self.get_parser()

        try:
            return parser.parse_args(args)
        except SystemExit:
            logging.info(f'For addition help try running "python watcher.py help {self.get_name()}"')
            raise AttributeError('missing required arguments')

    @abstractmethod
    def send(self, text):
        pass

    @classmethod
    @abstractmethod
    def get_parser(cls):
        pass

    @classmethod
    @abstractmethod
    def get_name(cls):
        pass

    @classmethod
    @abstractmethod
    def get_description(cls):
        pass

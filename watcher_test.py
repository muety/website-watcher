import os
import uuid
import unittest
from unittest.mock import Mock, patch

import watcher
from adapters import SendAdapter

class NoopAdapter(SendAdapter):
    def __init__(self):
        self.calls = {
            'send': []
        }

    def send(self, data):
        self.calls['send'].append(data)
        return True

    @classmethod
    def get_parser(cls):
        pass

    @classmethod
    def get_name(cls):
        pass

    @classmethod
    def get_description(cls):
        pass

class Args:
    def __init__(self, url=None, adapter='noop', user_agent='firefox', xpath='//body', tolerance=0):
        self.url = url if url is not None else f'https://{uuid.uuid4()}.org'
        self.adapter = adapter
        self.user_agent = user_agent
        self.xpath = xpath
        self.tolerance = tolerance

doc1 = '''
<html>
<body>
    <div id="d1">Some text including umlauts äöü.</div>
    <div id="d2">Not changing</div>
</body>
</html>
'''

doc2 = '''
<html>
<body>
    <div id="d1">Some text including umlauts äöü (changed)</div>
    <div id="d2">Not changing</div>
</body>
</html>
'''

class WatcherTests(unittest.TestCase):
    @patch('watcher.requests.get', autospec=True)
    @patch('adapters.SendAdapterFactory.get', autospec=True)
    def test_ignore_change_in_different_xpath(self, adapter_factory_mock, request_mock):
        noop_adapter = NoopAdapter()

        # Set up mocks
        adapter_factory_mock.return_value = noop_adapter
        request_mock.return_value.status_code = 200
        request_mock.return_value.text = doc1
        
        args = Args(xpath='//div[@id="d2"]')
        
        # First call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)
        self.assertEqual(noop_adapter.calls['send'][0].diff, 12) # 'A'
        self.assertEqual(noop_adapter.calls['send'][0].url, args.url)

        request_mock.return_value.text = doc2

        # Second call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1) # same as before


    @patch('watcher.requests.get', autospec=True)
    @patch('adapters.SendAdapterFactory.get', autospec=True)
    def test_detect_change_in_same_xpath(self, adapter_factory_mock, request_mock):
        noop_adapter = NoopAdapter()

        # Set up mocks
        adapter_factory_mock.return_value = noop_adapter
        request_mock.return_value.status_code = 200
        request_mock.return_value.text = doc1
        
        args = Args(xpath='//div[@id="d1"]')

        # First call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)
        self.assertEqual(noop_adapter.calls['send'][0].diff, 32)
        self.assertEqual(noop_adapter.calls['send'][0].url, args.url)

        request_mock.return_value.text = doc2

        # Second call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 2)
        self.assertEqual(noop_adapter.calls['send'][1].diff, 11) # 9 new chars, minus '.', plus ' '
        self.assertEqual(noop_adapter.calls['send'][1].url, args.url)

    @patch('watcher.requests.get', autospec=True)
    @patch('adapters.SendAdapterFactory.get', autospec=True)
    def test_ignore_changes_below_tolerance(self, adapter_factory_mock, request_mock):
        noop_adapter = NoopAdapter()

        # Set up mocks
        adapter_factory_mock.return_value = noop_adapter
        request_mock.return_value.status_code = 200
        request_mock.return_value.text = doc1
        
        args = Args(xpath='/*', tolerance=12)

        # First call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)
        self.assertEqual(noop_adapter.calls['send'][0].url, args.url)

        request_mock.return_value.text = doc2

        # Second call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)
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
    def __init__(self, url=None, adapter='noop', user_agent='firefox', xpath='//body', tolerance=0, jsonpath=None, ignore='', json=False):
        self.url = url if url is not None else f'https://{uuid.uuid4()}.org'
        self.adapter = adapter
        self.user_agent = user_agent
        self.xpath = xpath
        self.tolerance = tolerance
        self.jsonpath = jsonpath
        self.ignore = ignore
        self.json = json


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

json_doc1 = '''
[
  {
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "original body content"
  },
  {
    "userId": 1,
    "id": 2,
    "title": "qui est esse",
    "body": "this body will not change"
  }
]
'''

json_doc2 = '''
[
  {
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "changed body content"
  },
  {
    "userId": 1,
    "id": 2,
    "title": "qui est esse",
    "body": "this body will not change"
  }
]
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
        self.assertEqual(noop_adapter.calls['send'][0].diff, 12)  # 'A'
        self.assertEqual(noop_adapter.calls['send'][0].url, args.url)

        request_mock.return_value.text = doc2

        # Second call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)  # same as before

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
        self.assertEqual(noop_adapter.calls['send'][1].diff, 11)  # 9 new chars, minus '.', plus ' '
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

    def test_get_json_nodes(self):
        nodes = watcher.get_json_nodes('$[0].body', json_doc1)
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].value, 'original body content')

    @patch('builtins.print')
    def test_get_json_nodes_invalid_json(self, print_mock):
        nodes = watcher.get_json_nodes('$.*', '{ not valid json }')
        self.assertEqual(nodes, [])
        print_mock.assert_called_once()
        self.assertIn('Invalid JSON content', print_mock.call_args[0][0])

    def test_filter_json(self):
        nodes = watcher.get_json_nodes('$[*].body', json_doc1)
        text = watcher.filter_json(nodes)
        self.assertEqual(text, 'original body contentthis body will not change')

    @patch('watcher.requests.get', autospec=True)
    @patch('adapters.SendAdapterFactory.get', autospec=True)
    def test_detect_change_in_jsonpath(self, adapter_factory_mock, request_mock):
        noop_adapter = NoopAdapter()

        # Set up mocks
        adapter_factory_mock.return_value = noop_adapter
        request_mock.return_value.status_code = 200
        request_mock.return_value.text = json_doc1

        args = Args(xpath='//body', jsonpath='$[0].body')

        # First call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)
        self.assertEqual(noop_adapter.calls['send'][0].diff, 21)
        self.assertEqual(noop_adapter.calls['send'][0].url, args.url)

        request_mock.return_value.text = json_doc2

        # Second call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 2)
        self.assertEqual(noop_adapter.calls['send'][1].diff, 13)
        self.assertEqual(noop_adapter.calls['send'][1].url, args.url)

    @patch('watcher.requests.get', autospec=True)
    @patch('adapters.SendAdapterFactory.get', autospec=True)
    def test_ignore_change_in_different_jsonpath(self, adapter_factory_mock, request_mock):
        noop_adapter = NoopAdapter()

        # Set up mocks
        adapter_factory_mock.return_value = noop_adapter
        request_mock.return_value.status_code = 200
        request_mock.return_value.text = json_doc1

        args = Args(xpath='//body', jsonpath='$[1].body')

        # First call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)
        self.assertEqual(noop_adapter.calls['send'][0].diff, 25)
        self.assertEqual(noop_adapter.calls['send'][0].url, args.url)

        request_mock.return_value.text = json_doc2

        # Second call
        watcher.main(args, None)
        self.assertEqual(len(noop_adapter.calls['send']), 1)  # same as before

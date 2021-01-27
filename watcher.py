#!/usr/bin/python3
import argparse
import hashlib
import os
import sys
import tempfile

import requests
from lxml import html

from adapters import SendAdapterFactory
from model import WatchResult


def get_nodes(exp, page):
    """ Returns lxml nodes corresponding to the XPath expression """
    tree = html.fromstring(page)
    return tree.xpath(exp)


def filter_document(nodes) -> str:
    """ Returns the text content of the specified nodes """
    text = ""
    for element in nodes:
        text = text + element.text_content()
    return text


def get_tmp_file(url: str) -> str:
    tmp_dir = tempfile.gettempdir()
    m = hashlib.md5()
    m.update(url.encode('utf-8'))
    return os.path.join(tmp_dir, f'{m.hexdigest()[:6]}_cache.txt')


def main(args, remaining_args):
    tmp_location = get_tmp_file(args.url)

    try:
        adapter = SendAdapterFactory.get(args.adapter, remaining_args)
    except AttributeError:
        sys.exit(1)

    # Read length of old web page version
    try:
        with open(tmp_location, 'r') as f:
            len1 = len(filter_document(get_nodes(args.xpath, f.read().encode("utf-8"))))
    except:
        len1 = 0

    if args.user_agent.lower() == 'firefox':
        args.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0' # Firefox 84 on Windows 10

    # Read length of current web page version
    # 301 and 302 redirections are resolved automatically
    r = requests.get(args.url, headers = { 'user-agent': args.user_agent })
    if 200 <= r.status_code <= 299 :
        len2 = len(filter_document(get_nodes(args.xpath, r.text.encode("utf-8"))))
    else:
        print('Could not fetch %s.' % args.url)
        len2 = 0

    # Write new version to file
    try:
        with open(tmp_location, 'w', encoding='utf-8') as f:
            f.write(r.text)
    except Exception as e:
        print('Could not open file %s: %s' % (tmp_location, e))

    diff = abs(len2 - len1)
    if diff > args.tolerance:
        ok = adapter.send(WatchResult(args.url, diff))
        if not ok:
            sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'help':
        adapter_class = SendAdapterFactory.get_class(sys.argv[2])
        if adapter_class is None:
            sys.exit(1)
        else:
            adapter_class.adapter.get_parser().print_help()
            sys.exit(0)

    parser = argparse.ArgumentParser(prog='Website Watcher')
    parser.add_argument('-u', '--url', required=True, type=str, help='URL to watch')
    parser.add_argument('-t', '--tolerance', default=0, type=int, help='Number of characters which have to differ between cached- and new content to trigger a notification')
    parser.add_argument('-x', '--xpath', default='//body', type=str, help="XPath expression designating the elements to watch")
    parser.add_argument('-ua', '--user-agent', default='muety/website-watcher', type=str, help='User agent header to include in requests (available shortcuts: "firefox")')
    parser.add_argument('--adapter', default='email', type=str, help='Send method to use. See "adapters" for all available')

    args, remaining_args = parser.parse_known_args()

    main(*parser.parse_known_args())

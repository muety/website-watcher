import re
from typing import Union

URL_REGEX = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


def parse_url(string: str) -> Union[str, None]:
    match = URL_REGEX.fullmatch(string)
    if not match:
        return None
    return match.string

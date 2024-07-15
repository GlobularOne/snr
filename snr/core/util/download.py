"""
Download a file from the internet
"""

import urllib.parse

import requests
from requests import RequestException

from snr.core.core import options

__all__ = (
    "download", "RequestException"
)


def download(url: str, path: str, timeout: int | None = None) -> None:
    """Download a file from the internet

    Args:
        url: URL to download
        path: Where to write the download file to 
    """
    parsed_url = urllib.parse.urlparse(url)
    if len(parsed_url.scheme) == 0:
        parsed_url = urllib.parse.urlparse(url, scheme="http")
    if parsed_url.scheme not in ("http", "https"):
        # Reject it
        raise ValueError(
            f"url parameter has invalid scheme '{parsed_url.scheme}'")
    with open(path, "wb") as stream:
        response = requests.get(
            url,
            cookies={"User-Agent": options.default_user_agent},
            timeout=timeout)
        stream.write(response.content)

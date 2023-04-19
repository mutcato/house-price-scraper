import json
import logging
import ssl
from random import shuffle
from typing import Any, Dict, List

import requests
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError, ProtocolError

from adapters import TlsAdapter

logger = logging.getLogger("messagereport")


def fetch_and_save(url: str, session: requests.Session, file_name: str):
    """Fetches the given url with the given session and saves it to the given file_name"""
    try:
        single_response = session.get(url)
    except MaxRetryError as e:
        logger.warning(f"MaxRetryError: {e}")
    except ConnectionError as e:
        logger.warning(f"ConnectionError: {e}")
    except ProtocolError as e:
        logger.warning(f"ProtocolError: {e}")

    if single_response.raise_for_status():
        return

    with open(file_name, "w") as file:
        json.dump(single_response.json(), file, indent=4, ensure_ascii=False)


def generate_session_with_unique_fingerprint(
    headers: Dict[Any, Any], ciphers: List[str]
):
    # default = requests.get("https://tools.scrapfly.io/api/fp/ja3?extended=1").json()
    session = requests.session()
    session.headers.update(headers)
    shuffle(ciphers)
    CIPHERS = ":".join(ciphers)
    adapter = TlsAdapter(
        ciphers=CIPHERS, ssl_options=ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
    )  # prioritize TLS 1.2
    session.mount("https://", adapter)
    return session

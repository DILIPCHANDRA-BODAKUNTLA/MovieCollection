import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


def get_retry_session():
    """
    Create a requests session with retry mechanism.
    """
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        method_whitelist=["GET"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    return session
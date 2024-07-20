import validators
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def validate_url(url):
    if validators.url(url) and len(url) <= 255:
        host = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        return host


def get_url_data(url):
    r = requests.get(url, timeout=1)
    r.raise_for_status()
    status_code = r.status_code
    soup = BeautifulSoup(r.content, "html.parser")
    h1, title, meta_descr = soup.find("h1"), soup.find("title"), soup.find("meta", attrs={"name": "description"})
    h1_cont = h1.text if h1 else ''
    title_cont = title.text if title else ''
    descr_cont = meta_descr.get("content") if meta_descr else ''
    return status_code, h1_cont, title_cont, descr_cont

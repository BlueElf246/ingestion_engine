import requests
from bs4 import BeautifulSoup
from typing import Dict
import time

def get_content(url: str):
    """Fetch the URL and extract title and content.

    Returns a dict with keys 'title' and 'content'. Raises requests.RequestException
    for network-related errors or a generic Exception for parsing errors.
    """
    attempt = 0
    max_retries = 3
    while attempt < max_retries:
        try:
            print(f"Fetching content from {url} (attempt {attempt + 1}/{max_retries})...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            title_tag = soup.find("h1", class_="title-detail")
            content_tag = soup.find("article", class_="fck_detail")

            title = title_tag.get_text(strip=True) if title_tag else ""
            content = content_tag.get_text(separator="\n", strip=True) if content_tag else ""

            return {"title": title, "content": content}
        except requests.RequestException as exc:
            if exc.response is not None and exc.response.status_code == 429:
                attempt += 1
                if attempt < max_retries:
                    time.sleep(10)
                    continue
            raise exc

def get_list_of_links(url: str) -> list[str]:
    """Fetch the URL and extract all hyperlinks.

    Returns a list of URLs found in anchor tags. Raises requests.RequestException
    for network-related errors or a generic Exception for parsing errors.
    """
    response = requests.get(url, timeout=10)

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    # filter and stable-dedupe
    links = [link for link in links if link.endswith(".html")]
    links = list(dict.fromkeys(links))
    return links

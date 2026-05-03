import requests
from bs4 import BeautifulSoup
from typing import Dict


def get_content(url: str) -> Dict[str, str]:
    """Fetch the URL and extract title and content.

    Returns a dict with keys 'title' and 'content'. Raises requests.RequestException
    for network-related errors or a generic Exception for parsing errors.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("h1", class_="title-detail")
    content_tag = soup.find("article", class_="fck_detail")

    title = title_tag.get_text(strip=True) if title_tag else ""
    content = content_tag.get_text(separator="\n", strip=True) if content_tag else ""

    return {"title": title, "content": content}

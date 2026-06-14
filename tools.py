import requests
from bs4 import BeautifulSoup
from config import NEWSAPI_KEY

def fetch_news_articles(params: dict) -> list:
    url = "https://newsapi.org/v2/everything"
    headers = {"X-Api-Key": NEWSAPI_KEY}

    response = requests.get(url, headers=headers, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("articles", [])

def scrape_article_text(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=(5, 15))
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    paragraphs = soup.find_all("p")
    text_chunks = [p.get_text(" ", strip=True) for p in paragraphs]
    text = "\n".join(chunk for chunk in text_chunks if len(chunk) > 40)

    return text[:8000]
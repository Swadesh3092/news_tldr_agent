import json
from langgraph.graph import StateGraph, START, END
from config import client
from schemas import GraphState
from tools import fetch_news_articles, scrape_article_text

import re
from urllib.parse import urlparse


def generate_search_params(state: GraphState) -> dict:
    retry_note = ""
    if state["retry_count"] > 0:
        retry_note = f"""
This is retry attempt {state['retry_count']}.
Previous search did not return enough useful article content.
Try a broader or smarter news search query while staying relevant.
"""

    prompt = f"""
You are helping build NewsAPI search parameters.

User query: {state['user_query']}

{retry_note}

Return only valid JSON with this exact structure:
{{
  "q": "search keywords for news lookup",
  "language": "en",
  "sortBy": "publishedAt",
  "pageSize": 5
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "q": {"type": "string"},
                    "language": {"type": "string"},
                    "sortBy": {"type": "string"},
                    "pageSize": {"type": "integer"}
                },
                "required": ["q", "language", "sortBy", "pageSize"]
            }
        }
    )

    params = json.loads(response.text)
    return {"newsapi_params": params}


def fetch_articles(state: GraphState) -> dict:
    articles = fetch_news_articles(state["newsapi_params"])
    return {"articles_metadata": articles}


def scrape_articles(state: GraphState) -> dict:
    scraped = []

    for article in state.get("articles_metadata", [])[:5]:
        url = article.get("url")
        if not url:
            continue

        try:
            content = scrape_article_text(url)
            scraped.append({
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "url": url,
                "description": article.get("description"),
                "content": content
            })
        except Exception as e:
            scraped.append({
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "url": url,
                "description": article.get("description"),
                "content": "",
                "error": str(e)
            })

    return {"scraped_articles": scraped}


def validate_scraped_articles(state: GraphState) -> dict:
    scraped = state.get("scraped_articles", [])
    useful_articles = [
        article for article in scraped
        if len(article.get("content", "").strip()) > 500
    ]

    return {
        "error": None if useful_articles else "Not enough useful scraped content"
    }


def route_after_validation(state: GraphState) -> str:
    useful_articles = [
        article for article in state.get("scraped_articles", [])
        if len(article.get("content", "").strip()) > 500
    ]

    if len(useful_articles) >= 2:
        return "select_articles"

    if state["retry_count"] < state["max_retries"]:
        return "retry"

    return "format_output"


def increment_retry(state: GraphState) -> dict:
    return {"retry_count": state["retry_count"] + 1}


def select_articles(state: GraphState) -> dict:
    article_candidates = []
    for idx, article in enumerate(state.get("scraped_articles", [])):
        article_candidates.append({
            "id": idx,
            "title": article.get("title", ""),
            "source": article.get("source", ""),
            "description": article.get("description", ""),
            "content_preview": article.get("content", "")[:1500]
        })

    prompt = f"""
User query: {state['user_query']}

Select the 3 most relevant articles for this query.

Return only JSON in this format:
{{
  "selected_ids": [0, 2, 3]
}}

Articles:
{json.dumps(article_candidates, ensure_ascii=False)}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "selected_ids": {
                        "type": "array",
                        "items": {"type": "integer"}
                    }
                },
                "required": ["selected_ids"]
            }
        }
    )

    selected_ids = json.loads(response.text)["selected_ids"]
    selected = [
        state["scraped_articles"][i]
        for i in selected_ids
        if 0 <= i < len(state["scraped_articles"])
    ]

    return {"selected_articles": selected}

def normalize_title(title: str) -> str:
    title = title.lower().strip()
    title = re.sub(r"[^a-z0-9\s]", "", title)
    title = re.sub(r"\s+", " ", title)
    return title

def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.netloc}{parsed.path}".lower().rstrip("/")

def deduplicate_articles(state: GraphState) -> dict:
    seen_titles = set()
    seen_urls = set()
    deduped = []

    for article in state.get("selected_articles", []):
        norm_title = normalize_title(article.get("title", ""))
        norm_url = normalize_url(article.get("url", ""))

        if norm_title in seen_titles or norm_url in seen_urls:
            continue

        seen_titles.add(norm_title)
        seen_urls.add(norm_url)
        deduped.append(article)

    return {"selected_articles": deduped}


def summarize_articles(state: GraphState) -> dict:
    summaries = []

    for article in state.get("selected_articles", []):
        prompt = f"""
Summarize this news article for a TL;DR app.

Requirements:
- Return 4 concise bullet points
- Focus on major facts, developments, and implications
- Avoid fluff
- If the content is weak, still summarize carefully

Article title: {article.get("title", "")}
Source: {article.get("source", "")}
Content:
{article.get("content", "")[:6000]}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        summaries.append({
            "title": article.get("title"),
            "source": article.get("source"),
            "url": article.get("url"),
            "summary": response.text
        })

    return {"summaries": summaries}

def synthesize_overall_takeaway(state: GraphState) -> dict:
    summaries = state.get("summaries", [])

    if not summaries:
        return {"overall_takeaway": "No strong overall takeaway could be generated."}

    summary_text = []
    for item in summaries:
        summary_text.append(
            f"Title: {item['title']}\n"
            f"Source: {item['source']}\n"
            f"Summary:\n{item['summary']}\n"
        )

    prompt = f"""
You are creating a final news TL;DR synthesis.

User query: {state['user_query']}

Based on the article summaries below, write:
1. A 3-bullet overall takeaway
2. A short 'Why it matters' paragraph in simple language

Article summaries:
{chr(10).join(summary_text)}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {"overall_takeaway": response.text}

def format_output(state: GraphState) -> dict:
    summaries = state.get("summaries", [])
    overall_takeaway = state.get("overall_takeaway", "")

    if summaries:
        lines = [f"News TL;DR for: {state['user_query']}\n"]

        for i, item in enumerate(summaries, 1):
            lines.append(f"{i}. {item['title']} ({item['source']})")
            lines.append(item["summary"])
            lines.append(f"Source: {item['url']}\n")

        if overall_takeaway:
            lines.append("Overall Takeaway:")
            lines.append(overall_takeaway)

        return {"final_output": "\n".join(lines)}

    return {
        "final_output": (
            f"Could not generate a strong TL;DR for '{state['user_query']}' "
            f"after {state['retry_count']} retries. Try a more specific topic."
        )
    }


builder = StateGraph(GraphState)

builder.add_node("deduplicate_articles", deduplicate_articles)
builder.add_node("synthesize_overall_takeaway", synthesize_overall_takeaway)
builder.add_node("generate_search_params", generate_search_params)
builder.add_node("fetch_articles", fetch_articles)
builder.add_node("scrape_articles", scrape_articles)
builder.add_node("validate_scraped_articles", validate_scraped_articles)
builder.add_node("increment_retry", increment_retry)
builder.add_node("select_articles", select_articles)
builder.add_node("summarize_articles", summarize_articles)
builder.add_node("format_output", format_output)

builder.add_edge(START, "generate_search_params")
builder.add_edge("generate_search_params", "fetch_articles")
builder.add_edge("fetch_articles", "scrape_articles")
builder.add_edge("scrape_articles", "validate_scraped_articles")


builder.add_conditional_edges(
    "validate_scraped_articles",
    route_after_validation,
    {
        "select_articles": "select_articles",
        "retry": "increment_retry",
        "format_output": "format_output"
    }
)

builder.add_edge("increment_retry", "generate_search_params")
builder.add_edge("select_articles", "deduplicate_articles")
builder.add_edge("deduplicate_articles", "summarize_articles")
builder.add_edge("summarize_articles", "synthesize_overall_takeaway")
builder.add_edge("synthesize_overall_takeaway", "format_output")
builder.add_edge("format_output", END)

graph = builder.compile()
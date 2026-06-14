from typing import TypedDict, Dict, Any, Optional, List

class GraphState(TypedDict):
    user_query: str
    newsapi_params: Dict[str, Any]
    articles_metadata: List[Dict[str, Any]]
    scraped_articles: List[Dict[str, Any]]
    selected_articles: List[Dict[str, Any]]
    summaries: List[Dict[str, Any]]
    overall_takeaway: str
    final_output: str
    retry_count: int
    max_retries: int
    error: Optional[str]
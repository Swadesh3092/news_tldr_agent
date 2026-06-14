from agents import graph

if __name__ == "__main__":
    user_query = input("Enter your news topic: ")

    result = graph.invoke({
        "user_query": user_query,
        "newsapi_params": {},
        "articles_metadata": [],
        "scraped_articles": [],
        "selected_articles": [],
        "summaries": [],
        "overall_takeaway": "",
        "final_output": "",
        "retry_count": 0,
        "max_retries": 2,
        "error": None
    })

    print("\n--- RESULT ---")
    print(result["final_output"])
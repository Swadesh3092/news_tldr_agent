import streamlit as st
from agents import graph

st.set_page_config(page_title="News TL;DR Agent", page_icon="📰", layout="wide")

st.title("📰 News TL;DR Agent")
st.write("Enter a topic and get concise news summaries from recent articles.")

user_query = st.text_input("News topic", placeholder="e.g. latest AI startup funding news")

if st.button("Generate TL;DR"):
    if not user_query.strip():
        st.warning("Please enter a topic.")
    else:
        with st.spinner("Fetching, scraping, and summarizing news..."):
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

        st.subheader("Result")
        st.text(result["final_output"])
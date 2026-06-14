\# News TL;DR Agent



An AI-powered News TL;DR Agent built with LangGraph, Gemini, NewsAPI, and Streamlit.



This project takes a user’s news topic, retrieves relevant articles, scrapes article content, validates content quality, retries when content is weak, removes duplicate stories, summarizes selected articles, and generates a final overall takeaway.



\## Features



\- Converts natural language topics into structured NewsAPI search parameters

\- Fetches recent news articles from NewsAPI

\- Scrapes full article text for better summarization

\- Validates scraped article quality before continuing

\- Retries automatically when content is weak

\- Selects the most relevant articles

\- Deduplicates repeated or overlapping stories

\- Generates concise article-level TL;DR summaries

\- Produces an overall takeaway across multiple articles

\- Includes a Streamlit UI for interaction



\## Tech Stack



\- Python

\- LangGraph

\- Google Gemini

\- NewsAPI

\- BeautifulSoup

\- Requests

\- Streamlit



\## Workflow



1\. User enters a news topic

2\. The agent generates search parameters

3\. News articles are fetched from NewsAPI

4\. Article pages are scraped

5\. Scraped content is validated

6\. The agent retries if content quality is weak

7\. The most relevant articles are selected

8\. Duplicate stories are removed

9\. Articles are summarized

10\. A final overall takeaway is generated

11\. Output is displayed in the Streamlit app



\## Project Structure



```bash

.

├── app.py

├── agents.py

├── config.py

├── schemas.py

├── tools.py

├── main.py

├── requirements.txt

├── README.md

└── .gitignore

```



\## Setup



\### 1. Clone the repository



```bash

git clone https://github.com/YOUR\_USERNAME/YOUR\_REPO\_NAME.git

cd YOUR\_REPO\_NAME

```



\### 2. Create a virtual environment



```bash

python -m venv .venv

```



\### 3. Activate the virtual environment



On Windows:



```bash

.venv\\Scripts\\activate

```



On macOS/Linux:



```bash

source .venv/bin/activate

```



\### 4. Install dependencies



```bash

pip install -r requirements.txt

```



\### 5. Add environment variables



Create a `.env` file in the root folder:



```env

GEMINI\_API\_KEY=your\_gemini\_api\_key

NEWS\_API\_KEY=your\_newsapi\_key

```



\## Run the Project



\### Run in terminal



```bash

python main.py

```



\### Run Streamlit app



```bash

streamlit run app.py

```



\## Example Queries



\- latest AI startup funding news

\- OpenAI and Microsoft AI updates

\- India semiconductor policy news

\- latest robotics regulation updates



\## Key Learnings



This project helped me learn:



\- agent orchestration using LangGraph

\- structured output with Gemini

\- retrieval + scraping pipeline design

\- validation and retry logic

\- deduplication strategies

\- summarization vs synthesis

\- building a simple user-facing AI product with Streamlit



\## Future Improvements



\- Multi-language support

\- Better ranking of sources

\- Bias and sentiment analysis

\- Caching for faster results

\- Deployment to cloud

\- Better UI formatting for article cards and source links



\## License



This project is for learning, experimentation, and portfolio use.


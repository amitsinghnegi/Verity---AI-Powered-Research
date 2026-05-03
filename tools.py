import os
from dotenv import load_dotenv
load_dotenv()

if os.environ.get("GEMINI_API_KEY") is not None:
    print("GEMINI_API_KEY is set")
if os.environ.get('TAVILY_API_KEY') is not None:
    print("TAVILY_API_KEY is set")


from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """Search web for recent and reliable information. Return title, link and snippet."""
    from langchain_tavily import TavilySearch

    tavilySearch = TavilySearch(
        max_results=5,
        topic="general"
    )                               
    
    response = tavilySearch.invoke(query)

    out = []
    for result in  response['results']:
        out.append(f"Title: {result['title']} \nURL: {result['url']} \nResult: {result['content']}")

    return '\n--------\n'.join(out)


import requests
from bs4 import BeautifulSoup

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:1000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
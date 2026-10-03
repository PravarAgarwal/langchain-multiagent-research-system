import re 
import os
import requests
from langchain.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv('TAVILY_API_KEY'))

@tool()
def web_search(query: str) -> str:
    """
    search the web for recent and reliable information based on the input query
    """
    results = tavily_client.search(query=query, max_results=5)
    out = []
    for r in results["results"]:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:300]}"
        )
    return "\n----\n".join(out)


@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    html = None

    # --- Step 1: Initial Page Fetch Attempt ---
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        html = response.text

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else 0
        
        # 🛡️ If blocked by anti-bot firewall (403), use Tavily Extract as an alternative fetcher
        if status_code == 403:
            try:
                extract_response = tavily_client.extract(urls=[url])
                if extract_response and extract_response.get("results"):
                    # Extract the raw HTML markup string retrieved by Tavily's infrastructure proxies
                    html = extract_response["results"][0].get("raw_content", "")
            except Exception as tavily_err:
                return f"Direct scraping returned 403, and Tavily proxy extraction backup failed: {str(tavily_err)}"
        
        # If it wasn't a 403 error, or if Tavily didn't return any HTML payload contents, fail cleanly
        if not html:
            return f"HTTP error occurred: {str(e)}"

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

    # ------------------------------------------------------------------
    # Your EXACT original processing/strategy flow continues unchanged below
    # ------------------------------------------------------------------
    
    # ──────────────────────────────────────────────────
    # Strategy 1 → trafilatura (BEST for articles/blogs)
    # ──────────────────────────────────────────────────
    extracted = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False
    )

    if extracted and len(extracted.strip()) > 200:
        cleaned = re.sub(r'\s+', ' ', extracted)
        return cleaned[:5000]

    # ──────────────────────────────────────────────────
    # Strategy 2 → readability
    # ──────────────────────────────────────────────────
    doc = Document(html)
    clean_html = doc.summary()

    soup = BeautifulSoup(clean_html, "html.parser")

    for tag in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form"
    ]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    if text and len(text.strip()) > 200:
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned[:5000]

    # ──────────────────────────────────────────────────
    # Strategy 3 → fallback full page extraction
    # ──────────────────────────────────────────────────
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup([
        "script",
        "style",
        "nav",
        "footer",
        "header",
        "aside",
        "form"
    ]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    cleaned = re.sub(r'\s+', ' ', text)

    if cleaned:
        return cleaned[:5000]

    return "Could not extract meaningful content from the page."


def main():
    # Testing the NewsNation URL that triggered your 403 Forbidden Error
    url = "https://www.newsnationnow.com/world/us-iran-iraq-inherent-resolve-strait-of-hormuz"
    scraped_data = scrape_url.invoke(url)
    print(scraped_data)

if __name__ == "__main__":
    main()

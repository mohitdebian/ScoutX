import asyncio
import aiohttp
import logging
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)

# Basic headers to avoid immediate blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

class CrawlerException(Exception):
    pass

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
    reraise=True
)
async def fetch_page(url: str, session: aiohttp.ClientSession) -> str:
    """Fetch the HTML content of a URL."""
    try:
        async with session.get(url, headers=HEADERS, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 429:
                logger.warning(f"Rate limited (429) on {url}")
                raise CrawlerException("Rate limited")
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        raise

async def crawl_job(url: str, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
    """
    Crawls a job page and attempts to extract structured information.
    Since pages vary wildly, this is a best-effort generic extraction.
    """
    try:
        html = await fetch_page(url, session)
        soup = BeautifulSoup(html, 'lxml')

        # Generic extractions
        title = _extract_title(soup)
        company = _extract_company(soup, url)
        description = _extract_description(soup)

        if not title or not description:
            return None

        return {
            "title": title,
            "company": company,
            "description": description,
            "url": url,
            "html": html # Raw HTML might be useful for LLM processing if needed
        }
    except Exception as e:
        logger.error(f"Failed to crawl job {url}: {e}")
        return None

def _extract_title(soup: BeautifulSoup) -> str:
    """Attempt to extract job title."""
    h1 = soup.find('h1')
    if h1:
        return h1.get_text(strip=True)
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text(strip=True).split('|')[0].strip()
    return ""

def _extract_company(soup: BeautifulSoup, url: str) -> str:
    """Attempt to extract company name."""
    # Often in the title: "Software Engineer at Acme Corp"
    title_tag = soup.find('title')
    if title_tag:
        parts = title_tag.get_text(strip=True).split(' at ')
        if len(parts) > 1:
            return parts[1].split('|')[0].strip()

    # Domain fallback
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    return domain.replace("www.", "").split('.')[0].capitalize()

def _extract_description(soup: BeautifulSoup) -> str:
    """Attempt to extract job description."""
    # Common container IDs/classes
    containers = soup.find_all(['div', 'section'], class_=lambda c: c and any(x in c.lower() for x in ['description', 'details', 'job-content']))

    if containers:
        # Pick the largest one
        largest = max(containers, key=lambda x: len(x.get_text()))
        return largest.get_text(separator='\n', strip=True)

    # Fallback: just return body text
    body = soup.find('body')
    if body:
        return body.get_text(separator='\n', strip=True)
    return ""

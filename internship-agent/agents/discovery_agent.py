import asyncio
import logging
from typing import List, Set
from bs4 import BeautifulSoup
import aiohttp
from database.db import execute, execute_many, fetch_all

logger = logging.getLogger(__name__)

INITIAL_SEED_URLS = [
    "https://remoteok.com",
    "https://remote.co/remote-jobs/",
    "https://weworkremotely.com",
    "https://wellfound.com/jobs",
    "https://www.linkedin.com/jobs/search/?keywords=software%20engineer%20intern&f_WT=2",
    "https://www.simplyhired.com/search?q=software+engineer+intern+remote",
    "https://jobspresso.co",
    "https://datajobs.com",
    "https://outsourcely.com",
    "https://www.toptal.com",
    "https://www.skipthedrive.com",
    "https://nodesk.co",
    "https://remotehabits.com",
    "https://remotive.com",
    "https://remote4me.com",
    "https://pangian.com",
    "https://remotees.com",
    "https://europeremotely.com",
    "https://remoteokeurope.com",
    "https://remoteasia.com",
    "https://www.flexjobs.com",
    "https://www.workingnomads.com/jobs",
    "https://www.virtualvocations.com",
    "https://remotefreelance.com",
    "https://www.remoterocketship.com",
    "https://www.freelancer.com",
    # Specific companies
    "https://careers.google.com/jobs/results/",
    "https://jobs.careers.microsoft.com/global/en/search",
    "https://www.amazon.jobs/en/",
    "https://www.metacareers.com/jobs",
    "https://jobs.apple.com/",
    "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite",
    "https://stripe.com/jobs/search",
    "https://careers.cloudflare.com/jobs",
    "https://careers.datadoghq.com/",
    "https://www.mongodb.com/careers/jobs",
    "https://vercel.com/careers",
    "https://supabase.com/careers",
    "https://turso.tech/careers",
    "https://neon.tech/careers",
    "https://www.figma.com/careers/",
    "https://discord.com/careers",
    "https://github.com/about/careers",
    "https://about.gitlab.com/jobs/",
    "https://www.jetbrains.com/careers/",
    "https://canonical.com/careers/all",
    "https://www.hashicorp.com/jobs",
    "https://linear.app/careers",
    "https://openai.com/careers",
    "https://www.anthropic.com/careers",
    "https://huggingface.co/careers",
    "https://posthog.com/careers"
]

async def seed_initial_urls():
    """Ensure seed URLs are in the crawl queue."""
    parameters = [(url, "seed", 10) for url in INITIAL_SEED_URLS]
    await execute_many(
        "INSERT OR IGNORE INTO crawl_queue (url, source, priority) VALUES (?, ?, ?)",
        parameters
    )

async def discover_urls():
    """
    Simulated continuous discovery.
    In a full production version, this would search the web for new career pages.
    For this implementation, we will periodically re-queue seed URLs if the queue is empty
    and extract links from crawled pages (handled primarily in crawler).
    """
    await seed_initial_urls()
    logger.info("Discovery agent ran.")

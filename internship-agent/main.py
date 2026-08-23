import asyncio
import logging
import aiohttp
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any

from database.db import init_db, close_db_pool, execute, fetch_one
from providers.tokenrouter import KimiProvider
from agents.discovery_agent import discover_urls
from agents.crawler_agent import crawl_job
from agents.role_filter_agent import filter_role
from agents.remote_filter_agent import filter_remote
from agents.resume_match_agent import evaluate_match
from agents.storage_agent import save_job, sync_to_markdown
from agents.notification_agent import send_alert

# Setup rich logging
from rich.logging import RichHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("internship_agent")

class AgentState(TypedDict):
    current_url: str
    job_details: Dict[str, Any]
    match_results: Dict[str, Any]
    session: aiohttp.ClientSession
    provider: KimiProvider

async def get_next_url() -> str:
    row = await fetch_one("SELECT url FROM crawl_queue ORDER BY priority DESC LIMIT 1")
    if row:
        url = row['url']
        await execute("DELETE FROM crawl_queue WHERE url = ?", (url,))
        await execute("INSERT OR REPLACE INTO visited_urls (url) VALUES (?)", (url,))
        return url
    return ""

async def discovery_node(state: AgentState) -> Dict[str, Any]:
    url = await get_next_url()
    if not url:
        await discover_urls()
        url = await get_next_url()
    return {"current_url": url}

async def crawler_node(state: AgentState) -> Dict[str, Any]:
    url = state.get("current_url")
    if not url:
        return {"job_details": None}

    logger.info(f"Crawling: {url}")
    job_details = await crawl_job(url, state["session"])
    return {"job_details": job_details}

async def filter_node(state: AgentState) -> Dict[str, Any]:
    job = state.get("job_details")
    if not job:
        return {"job_details": None}

    title = job.get("title", "")
    description = job.get("description", "")

    # We lack strict location in this simple crawler, so we pass empty string and rely on description
    if not filter_role(title, description):
        logger.info(f"Filtered out by role: {title}")
        return {"job_details": None}

    if not filter_remote(title, "", description):
        logger.info(f"Filtered out by remote requirement: {title}")
        return {"job_details": None}

    return {"job_details": job}

async def evaluate_node(state: AgentState) -> Dict[str, Any]:
    job = state.get("job_details")
    if not job:
        return {"match_results": None}

    logger.info(f"Evaluating match for: {job.get('title')} at {job.get('company')}")
    results = await evaluate_match(job, state["provider"])
    return {"match_results": results}

async def storage_node(state: AgentState) -> Dict[str, Any]:
    job = state.get("job_details")
    results = state.get("match_results")

    if job and results:
        await save_job(job, results)
        await sync_to_markdown()
        await send_alert(job, results)

    return {}

def should_continue(state: AgentState) -> str:
    if not state.get("current_url"):
        return "sleep"
    if not state.get("job_details"):
        return "discovery"
    return "evaluate"

def should_store(state: AgentState) -> str:
    if state.get("match_results"):
        return "storage"
    return "discovery"

def build_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("discovery", discovery_node)
    workflow.add_node("crawler", crawler_node)
    workflow.add_node("filter", filter_node)
    workflow.add_node("evaluate", evaluate_node)
    workflow.add_node("storage", storage_node)

    # Simple sleep node for empty queues
    async def sleep_node(state: AgentState):
        await asyncio.sleep(2)
        return {}
    workflow.add_node("sleep", sleep_node)

    workflow.set_entry_point("discovery")

    workflow.add_edge("discovery", "crawler")
    workflow.add_edge("crawler", "filter")

    workflow.add_conditional_edges("filter", should_continue, {
        "evaluate": "evaluate",
        "discovery": "discovery",
        "sleep": "sleep"
    })

    workflow.add_conditional_edges("evaluate", should_store, {
        "storage": "storage",
        "discovery": "discovery"
    })

    workflow.add_edge("storage", "discovery")
    workflow.add_edge("sleep", "discovery")

    return workflow.compile()

async def main():
    await init_db()

    try:
        # Insert mock resume for testing purposes if not exists
        await execute("INSERT OR IGNORE INTO resume (id, skills, experience) VALUES (1, 'Python, Asyncio, SQL, APIs', '1 year backend development')")

        graph = build_graph()
        provider = KimiProvider()

        logger.info("Starting Autonomous Internship Agent...")

        async with aiohttp.ClientSession() as session:
            state = AgentState(
                current_url="",
                job_details={},
                match_results={},
                session=session,
                provider=provider
            )

            # We run the compiled graph continuously.
            # Using a generator approach for continuous execution.
            try:
                 async for output in graph.astream(state):
                     pass # The loop runs forever, driven by graph structure
            except asyncio.CancelledError:
                 logger.info("Agent shut down gracefully.")
            except Exception as e:
                 logger.error(f"Critical error in main loop: {e}")
    finally:
        await close_db_pool()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")

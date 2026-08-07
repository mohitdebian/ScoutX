import aiofiles
import logging
from typing import Dict, Any, List
from database.db import fetch_all, execute
from datetime import datetime

logger = logging.getLogger(__name__)

MARKDOWN_PATH = "internships/internships.md"

async def save_job(job_details: Dict[str, Any], match_results: Dict[str, Any]):
    """Save or update job in SQLite."""
    company_name = job_details.get("company", "Unknown")

    # Handle company insertion
    try:
        company_id = await execute(
            "INSERT OR IGNORE INTO companies (name) VALUES (?)",
            (company_name,)
        )
        if not company_id:
            row = await fetch_all("SELECT id FROM companies WHERE name = ?", (company_name,))
            if row:
                company_id = row[0]['id']
    except Exception as e:
        logger.error(f"Error handling company insertion: {e}")
        return

    # Handle job insertion/update
    try:
        # Check if exists
        existing = await fetch_all("SELECT id, status FROM jobs WHERE apply_url = ?", (job_details["url"],))

        if existing:
            # We don't overwrite if manual changes were made to status
            status = existing[0]['status']
            if status == 'Found' or status == 'Expired':
                await execute(
                    """
                    UPDATE jobs SET
                        title = ?, company_id = ?, description = ?, match_score = ?,
                        matched_skills = ?, missing_skills = ?, summary = ?, status = 'Found'
                    WHERE apply_url = ?
                    """,
                    (
                        job_details.get("title"), company_id, job_details.get("description"),
                        match_results.get("match_score"),
                        ", ".join(match_results.get("matched_skills", [])),
                        ", ".join(match_results.get("missing_skills", [])),
                        match_results.get("summary"),
                        job_details["url"]
                    )
                )
        else:
             await execute(
                """
                INSERT INTO jobs (
                    company_id, title, apply_url, description,
                    match_score, matched_skills, missing_skills, summary, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Found')
                """,
                (
                    company_id, job_details.get("title"), job_details["url"],
                    job_details.get("description"), match_results.get("match_score"),
                    ", ".join(match_results.get("matched_skills", [])),
                    ", ".join(match_results.get("missing_skills", [])),
                    match_results.get("summary")
                )
            )
    except Exception as e:
        logger.error(f"Error saving job: {e}")

async def sync_to_markdown():
    """Reads all active jobs from DB and writes to a single markdown file."""
    query = """
        SELECT j.*, c.name as company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        ORDER BY j.match_score DESC, j.date_found DESC
    """

    try:
        jobs = await fetch_all(query)

        content = "# 🚀 Autonomous AI Internship Discovery\n\n"
        content += f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

        for job in jobs:
            status_emoji = {
                "Found": "🟢", "Applied": "📬", "Interviewing": "🗣️",
                "Rejected": "❌", "Accepted": "🎉", "Expired": "💀"
            }.get(job['status'], "❓")

            content += f"## {job['title']} @ {job['company_name']}\n\n"
            content += f"- **Status:** {status_emoji} {job['status']}\n"
            content += f"- **Match Score:** {job['match_score']}%\n"
            content += f"- **Apply Link:** [{job['apply_url']}]({job['apply_url']})\n"
            content += f"- **Date Found:** {job['date_found']}\n\n"

            content += "### AI Summary\n"
            content += f"{job['summary']}\n\n"

            content += "### Skills Breakdown\n"
            content += f"- **Matched:** {job['matched_skills']}\n"
            content += f"- **Missing:** {job['missing_skills']}\n\n"
            content += "---\n\n"

        async with aiofiles.open(MARKDOWN_PATH, mode='w', encoding='utf-8') as f:
            await f.write(content)

        logger.info(f"Successfully synced {len(jobs)} jobs to {MARKDOWN_PATH}")
    except Exception as e:
        logger.error(f"Failed to sync markdown: {e}")

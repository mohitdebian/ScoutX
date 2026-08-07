import logging
import httpx
from typing import Dict, Any
from config.settings import settings

logger = logging.getLogger(__name__)

async def send_alert(job_details: Dict[str, Any], match_results: Dict[str, Any]):
    """Send Telegram notification if score >= 90."""
    score = match_results.get("match_score", 0)
    if score < 90:
        return

    token = settings.telegram_bot_token
    chat_id = settings.telegram_chat_id

    if not token or not chat_id:
        logger.warning("Telegram configuration missing. Cannot send alert.")
        return

    title = job_details.get('title', 'Unknown Role')
    company = job_details.get('company', 'Unknown Company')
    url = job_details.get('url', '')

    message = (
        f"🌟 **High Match Internship Found!** ({score}%)\n\n"
        f"**Role:** {title}\n"
        f"**Company:** {company}\n"
        f"**Link:** {url}\n\n"
        f"**Summary:** {match_results.get('summary', '')}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
             resp = await client.post(url, json=payload)
             resp.raise_for_status()
             logger.info(f"Telegram alert sent for {title} at {company}")
    except Exception as e:
         logger.error(f"Failed to send Telegram alert: {e}")

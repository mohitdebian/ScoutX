import logging
import json
from typing import Dict, Any, Optional
from database.db import fetch_one
from providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)

MATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "match_score": {"type": "integer"},
        "matched_skills": {"type": "array", "items": {"type": "string"}},
        "missing_skills": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "string"},
        "reason": {"type": "string"}
    },
    "required": ["match_score", "matched_skills", "missing_skills", "summary", "reason"]
}

async def load_resume() -> Optional[Dict[str, str]]:
    """Loads resume data from the database. Assumes it's inserted once (id=1)."""
    row = await fetch_one("SELECT skills, projects, technologies, experience FROM resume WHERE id = 1")
    if row:
        return dict(row)
    return None

async def evaluate_match(job_details: Dict[str, Any], provider: BaseProvider) -> Optional[Dict[str, Any]]:
    """
    Constructs prompt, calls LLM, and parses JSON to evaluate resume match.
    Returns None if score is below 75 or parsing fails.
    """
    resume_data = await load_resume()
    if not resume_data:
         logger.warning("No resume data found in DB. Skipping match.")
         return None

    prompt = f"""
    Evaluate the match between the following candidate resume and the job description.

    Job Title: {job_details.get('title')}
    Job Company: {job_details.get('company')}
    Job Description: {job_details.get('description', '')[:2000]}...

    Candidate Skills: {resume_data.get('skills')}
    Candidate Technologies: {resume_data.get('technologies')}
    Candidate Experience: {resume_data.get('experience')}
    Candidate Projects: {resume_data.get('projects')}

    Provide a match score out of 100 based strictly on how well the candidate's skills and experience align with the job requirements.
    """

    try:
        result = await provider.generate(prompt, schema=MATCH_SCHEMA)

        if "error" in result:
             logger.error(f"Provider error during match evaluation: {result['error']}")
             return None

        score = result.get("match_score", 0)

        if score >= 75:
            return result
        else:
            logger.info(f"Match score {score} is below threshold 75 for {job_details.get('title')} at {job_details.get('company')}.")
            return None

    except Exception as e:
        logger.error(f"Failed to evaluate match: {e}")
        return None

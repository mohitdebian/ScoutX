import re

REMOTE_KEYWORDS = [
    "remote", "fully remote", "remote first", "distributed",
    "work from home", "anywhere", "remote us", "remote worldwide",
    "remote india", "remote europe", "remote apac"
]

REJECT_KEYWORDS = [
    "hybrid", "onsite", "on-site", "office", "relocation"
]

def filter_remote(title: str, location: str, description: str) -> bool:
    """
    Checks if the job is strictly remote.
    Returns True if it's a remote job, False otherwise.
    """
    combined_text = f"{title} {location} {description}".lower()

    # If any reject keyword is present (and not negated, though negation is hard,
    # we'll be strict and reject if hybrid/onsite is mentioned as primary location)
    # To be safe, let's look for strong remote signals first.

    has_remote_signal = any(kw in combined_text for kw in REMOTE_KEYWORDS)

    if not has_remote_signal:
        return False

    # Check for hybrid/onsite in location or title specifically
    loc_title_text = f"{title} {location}".lower()
    if any(kw in loc_title_text for kw in REJECT_KEYWORDS):
        return False

    return True

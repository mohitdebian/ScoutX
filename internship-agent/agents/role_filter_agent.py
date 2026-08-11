import re

ALLOWED_ROLES = [
    "software engineer intern",
    "software development engineer",
    "sde intern",
    "backend engineer intern",
    "backend developer intern",
    "platform engineer intern",
    "infrastructure engineer intern",
    "full stack engineer intern",
    "ai engineer intern",
    "ai application engineer intern",
    "developer tools engineer intern"
]

# Hoist list and string allocations to avoid recreating/computing on every function call
INTERN_KEYWORDS = ["intern", "internship", "co-op", "student"]
ROLE_PARTS_CACHE = [(role, role.replace(" intern", "").split()) for role in ALLOWED_ROLES]
BACKEND_KEYWORDS = ["backend", "back-end", "database", "api", "infrastructure", "sql", "postgresql", "python", "go", "java"]
FRONTEND_KEYWORDS = ["frontend", "front-end", "css", "html", "react", "vue", "ui", "ux"]


def filter_role(title: str, description: str = "") -> bool:
    """
    Checks if the job title matches the allowed roles.
    Special handling for 'Full Stack': must verify description indicates backend-heavy.
    """
    title_lower = title.lower()

    # Fast reject if no "intern" or similar in title to avoid processing senior roles
    if not any(word in title_lower for word in INTERN_KEYWORDS):
        return False

    is_allowed = False
    is_full_stack = False

    for role, role_parts in ROLE_PARTS_CACHE:
        # Simple string inclusion for now. In production, might want better tokenization
        if all(part in title_lower for part in role_parts):
            is_allowed = True
            if "full stack" in role:
                is_full_stack = True
            break

    if not is_allowed:
        return False

    if is_full_stack:
        return _is_backend_heavy(description)

    return True

def _is_backend_heavy(description: str) -> bool:
    """Analyze description to ensure full stack is backend heavy."""
    desc_lower = description.lower()

    backend_count = sum(1 for kw in BACKEND_KEYWORDS if kw in desc_lower)
    frontend_count = sum(1 for kw in FRONTEND_KEYWORDS if kw in desc_lower)

    return backend_count >= frontend_count

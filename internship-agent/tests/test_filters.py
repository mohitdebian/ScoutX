from agents.role_filter_agent import filter_role, _is_backend_heavy
from agents.remote_filter_agent import filter_remote

def test_role_filter_accepts_backend():
    assert filter_role("Backend Engineer Intern") == True
    assert filter_role("Software Engineer Intern") == True
    assert filter_role("SDE Intern") == True

def test_role_filter_rejects_senior():
    assert filter_role("Senior Backend Engineer") == False
    assert filter_role("Frontend Developer Intern") == False

def test_role_filter_full_stack():
    # Should accept backend heavy
    assert filter_role("Full Stack Engineer Intern", "Working mostly with Python, APIs, and PostgreSQL") == True
    # Should reject frontend heavy
    assert filter_role("Full Stack Engineer Intern", "Working mostly with React, CSS, and UI components") == False

def test_remote_filter_accepts_remote():
    assert filter_remote("Backend Intern", "Remote US", "Work from anywhere") == True
    assert filter_remote("Remote Software Engineer Intern", "", "") == True

def test_remote_filter_rejects_hybrid():
    assert filter_remote("Backend Intern", "Hybrid", "Remote 2 days a week") == False
    assert filter_remote("Software Intern", "San Francisco, CA (Onsite)", "Great office") == False

import pytest
from bs4 import BeautifulSoup
from agents.crawler_agent import _extract_title, _extract_company, _extract_description

def test_crawler_extracts_title():
    html = "<html><head><title>Software Engineer Intern | Google</title></head><body><h1>Software Engineer Intern</h1></body></html>"
    soup = BeautifulSoup(html, 'lxml')
    assert _extract_title(soup) == "Software Engineer Intern"

def test_crawler_extracts_company():
    html = "<html><head><title>Backend Intern at Stripe</title></head><body></body></html>"
    soup = BeautifulSoup(html, 'lxml')
    assert _extract_company(soup, "https://stripe.com/jobs") == "Stripe"

def test_crawler_extracts_description():
    html = "<html><body><div class='job-description'>This is a great job. Python is required.</div></body></html>"
    soup = BeautifulSoup(html, 'lxml')
    assert "This is a great job" in _extract_description(soup)

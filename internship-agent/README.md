# AI Internship Discovery Agent

An autonomous AI agent that continuously discovers remote internships matching specific criteria, filtering and parsing data using LangGraph and the Kimi K3 provider.

## Setup

1. Configure `.env`:
   \`\`\`bash
   cp .env.example .env
   # Add your Kimi API key and Telegram bot token
   \`\`\`
2. Run the agent:
   \`\`\`bash
   python main.py
   \`\`\`

## Architecture

- **Discovery Agent**: Feeds the crawl queue with initial job boards.
- **Crawler Agent**: Feeds and parses basic job data asynchronously.
- **Filtering Agents**: Strictly filters for Software Engineer / Backend roles that are Remote.
- **Resume Match Agent**: Uses LLM to score the job against a resume (>75% threshold).
- **Storage/Notification Agents**: Saves valid matches to SQLite, syncs to `internships/internships.md`, and alerts via Telegram (>=90%).

## Built With
- LangGraph
- aiohttp & BeautifulSoup4
- aiosqlite
- Pydantic

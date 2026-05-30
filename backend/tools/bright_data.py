"""Bright Data integration: Web Scraper API, SERP API, Web Unlocker, Scraping Browser, MCP."""
from __future__ import annotations
import httpx
import json
from typing import Any, Optional
from playwright.async_api import async_playwright
from backend.config import settings


HEADERS = {"Authorization": f"Bearer {settings.BRIGHT_DATA_API_KEY}"}
SCRAPER_BASE = "https://api.brightdata.com/datasets/v3"
SERP_PROXY = f"http://{settings.BRIGHT_DATA_SERP_ZONE}@brd.superproxy.io:22225"
UNLOCKER_PROXY = f"http://{settings.BRIGHT_DATA_UNLOCKER_ZONE}@brd.superproxy.io:22225"


async def serp_search(query: str, num: int = 10) -> list[dict]:
    """SERP API — real-time Google search results via Bright Data proxy."""
    url = f"https://www.google.com/search?q={query}&num={num}&brd_json=1"
    async with httpx.AsyncClient(proxies={"https://": SERP_PROXY}, verify=False, timeout=30) as c:
        r = await c.get(url)
        r.raise_for_status()
        data = r.json()
        return data.get("organic", [])


async def scrape_url(url: str) -> str:
    """Web Unlocker — bypass anti-bot for any URL, returns page text."""
    async with httpx.AsyncClient(proxies={"https://": UNLOCKER_PROXY}, verify=False, timeout=45) as c:
        r = await c.get(url)
        r.raise_for_status()
        return r.text


async def scraper_api_trigger(dataset_id: str, inputs: list[dict]) -> list[dict]:
    """Web Scraper API — trigger a pre-built dataset collector and poll results."""
    async with httpx.AsyncClient(headers=HEADERS, timeout=60) as c:
        # trigger
        r = await c.post(f"{SCRAPER_BASE}/trigger", params={"dataset_id": dataset_id},
                         json={"inputs": inputs})
        r.raise_for_status()
        snapshot_id = r.json()["snapshot_id"]
        # poll until ready (max 30s)
        for _ in range(6):
            await __import__("asyncio").sleep(5)
            snap = await c.get(f"{SCRAPER_BASE}/snapshot/{snapshot_id}", params={"format": "json"})
            if snap.status_code == 200:
                return snap.json()
    return []


async def browser_scrape(url: str, js_scenario: Optional[list[dict]] = None) -> str:
    """Scraping Browser — full Playwright session through Bright Data CDP."""
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(settings.BRIGHT_DATA_BROWSER_WS)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        if js_scenario:
            for step in js_scenario:
                if step["action"] == "click":
                    await page.click(step["selector"])
                elif step["action"] == "fill":
                    await page.fill(step["selector"], step["value"])
                elif step["action"] == "wait":
                    await page.wait_for_timeout(step.get("ms", 1000))
        content = await page.content()
        await browser.close()
        return content


async def mcp_query(tool: str, params: dict) -> Any:
    """Bright Data MCP Server — call any MCP tool (search_engine, scrape_as_markdown, etc.)."""
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            f"{settings.BRIGHT_DATA_MCP_URL}/tools/{tool}",
            headers={"Authorization": f"Bearer {settings.BRIGHT_DATA_API_KEY}"},
            json=params,
        )
        r.raise_for_status()
        return r.json()

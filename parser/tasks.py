import asyncio
import aiohttp
from bs4 import BeautifulSoup

from parser.celery_worker import celery_app
from parser.connection import get_session
from parser.models import Page


@celery_app.task
def parse_and_save_task(url: str):
    asyncio.run(parse(url))


async def parse(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()

    soup = BeautifulSoup(html, "html.parser")

    name = soup.title.string.strip() if soup.title else "No name"

    description = "No description"
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):
        description = meta_tag["content"].strip()

    with get_session() as session:
        page = Page(name=name, description=description)
        session.merge(page)
        session.commit()

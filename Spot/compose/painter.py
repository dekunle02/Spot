import asyncio
from pyppeteer import launch

viewport_width = 1366
viewport_height = 900

async def paint_html_to_photo(html_string: str):
    browser = await launch()
    page = await browser.newPage()
    await page.setViewport({'width': viewport_width, 'height':viewport_height})
    await page.goto("https://www.wikipedia.org")
    await page.setContent(html_string)
    image_bytes_array = await page.screenshot()
    return image_bytes_array

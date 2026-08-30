import asyncio
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from playwright.async_api import async_playwright
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BotVerse API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

async def human_delay(min_sec=2.0, max_sec=6.0):
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def run_galaxy_worker(cookies: list, target_group_url: str):
    print("🚀 Galaxy Worker Started...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        if cookies:
            await context.add_cookies(cookies)
        page = await context.new_page()
        try:
            await page.goto(target_group_url, wait_until="networkidle")
            await human_delay(3, 7)
            posts = await page.query_selector_all('div[role="article"]')
            scraped_leads = []
            for post in posts[:5]:
                text_content = await post.inner_text()
                scraped_leads.append(text_content)
                print("✅ Lead Found:", text_content[:30], "...")
            return {"status": "success", "leads_count": len(scraped_leads)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            await browser.close()

class CampaignRequest(BaseModel):
    target_url: str
    cookies: list

@app.get("/")
def read_root():
    return {"message": "BotVerse API is Running!"}

@app.post("/api/start-campaign")
async def start_campaign(request: CampaignRequest):
    result = await run_galaxy_worker(request.cookies, request.target_url)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return {"message": "Success", "result": result}

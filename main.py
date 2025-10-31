from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Mount static files (public directory)
app.mount("/public", StaticFiles(directory="public"), name="public")

# Set up templates
templates = Jinja2Templates(directory="templates")


@app.get("/robots.txt", response_class=Response)
async def robots():
    """Serve robots.txt that only allows social media crawlers"""
    content = """User-agent: *
Disallow: /

# Allow Facebook crawler
User-agent: facebookexternalhit/1.1
Allow: /

# Allow Twitter crawler
User-agent: Twitterbot
Allow: /

# Allow LinkedIn crawler
User-agent: LinkedInBot
Allow: /

# Allow Pinterest crawler
User-agent: Pinterestbot
Allow: /

# Allow WhatsApp crawler
User-agent: WhatsApp
Allow: /

# Allow Telegram crawler
User-agent: TelegramBot
Allow: /

# Allow Slack crawler
User-agent: Slackbot
Allow: /
"""
    return Response(content=content, media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with path-based image sharing"""
    image_url = f"{request.base_url}public/image.jpg"
    page_url = str(request.url)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Beautiful Mountain Landscape",
            "description": "A stunning view of mountains at sunrise - share this beautiful image!",
            "image_url": image_url,
            "page_url": page_url,
            "route_type": "Path-based"
        }
    )


@app.get("/share", response_class=HTMLResponse)
async def share_with_query(request: Request, id: str = "default"):
    """Image sharing page with query string parameter"""
    image_url = f"{request.base_url}public/image.jpg"
    page_url = str(request.url)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": f"Beautiful Mountain Landscape (ID: {id})",
            "description": f"A stunning view of mountains at sunrise - share this beautiful image! (Share ID: {id})",
            "image_url": image_url,
            "page_url": page_url,
            "route_type": f"Query Parameter (id={id})"
        }
    )

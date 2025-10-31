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
            "og_url": page_url,  # Same as page_url for home route
            "route_type": "Path-based",
            "meta_refresh": None
        }
    )


@app.get("/share", response_class=HTMLResponse)
async def share_with_query(request: Request, qv: str = None, ssid: str = None):
    """Image sharing page with two query parameters to test Facebook crawling issue"""
    image_url = f"{request.base_url}public/image.jpg"
    page_url = str(request.url)

    # Check if parameters exist and their order in the query string
    query_string = str(request.url.query)

    # Determine if we need to trigger a meta refresh redirect
    # If qv comes before ssid in the query string, we'll redirect to swap them
    meta_refresh = None
    if qv and ssid:
        # Check the order of parameters in the query string
        qv_pos = query_string.find('qv=')
        ssid_pos = query_string.find('ssid=')

        if qv_pos >= 0 and ssid_pos >= 0 and qv_pos < ssid_pos:
            # qv comes before ssid, trigger meta refresh to swap order
            redirect_url = f"{request.base_url}share?ssid={ssid}&qv={qv}"
            meta_refresh = redirect_url

    # For og:url, intentionally drop qv parameter to replicate the issue
    if ssid and qv:
        og_url = f"{request.base_url}share?ssid={ssid}"  # Missing qv!
    elif ssid:
        og_url = f"{request.base_url}share?ssid={ssid}"
    elif qv:
        og_url = f"{request.base_url}share?qv={qv}"
    else:
        og_url = str(request.url)

    title = "Beautiful Mountain Landscape"
    if qv or ssid:
        title += f" (qv={qv or 'none'}, ssid={ssid or 'none'})"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": title,
            "description": f"A stunning view of mountains at sunrise - share this beautiful image! (qv={qv}, ssid={ssid})",
            "image_url": image_url,
            "page_url": page_url,
            "og_url": og_url,  # Different from page_url - this causes the issue!
            "route_type": f"Two Query Parameters (qv={qv}, ssid={ssid})",
            "meta_refresh": meta_refresh
        }
    )

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI()

# Mount static files (public directory)
app.mount("/public", StaticFiles(directory="public"), name="public")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Database setup
DB_PATH = "sessions.db"

def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_mapping (
            ssid TEXT PRIMARY KEY,
            qv TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_session_mapping(ssid: str, qv: str):
    """Save ssid -> qv mapping to database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO session_mapping (ssid, qv) VALUES (?, ?)",
        (ssid, qv)
    )
    conn.commit()
    conn.close()

def get_qv_for_ssid(ssid: str) -> str:
    """Look up qv value for a given ssid"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT qv FROM session_mapping WHERE ssid = ?", (ssid,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# Initialize database on startup
init_db()


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


@app.get("/session", response_class=HTMLResponse)
async def session_redirect(request: Request, ssid: str = None, qv: str = None):
    """
    Session route that returns HTML with meta refresh redirect to /share with both parameters.
    This route is used in og:url but redirects to the full /share URL.

    If qv is missing, it looks up the value from the database using ssid.
    The meta refresh swaps the parameter order from the incoming request.
    """
    # If qv is not provided, look it up from database
    if ssid and not qv:
        qv = get_qv_for_ssid(ssid)

    # Check the order of parameters in the incoming query string
    query_string = str(request.url.query)

    # Build redirect URL with parameters in REVERSE order
    if ssid and qv:
        # Check which parameter came first in the incoming request
        ssid_pos = query_string.find('ssid=')
        qv_pos = query_string.find('qv=')

        if qv_pos >= 0 and ssid_pos >= 0:
            # Both params present in query string
            if ssid_pos < qv_pos:
                # ssid came first, so reverse to qv first
                redirect_url = f"{request.base_url}share?qv={qv}&ssid={ssid}"
            else:
                # qv came first, so reverse to ssid first
                redirect_url = f"{request.base_url}share?ssid={ssid}&qv={qv}"
        else:
            # Only one param in query string (other was looked up from DB)
            # Since only ssid was in the URL, put qv first in redirect
            redirect_url = f"{request.base_url}share?qv={qv}&ssid={ssid}"
    elif ssid:
        redirect_url = f"{request.base_url}share?ssid={ssid}"
    elif qv:
        redirect_url = f"{request.base_url}share?qv={qv}"
    else:
        redirect_url = f"{request.base_url}share"

    # Return HTML with meta refresh instead of HTTP redirect
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url={redirect_url}">
    <title>Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="{redirect_url}">{redirect_url}</a>...</p>
</body>
</html>"""

    # Create response with custom headers
    from datetime import datetime
    current_time = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    headers = {
        "Cache-Control": "max-age=0, must-revalidate, private",
        "Expires": current_time,
        "Server": "Share Tester 1.0.0",
        "Backend-Version": "v1",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With,user-token",
        "Access-Control-Expose-Headers": "Authorization,user-token",
        "Vary": "Accept-Encoding"
    }

    return HTMLResponse(content=html_content, headers=headers)


@app.get("/share", response_class=HTMLResponse)
async def share_with_query(request: Request, qv: str = None, ssid: str = None):
    """Image sharing page with two query parameters to test Facebook crawling issue"""
    image_url = f"{request.base_url}public/image.jpg"
    page_url = str(request.url)

    # Save the mapping to database when both parameters are present
    if qv and ssid:
        save_session_mapping(ssid, qv)

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

    # For og:url, point to /session path with only ssid parameter to replicate the issue
    if ssid and qv:
        og_url = f"{request.base_url}session?ssid={ssid}"  # Different path, missing qv!
    elif ssid:
        og_url = f"{request.base_url}session?ssid={ssid}"
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

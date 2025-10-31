# Facebook Share Test Application

A Python FastAPI application for testing image sharing on social media platforms with proper Open Graph tags.

## Features

- ✅ Serves a beautiful free stock image from Unsplash
- ✅ Two routes for testing different sharing scenarios:
  - **Path-based route**: `/` - Simple URL without query parameters
  - **Query parameter route**: `/share?id=value` - URL with query string for testing parameter handling
- ✅ Complete Open Graph (OG) meta tags for Facebook, Twitter, and LinkedIn
- ✅ Custom robots.txt that only allows social media crawlers
- ✅ Responsive web design with sharing buttons
- ✅ Static file serving from public directory

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the application**:
```bash
uvicorn main:app --reload
```

The application will start at `http://localhost:8000`

## Routes

### 1. Path-based Route (/)
- URL: `http://localhost:8000/`
- Tests sharing without query parameters
- Clean URL structure

### 2. Query Parameter Route (/share)
- URL: `http://localhost:8000/share?id=test123`
- Tests sharing with query string parameters
- Useful for testing how platforms handle URL parameters
- Try different ID values: `/share?id=abc456`, `/share?id=xyz789`, etc.

## Testing Facebook Sharing

### Local Testing (Development)
When testing locally, Facebook's crawler cannot access `localhost`. You have two options:

1. **Use Facebook's Sharing Debugger**:
   - Deploy your app to a public server (ngrok, Heroku, etc.)
   - Visit: https://developers.facebook.com/tools/debug/
   - Enter your public URL to see how Facebook will parse it

2. **Use ngrok for local testing**:
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000
# Use the provided HTTPS URL in Facebook's debugger
```

### Production Testing
Once deployed to a public domain, you can:
- Test the share buttons directly
- Use Facebook's Sharing Debugger to validate OG tags
- Check that the correct image and metadata appear in previews

## Robots.txt

The application includes a custom `/robots.txt` that:
- **Disallows** all general web crawlers
- **Allows** only social media crawlers:
  - Facebook (facebookexternalhit)
  - Twitter (Twitterbot)
  - LinkedIn (LinkedInBot)
  - Pinterest (Pinterestbot)
  - WhatsApp
  - Telegram
  - Slack

View it at: `http://localhost:8000/robots.txt`

## Project Structure

```
fb-share-test/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── public/             # Static files directory
│   └── image.jpg       # Sample image from Unsplash
├── templates/          # Jinja2 templates
│   └── index.html      # Main template with OG tags
└── README.md           # This file
```

## Open Graph Tags Included

The application includes all essential OG tags:
- `og:type` - Website type
- `og:url` - Canonical URL
- `og:title` - Page title
- `og:description` - Page description
- `og:image` - Image URL
- `og:image:width` - Image width
- `og:image:height` - Image height
- `og:image:alt` - Image alt text

Plus Twitter Card tags for better Twitter integration.

## Image Attribution

The sample image is from Unsplash, a free stock photo service. The image is free to use under the Unsplash License.

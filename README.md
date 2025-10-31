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

### Development (Local Testing)

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the application**:
```bash
uvicorn main:app --reload
```

The application will start at `http://localhost:8000`

### Production Deployment (Nginx Web Server)

#### Quick Deployment (Automated)

The easiest way to deploy is using the provided deployment script:

```bash
# On your server, navigate to the project directory
cd /path/to/fb-share-test

# Run the deployment script as root
sudo ./deploy.sh
```

This script will:
- Copy files to `/var/www/fb-share-test`
- Create a Python virtual environment
- Install dependencies
- Set up systemd service
- Configure nginx
- Start the application

After deployment, edit the nginx config to use your domain:
```bash
sudo nano /etc/nginx/sites-available/fb-share
# Replace 'your-domain.com' with your actual domain
sudo systemctl reload nginx
```

#### Manual Deployment

If you prefer to deploy manually:

**1. Copy files to your web server:**
```bash
# Create directory
sudo mkdir -p /var/www/fb-share-test

# Copy files (use scp, rsync, or git clone)
sudo cp -r /path/to/fb-share-test/* /var/www/fb-share-test/
```

**2. Set up Python virtual environment:**
```bash
cd /var/www/fb-share-test
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
```

**3. Configure systemd service:**
```bash
# Copy service file
sudo cp fb-share.service /etc/systemd/system/

# Edit if needed (change paths, user, etc.)
sudo nano /etc/systemd/system/fb-share.service

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable fb-share.service
sudo systemctl start fb-share.service

# Check status
sudo systemctl status fb-share.service
```

**4. Configure nginx:**
```bash
# Copy nginx config
sudo cp nginx.conf /etc/nginx/sites-available/fb-share

# Edit and replace 'your-domain.com' with your actual domain
sudo nano /etc/nginx/sites-available/fb-share

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/fb-share /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

**5. Set permissions:**
```bash
sudo chown -R www-data:www-data /var/www/fb-share-test
sudo chmod -R 755 /var/www/fb-share-test
```

#### SSL Certificate (Optional but Recommended)

For HTTPS support, use Let's Encrypt:

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Certbot will automatically update your nginx config
```

The nginx.conf file includes commented SSL configuration that certbot will use.

#### Managing the Application

**Service commands:**
```bash
# View logs
sudo journalctl -u fb-share -f

# Restart application
sudo systemctl restart fb-share

# Stop application
sudo systemctl stop fb-share

# Start application
sudo systemctl start fb-share

# Check status
sudo systemctl status fb-share
```

**Nginx commands:**
```bash
# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# View nginx logs
sudo tail -f /var/log/nginx/fb-share-access.log
sudo tail -f /var/log/nginx/fb-share-error.log
```

#### Updating the Application

To update after making changes:

```bash
# Copy updated files to server
sudo cp -r /path/to/updated/files/* /var/www/fb-share-test/

# Restart the service
sudo systemctl restart fb-share
```

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
Once deployed to your nginx web server with a public domain:

1. **Access your application:**
   - Visit `http://your-domain.com/` for the path-based route
   - Visit `http://your-domain.com/share?id=test123` for the query parameter route

2. **Validate Open Graph tags:**
   - Use Facebook's Sharing Debugger: https://developers.facebook.com/tools/debug/
   - Enter your production URL (e.g., `http://your-domain.com/`)
   - Facebook will show how your page will appear when shared
   - You can also use this to clear Facebook's cache if you make changes

3. **Test sharing:**
   - Click the share buttons on your page
   - Or manually share the URL on Facebook
   - Verify the correct image, title, and description appear in the preview

4. **Test both routes:**
   - Share the root path: `http://your-domain.com/`
   - Share with query parameters: `http://your-domain.com/share?id=test123`
   - Verify both render correctly with their respective metadata

**Important for Facebook sharing:**
- Facebook requires HTTPS for optimal sharing. Use certbot to set up SSL.
- Facebook caches OG tags. Use the Sharing Debugger to clear the cache after changes.
- The robots.txt allows Facebook's crawler (facebookexternalhit) to access your pages.

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
├── fb-share.service     # Systemd service configuration
├── nginx.conf           # Nginx server configuration
├── deploy.sh            # Automated deployment script
├── public/              # Static files directory
│   └── image.jpg        # Sample image from Unsplash
├── templates/           # Jinja2 templates
│   └── index.html       # Main template with OG tags
├── .gitignore           # Git ignore file
└── README.md            # This file
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

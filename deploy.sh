#!/bin/bash

# Facebook Share Test - Deployment Script
# This script helps deploy the application to an nginx web server

set -e  # Exit on error

echo "=== Facebook Share Test Deployment Script ==="
echo ""

# Configuration variables (modify these as needed)
APP_DIR="/opt/fb-share-test"
APP_USER="www-data"
APP_GROUP="www-data"
SERVICE_NAME="fb-share"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Step 1: Creating application directory..."
mkdir -p $APP_DIR
echo "✓ Directory created: $APP_DIR"

echo ""
echo "Step 2: Copying application files..."
cp -r ./* $APP_DIR/
echo "✓ Files copied"

echo ""
echo "Step 3: Setting up Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
echo "✓ Virtual environment created"

echo ""
echo "Step 4: Installing Python dependencies..."
$APP_DIR/venv/bin/pip install --upgrade pip
$APP_DIR/venv/bin/pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "Step 5: Setting correct permissions..."
chown -R $APP_USER:$APP_GROUP $APP_DIR
chmod -R 755 $APP_DIR
echo "✓ Permissions set"

echo ""
echo "Step 6: Installing systemd service..."
cp $APP_DIR/fb-share.service /etc/systemd/system/$SERVICE_NAME.service
systemctl daemon-reload
systemctl enable $SERVICE_NAME.service
echo "✓ Service installed and enabled"

echo ""
echo "Step 7: Starting the service..."
systemctl restart $SERVICE_NAME.service
sleep 2
systemctl status $SERVICE_NAME.service --no-pager
echo "✓ Service started"

echo ""
echo "Step 8: Configuring domain name..."
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    echo "Error: Domain name is required"
    exit 1
fi

echo "✓ Domain name set to: $DOMAIN_NAME"

echo ""
echo "Step 9: Installing nginx configuration..."
if [ -f "/etc/nginx/sites-available/$SERVICE_NAME" ]; then
    echo "  Warning: Nginx config already exists. Backing up..."
    cp /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-available/$SERVICE_NAME.backup.$(date +%Y%m%d_%H%M%S)
fi
cp $APP_DIR/nginx.conf /etc/nginx/sites-available/$SERVICE_NAME

# Replace placeholder domain with actual domain
sed -i "s/your-domain.com/$DOMAIN_NAME/g" /etc/nginx/sites-available/$SERVICE_NAME

# Create symbolic link if it doesn't exist
if [ ! -L "/etc/nginx/sites-enabled/$SERVICE_NAME" ]; then
    ln -s /etc/nginx/sites-available/$SERVICE_NAME /etc/nginx/sites-enabled/$SERVICE_NAME
fi
echo "✓ Nginx config installed with domain: $DOMAIN_NAME"

echo ""
echo "Step 10: Testing nginx configuration..."
nginx -t
echo "✓ Nginx config is valid"

echo ""
echo "Step 11: Reloading nginx..."
systemctl reload nginx
echo "✓ Nginx reloaded"

echo ""
echo "Step 12: Setting up SSL certificate with Let's Encrypt..."
read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " SETUP_SSL

if [ "$SETUP_SSL" = "y" ] || [ "$SETUP_SSL" = "Y" ]; then
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        echo "  Installing certbot..."
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
        echo "  ✓ Certbot installed"
    else
        echo "  ✓ Certbot already installed"
    fi

    read -p "Enter your email address for Let's Encrypt notifications: " EMAIL

    if [ -z "$EMAIL" ]; then
        echo "  Warning: No email provided. Skipping SSL setup."
        echo "  You can run this later: sudo certbot --nginx -d $DOMAIN_NAME"
    else
        echo "  Obtaining SSL certificate for $DOMAIN_NAME..."
        echo ""
        echo "  NOTE: Only include www subdomain if you have DNS configured for it!"
        echo "  Most users should answer 'n' here."

        # Check if www subdomain should be included
        read -p "Include www.$DOMAIN_NAME? (y/N, default=N): " INCLUDE_WWW
        INCLUDE_WWW=${INCLUDE_WWW:-n}  # Default to 'n' if empty

        if [ "$INCLUDE_WWW" = "y" ] || [ "$INCLUDE_WWW" = "Y" ]; then
            echo "  Getting certificate for both $DOMAIN_NAME and www.$DOMAIN_NAME..."
            certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL --redirect
        else
            echo "  Getting certificate for $DOMAIN_NAME only..."
            certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL --redirect
        fi

        echo "  ✓ SSL certificate obtained and configured"
        echo "  ✓ HTTP to HTTPS redirect enabled"

        # Set up auto-renewal
        systemctl enable certbot.timer
        systemctl start certbot.timer
        echo "  ✓ Auto-renewal configured"
    fi
else
    echo "  Skipping SSL setup. You can set it up later with:"
    echo "  sudo certbot --nginx -d $DOMAIN_NAME"
fi

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Your application is now running!"
echo "  HTTP:  http://$DOMAIN_NAME"
if [ "$SETUP_SSL" = "y" ] || [ "$SETUP_SSL" = "Y" ]; then
    if [ -n "$EMAIL" ]; then
        echo "  HTTPS: https://$DOMAIN_NAME"
    fi
fi
echo ""
echo "Service commands:"
echo "  View logs:    sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart app:  sudo systemctl restart $SERVICE_NAME"
echo "  Stop app:     sudo systemctl stop $SERVICE_NAME"
echo "  Check status: sudo systemctl status $SERVICE_NAME"
echo ""
echo "Nginx commands:"
echo "  Test config:  sudo nginx -t"
echo "  Reload:       sudo systemctl reload nginx"
echo "  Logs:         sudo tail -f /var/log/nginx/fb-share-access.log"
echo ""
echo "SSL certificate renewal:"
echo "  Test renewal: sudo certbot renew --dry-run"
echo "  Force renew:  sudo certbot renew --force-renewal"
echo ""
echo "Test your Facebook sharing at: https://developers.facebook.com/tools/debug/"

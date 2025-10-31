#!/bin/bash

# Facebook Share Test - SSL Setup Script
# This script sets up Let's Encrypt SSL certificate for your domain

set -e  # Exit on error

echo "=== Let's Encrypt SSL Setup ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME

if [ -z "$DOMAIN_NAME" ]; then
    echo "Error: Domain name is required"
    exit 1
fi

echo "Domain: $DOMAIN_NAME"
echo ""

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Certbot is not installed. Installing..."
    apt-get update
    apt-get install -y certbot python3-certbot-nginx
    echo "✓ Certbot installed"
else
    echo "✓ Certbot already installed"
fi

echo ""

# Get email address
read -p "Enter your email address for Let's Encrypt notifications: " EMAIL

if [ -z "$EMAIL" ]; then
    echo "Error: Email address is required"
    exit 1
fi

echo ""

# Check if www subdomain should be included
read -p "Include www.$DOMAIN_NAME? (y/n): " INCLUDE_WWW

echo ""
echo "Obtaining SSL certificate..."
echo "This may take a minute..."
echo ""

# Run certbot
if [ "$INCLUDE_WWW" = "y" ] || [ "$INCLUDE_WWW" = "Y" ]; then
    certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL --redirect
    echo ""
    echo "✓ SSL certificate obtained for:"
    echo "  - $DOMAIN_NAME"
    echo "  - www.$DOMAIN_NAME"
else
    certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL --redirect
    echo ""
    echo "✓ SSL certificate obtained for $DOMAIN_NAME"
fi

echo "✓ HTTP to HTTPS redirect enabled"
echo ""

# Set up auto-renewal
echo "Setting up automatic certificate renewal..."
systemctl enable certbot.timer 2>/dev/null || true
systemctl start certbot.timer 2>/dev/null || true
echo "✓ Auto-renewal configured (certificates will renew automatically)"

echo ""
echo "Testing nginx configuration..."
nginx -t
echo "✓ Nginx configuration is valid"

echo ""
echo "Reloading nginx..."
systemctl reload nginx
echo "✓ Nginx reloaded"

echo ""
echo "=== SSL Setup Complete! ==="
echo ""
echo "Your site is now secured with HTTPS:"
echo "  https://$DOMAIN_NAME"
if [ "$INCLUDE_WWW" = "y" ] || [ "$INCLUDE_WWW" = "Y" ]; then
    echo "  https://www.$DOMAIN_NAME"
fi
echo ""
echo "Certificate information:"
certbot certificates
echo ""
echo "Important commands:"
echo "  Test renewal:   sudo certbot renew --dry-run"
echo "  Force renewal:  sudo certbot renew --force-renewal"
echo "  View certs:     sudo certbot certificates"
echo "  Revoke cert:    sudo certbot revoke --cert-path /etc/letsencrypt/live/$DOMAIN_NAME/cert.pem"
echo ""
echo "Your certificate will auto-renew before expiration (90 days)."
echo ""
echo "Test your Facebook sharing at: https://developers.facebook.com/tools/debug/"

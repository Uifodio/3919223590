#!/usr/bin/env python3
"""
Nginx Configuration Generator
============================

Generates nginx configuration files for the Unified Server Administrator.
Supports PHP-FPM, Node.js reverse proxy, and static file serving.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional

class NginxConfigGenerator:
    def __init__(self, config_dir: str = "/etc/nginx/sites-available"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_main_config(self) -> str:
        """Generate main nginx configuration with optimizations"""
        return """
user www-data;
worker_processes auto;
pid /run/nginx.pid;
include /etc/nginx/modules-enabled/*.conf;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # Basic Settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;

    # MIME Types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Gzip Settings
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Include site configurations
    include /etc/nginx/sites-enabled/*;
}
"""

    def generate_php_config(self, server_name: str, port: int, site_path: str, domain: str = None) -> str:
        """Generate nginx configuration for PHP with php-fpm"""
        server_name_config = domain or f"{server_name}.local"
        
        return f"""
server {{
    listen {port};
    server_name {server_name_config};
    root {site_path};
    index index.php index.html index.htm;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # PHP processing
    location ~ \\.php$ {{
        try_files $uri =404;
        fastcgi_split_path_info ^(.+\\.php)(/.+)$;
        fastcgi_pass unix:/var/run/php/php8.1-fpm-{server_name}.sock;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
        
        # Security
        fastcgi_hide_header X-Powered-By;
        fastcgi_read_timeout 300;
        fastcgi_connect_timeout 300;
        fastcgi_send_timeout 300;
    }}
    
    # Static files
    location / {{
        try_files $uri $uri/ /index.php?$query_string;
        
        # Cache static files
        location ~* \\.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # Deny access to hidden files
    location ~ /\\. {{
        deny all;
    }}
    
    # Logging
    access_log /var/log/nginx/{server_name}_access.log;
    error_log /var/log/nginx/{server_name}_error.log;
}}
"""

    def generate_nodejs_config(self, server_name: str, port: int, site_path: str, domain: str = None) -> str:
        """Generate nginx configuration for Node.js reverse proxy"""
        server_name_config = domain or f"{server_name}.local"
        
        return f"""
upstream {server_name}_backend {{
    server 127.0.0.1:{port + 1000};
    keepalive 32;
}}

server {{
    listen {port};
    server_name {server_name_config};
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # Proxy to Node.js
    location / {{
        proxy_pass http://{server_name}_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}
    
    # Static files (if any)
    location ~* \\.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {{
        root {site_path};
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
    
    # Logging
    access_log /var/log/nginx/{server_name}_access.log;
    error_log /var/log/nginx/{server_name}_error.log;
}}
"""

    def generate_static_config(self, server_name: str, port: int, site_path: str, domain: str = None) -> str:
        """Generate nginx configuration for static files"""
        server_name_config = domain or f"{server_name}.local"
        
        return f"""
server {{
    listen {port};
    server_name {server_name_config};
    root {site_path};
    index index.html index.htm;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
    
    # Static files
    location / {{
        try_files $uri $uri/ =404;
        
        # Cache static files
        location ~* \\.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}
    
    # Deny access to hidden files
    location ~ /\\. {{
        deny all;
    }}
    
    # Logging
    access_log /var/log/nginx/{server_name}_access.log;
    error_log /var/log/nginx/{server_name}_error.log;
}}
"""

    def save_config(self, server_name: str, config: str) -> str:
        """Save nginx configuration to file"""
        config_path = self.config_dir / f"{server_name}.conf"
        config_path.write_text(config, encoding='utf-8')
        return str(config_path)

    def enable_site(self, server_name: str) -> bool:
        """Enable nginx site by creating symlink"""
        try:
            source = self.config_dir / f"{server_name}.conf"
            target = Path("/etc/nginx/sites-enabled") / f"{server_name}.conf"
            
            if target.exists():
                target.unlink()
            
            target.symlink_to(source)
            return True
        except Exception as e:
            print(f"Failed to enable nginx site {server_name}: {e}")
            return False

    def disable_site(self, server_name: str) -> bool:
        """Disable nginx site by removing symlink"""
        try:
            target = Path("/etc/nginx/sites-enabled") / f"{server_name}.conf"
            if target.exists():
                target.unlink()
            return True
        except Exception as e:
            print(f"Failed to disable nginx site {server_name}: {e}")
            return False

    def test_config(self) -> bool:
        """Test nginx configuration"""
        import subprocess
        try:
            result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def reload_nginx(self) -> bool:
        """Reload nginx configuration"""
        import subprocess
        try:
            if not self.test_config():
                return False
            
            result = subprocess.run(['systemctl', 'reload', 'nginx'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                # Fallback to nginx -s reload
                result = subprocess.run(['nginx', '-s', 'reload'], 
                                      capture_output=True, text=True)
                return result.returncode == 0
            return True
        except Exception:
            return False

if __name__ == "__main__":
    generator = NginxConfigGenerator()
    
    # Example usage
    print("Nginx Configuration Generator")
    print("=" * 40)
    
    # Generate main config
    main_config = generator.generate_main_config()
    print("Main nginx configuration generated")
    
    # Generate PHP config example
    php_config = generator.generate_php_config("example-php", 8080, "/var/www/example", "example.com")
    print("PHP configuration example generated")
    
    # Generate Node.js config example
    nodejs_config = generator.generate_nodejs_config("example-node", 8081, "/var/www/node-app", "api.example.com")
    print("Node.js configuration example generated")
    
    # Generate static config example
    static_config = generator.generate_static_config("example-static", 8082, "/var/www/static", "static.example.com")
    print("Static configuration example generated")
    
    print("\nAll configurations generated successfully!")
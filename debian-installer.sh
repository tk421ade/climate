#!/usr/bin/env bash
#
# Debian 12 Installer
#

# configure git and clone repository
apt-get install git nginx virtualenvwrapper -y
cd /opt/
git clone https://github.com/tk421ade/climate.git
cd /opt/climate
make prepare

# run gunicorn
# /opt/climate/venv/bin/gunicorn climate.wsgi

cat > /etc/systemd/system/gunicorn.service << 'EOF'
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
# the specific user that our service will run as
User=www-data
Group=www-data
# another option for an even more restricted service is
# DynamicUser=yes
# see http://0pointer.net/blog/dynamic-users-with-systemd.html
RuntimeDirectory=gunicorn
WorkingDirectory=/opt/climate
ExecStart=/opt/climate/venv/bin/gunicorn climate.wsgi
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/gunicorn.socket << 'EOF'
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
# Our service won't need permissions for the socket, since it
# inherits the file descriptor by socket activation
# only the nginx daemon will need access to the socket
SocketUser=www-data
# Optionally restrict the socket permissions even more.
# SocketMode=600

[Install]
WantedBy=sockets.target
EOF

# test that gunicorn over socket is working
# sudo -u www-data curl --unix-socket /run/gunicorn.sock http

# configure nginx
cat > /etc/nginx/sites-available/climate << 'EOF'
  upstream app_server {
    # fail_timeout=0 means we always retry an upstream even if it failed
    # to return a good HTTP response

    # for UNIX domain socket setups
    server unix:/run/gunicorn.sock fail_timeout=0;

  }

  #server {
  #  # if no Host match, close the connection to prevent host spoofing
  #  listen 80 default_server;
  #  return 444;
  #}

  server {
    # use 'listen 80 deferred;' for Linux
    # use 'listen 80 accept_filter=httpready;' for FreeBSD
    #listen 80;
    listen 80 default_server;
    client_max_body_size 4G;

    # set the correct host(s) for your site
    #server_name example.com www.example.com;

    keepalive_timeout 5;

    # path for static files
    root /path/to/app/current/public;

    location / {
      # checks for static file, if not found proxy to app
      try_files $uri @proxy_to_app;
    }

    location @proxy_to_app {
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header Host $http_host;
      # we don't want nginx trying to do something clever with
      # redirects, we set the Host: header above already.
      proxy_redirect off;
      proxy_pass http://app_server;
    }

    error_page 500 502 503 504 /500.html;
    location = /500.html {
      root /path/to/app/current/public;
    }
  }
EOF

rm -f /etc/nginx/sites-enabled/default
ln -s /etc/nginx/sites-available/climate /etc/nginx/sites-enabled/climate

/sbin/iptables -I INPUT -p tcp -m tcp --dport 80 -j ACCEPT
/sbin/iptables -I INPUT -p tcp -m tcp --dport 443 -j ACCEPT


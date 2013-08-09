#!/bin/sh
#
# Build a scrypt-helper webhead node for AWS deployment.
# They're simple little compute notes running nginx and gunicorn.

set -e

YUM="yum --assumeyes --enablerepo=epel"

$YUM update
$YUM install python-pip git

# Checkout and build latest scrypt-helper
# XXX TODO: technically, we should build the currently-check-out version.
# AWSBoxen needs to learn how to pass the commit ref into this script.

python-pip install virtualenv

useradd scrypthelper

UDO="sudo -u scrypthelper"

cd /home/scrypthelper
$UDO git clone https://github.com/mozilla/scrypt-helper.git
cd ./scrypt-helper
if [ ! -f setup.py ]; then
  git checkout aws-deployment
fi

# Build a virtualenv with all the dependencies.

$YUM install openssl-devel python-devel gcc gcc-c++

$UDO virtualenv --no-site-packages ./local
$UDO ./local/bin/pip install .
$UDO ./local/bin/pip install gunicorn

# Write a circus config script.

cd ../
cat > circus.ini << EOF
[watcher:scrypthelper]
working_dir=/home/scrypthelper/scrypt-helper
cmd=local/bin/gunicorn -w 4 scrypt_helper.run
numprocesses = 1
EOF
chown scrypthelper:scrypthelper circus.ini

# Launch the server via circus on startup.

python-pip install circus

cat > /etc/rc.local << EOF
su -l scrypthelper -c '/usr/bin/circusd --daemon /home/scrypthelper/circus.ini'
exit 0
EOF

# Setup nginx as proxy.

$YUM install nginx

cat << EOF > /etc/nginx/nginx.conf
user  nginx;
worker_processes  1;
events {
    worker_connections  20480;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    log_format xff '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                   '\$status \$body_bytes_sent "\$http_referer" '
                   '"\$http_user_agent" XFF="\$http_x_forwarded_for" '
                   'TIME=\$request_time ';
    access_log /var/log/nginx/access.log xff;
    server {
        listen       80 default;
        location / {
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header Host \$http_host;
            proxy_redirect off;
            proxy_pass http://localhost:8000;
        }
    }
}
EOF

/sbin/chkconfig nginx on
/sbin/service nginx start

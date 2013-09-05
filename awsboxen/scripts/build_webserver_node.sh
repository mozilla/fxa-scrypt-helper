#!/bin/sh
#
# Build a scrypt-helper webhead node for AWS deployment.
# They're simple little compute notes running nginx and gunicorn.

set -e

YUM="yum --assumeyes --enablerepo=epel"

$YUM update
$YUM install python-pip git

# Add ssh public keys.

git clone https://github.com/mozilla/identity-pubkeys
cd identity-pubkeys
git checkout b63a19a153f631c949e7f6506ad4bf1f258dda69
cat *.pub >> /home/ec2-user/.ssh/authorized_keys
cd ..
rm -rf identity-pubkeys

# Checkout and build the active commit of scrypt-helper.

python-pip install virtualenv

useradd scrypthelper

UDO="sudo -u scrypthelper"

cd /home/scrypthelper
$UDO git clone https://github.com/mozilla/scrypt-helper.git
cd ./scrypt-helper
git checkout {"Ref": "AWSBoxenCommit"}

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
stdout_stream.class = FileStream
stdout_stream.filename = /home/scrypthelper/circus.log
stdout_stream.refresh_time = 0.5
stdout_stream.max_bytes = 1073741824
stdout_stream.backup_count = 3
stderr_stream.class = StdoutStream
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
            if (\$request_method = 'OPTIONS') {
                add_header 'Access-Control-Allow-Origin' '*';
                add_header 'Access-Control-Allow-Credentials' 'true';
                add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
                add_header 'Access-Control-Max-Age' 1728000;
                add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
                add_header 'Content-Type' 'text/plain charset=UTF-8';
                add_header 'Content-Length' 0;
                return 204;
            }
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Access-Control-Allow-Headers' 'DNT,X-Mx-ReqToken,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
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

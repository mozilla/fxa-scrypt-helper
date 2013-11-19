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

# Checkout and build scrypt-helper master branch.

python-pip install virtualenv

useradd app

UDO="sudo -u app"

cd /home/app
$UDO git clone https://github.com/mozilla/scrypt-helper.git
cd ./scrypt-helper

# Build a virtualenv with all the dependencies.

$YUM install openssl-devel python-devel gcc gcc-c++

$UDO virtualenv --no-site-packages ./local
$UDO ./local/bin/pip install .
$UDO ./local/bin/pip install gunicorn

# Write a circus config script.

cd ../
cat > circus.ini << EOF
[watcher:scrypthelper]
working_dir=/home/app/scrypt-helper
cmd=local/bin/gunicorn -w 4 scrypt_helper.run
numprocesses = 1
stdout_stream.class = FileStream
stdout_stream.filename = /home/app/scrypt-helper/circus.stdout.log
stdout_stream.refresh_time = 0.5
stdout_stream.max_bytes = 1073741824
stdout_stream.backup_count = 3
stderr_stream.class = FileStream
stderr_stream.filename = /home/app/scrypt-helper/circus.stderr.log
stderr_stream.refresh_time = 0.5
stderr_stream.max_bytes = 1073741824
stderr_stream.backup_count = 3
EOF
chown app:app circus.ini

# Launch the server via circus on startup.

python-pip install circus

cat > /etc/rc.local << EOF
su -l app -c '/usr/bin/circusd --daemon /home/app/circus.ini'
exit 0
EOF

# Write ver.txt for easy checking of current dev version.

cd ./scrypt-helper
$UDO git log --pretty=oneline -1 > ../ver.txt
chown app:app ../ver.txt
chmod +x /home/app
cd ../

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
        location /ver.txt {
            alias /home/app/ver.txt;
        }
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


# Install heka, have it send logfiles through to aggregator box.

HEKAFILE=heka-0_4_0-picl-idp-amd64.tar.gz
cd /opt
wget https://people.mozilla.com/~rmiller/heka/$HEKAFILE
tar -xzvf $HEKAFILE
rm -f $HEKAFILE

cd /home/app
mkdir ./hekad
chown app:app ./hekad

# Set some basic heka configuration.

cat > ./hekad/hekad.toml << EOF
[hekad]
base_dir = "/home/app/hekad"

[debug]
type = "FileOutput"
message_matcher = "TRUE"
path = "/home/app/hekad/hekad.log"
format = "json"


[app-error-log]
type = "LogfileInput"
logfile = "/home/app/scrypt-helper/circus.stderr.log"
decoders = ["app-error-decoder"]

[app-error-decoder]
type = "PayloadRegexDecoder"
timestamp_layout = "02/Jan/2006:15:04:05 -0700"
match_regex = '^(?P<Message>.+)'

[app-error-decoder.message_fields]
Type = "logfile"
Logger = "app"
App = "scrypt-helper"
Message = "%Message%"



[nginx-access-log]
type = "LogfileInput"
logfile = "/var/log/nginx/access.log"
decoders = ["nginx-log-decoder"]

[nginx-log-decoder]
type = "PayloadRegexDecoder"
timestamp_layout = "02/Jan/2006:15:04:05 -0700"
match_regex = '^(?P<RemoteIP>\S+) \S+ \S+ \[(?P<Timestamp>[^\]]+)\] "(?P<Method>[A-Z\-]+) (?P<Url>[^\s]+)[^"]*" (?P<StatusCode>\d+) (?P<RequestSize>\d+) "(?P<Referer>[^"]*)" "(?P<Browser>[^"]*)" XFF="(?P<XFF>[^"]+)" TIME=(?P<Time>\S+)'

[nginx-log-decoder.message_fields]
Type = "logfile"
Logger = "nginx"
App = "scrypt-helper"
Url|uri = "%Url%"
Method = "%Method%"
Status = "%StatusCode%"
RequestSize|B = "%RequestSize%"
Referer = "%Referer%"
Browser = "%Browser%"
RequestTime = "%Time%"
XForwardedFor = "%XFF%"

[aggregator-output]
type = "AMQPOutput"
message_matcher = "TRUE"
url = "amqp://heka:{"Ref":"AMQPPassword"}@logs.{"Ref":"DNSPrefix"}.lcip.org:5672/"
exchange = "heka"
exchangeType = "fanout"
EOF

chown app:app hekad/hekad.toml

chmod +r /var/log/nginx
chmod +x /var/log/nginx
chmod +r /var/log/nginx/access.log

cat >> circus.ini << EOF

[watcher:hekad]
working_dir=/home/app/hekad
cmd=/opt/heka-0_4_0-linux-amd64/bin/hekad -config=/home/app/hekad/hekad.toml
numprocesses = 1
stdout_stream.class = FileStream
stdout_stream.filename = /home/app/hekad/circus.stdout.log
stdout_stream.refresh_time = 0.5
stdout_stream.max_bytes = 1073741824
stdout_stream.backup_count = 3
stderr_stream.class = FileStream
stderr_stream.filename = /home/app/hekad/circus.stderr.log
stderr_stream.refresh_time = 0.5
stderr_stream.max_bytes = 1073741824
stderr_stream.backup_count = 3

EOF


# Stub out a cronjob to auto-update to latest master.
# It's not active by default; to enable it do:
#
#   echo "*/5 * * * * /bin/bash -l /home/app/auto_update.sh > /dev/null 2> /dev/null" | sudo crontab -u app -

cat >> /home/app/auto_update.sh << EOF
#!/bin/sh

set -e

CURCOMMIT="git log --pretty=%h -1"

cd /home/app/scrypt-helper
git fetch origin

date > /home/app/LAST_AUTO_UPDATE.txt

if [ \`\$CURCOMMIT master\` != \`\$CURCOMMIT origin/master\` ]; then
  git pull
  git log --pretty=oneline -1 > ../ver.txt
  circusctl restart
fi

EOF

chmod +r /home/app/auto_update.sh
chmod +x /home/app/auto_update.sh

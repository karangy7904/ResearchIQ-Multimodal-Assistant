import boto3, time

ssm = boto3.client('ssm', region_name='ap-southeast-2')
instance_id = 'i-09f6d429f7c1c7c30'

nginx_script = """cat << 'EOF' > /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /run/nginx.pid;
events {
    worker_connections 1024;
}
http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    sendfile on;
    keepalive_timeout 65;
    server {
        listen 80 default_server;
        server_name _;
        client_max_body_size 100M;

        location /researchiq-api/ {
            proxy_pass http://127.0.0.1:8002/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /researchiq {
            proxy_pass http://127.0.0.1:7861;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 600s;
        }

        location /cea-api/ {
            proxy_pass http://127.0.0.1:8001/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /cea {
            proxy_pass http://127.0.0.1:7860;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 600s;
        }

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 600s;
            proxy_connect_timeout 600s;
        }
    }
}
EOF
nginx -t && systemctl reload nginx
"""

resp = ssm.send_command(
    InstanceIds=[instance_id],
    DocumentName='AWS-RunShellScript',
    Parameters={'commands': [nginx_script]}
)

cmd_id = resp['Command']['CommandId']
time.sleep(4)
inv = ssm.get_command_invocation(CommandId=cmd_id, InstanceId=instance_id)
print('STATUS:', inv['Status'])
print('STDOUT:\n', inv['StandardOutputContent'])
print('STDERR:\n', inv['StandardErrorContent'])

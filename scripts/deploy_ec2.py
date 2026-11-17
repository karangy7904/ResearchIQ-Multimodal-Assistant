import boto3, time

ssm = boto3.client('ssm', region_name='ap-southeast-2')
instance_id = 'i-09f6d429f7c1c7c30'

commands = [
    # 1. Setup swap if missing
    '''if [ ! -f /swapfile ]; then
        fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
    fi''',
    # 2. Clone or update repo
    '''if [ ! -d /opt/researchiq/.git ]; then
        git clone https://github.com/karangy7904/ResearchIQ-Multimodal-Assistant.git /opt/researchiq
    else
        cd /opt/researchiq && git fetch origin && git reset --hard origin/main
    fi''',
    # 3. Create virtualenv and install requirements
    '''cd /opt/researchiq
    if [ ! -d /opt/researchiq/.venv ]; then
        /usr/bin/python3.11 -m venv /opt/researchiq/.venv
    fi
    /opt/researchiq/.venv/bin/pip install --upgrade pip
    /opt/researchiq/.venv/bin/pip install -r requirements.txt
    ''',
    # 4. Setup .env
    '''cat << 'EOF' > /opt/researchiq/.env
AWS_REGION=ap-southeast-2
AWS_DEFAULT_REGION=ap-southeast-2
S3_BUCKET=firstrag
BEDROCK_CHAT_MODEL=apac.amazon.nova-pro-v1:0
BEDROCK_EMBED_MODEL=amazon.titan-embed-text-v2:0
BEDROCK_TABLE_EMBED_MODEL=cohere.embed-english-v3
API_PORT=8002
GRADIO_PORT=7861
GRADIO_ROOT_PATH=/researchiq
EOF
    ''',
    # 5. Setup systemd service
    '''cat << 'EOF' > /etc/systemd/system/researchiq.service
[Unit]
Description=ResearchIQ Multimodal Research Assistant
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/researchiq
EnvironmentFile=/opt/researchiq/.env
ExecStart=/opt/researchiq/.venv/bin/python -m uvicorn app.api:app --host 0.0.0.0 --port 8002
ExecStartPost=/bin/sleep 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

cat << 'EOF' > /etc/systemd/system/researchiq-ui.service
[Unit]
Description=ResearchIQ Gradio UI
After=network.target researchiq.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/researchiq
EnvironmentFile=/opt/researchiq/.env
ExecStart=/opt/researchiq/.venv/bin/python -u -m app.ui
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable researchiq.service researchiq-ui.service
    systemctl restart researchiq.service researchiq-ui.service
    ''',
    # 6. Check status
    'systemctl status researchiq.service --no-pager -l',
    'systemctl status researchiq-ui.service --no-pager -l'
]

print("Sending deployment command to EC2 instance:", instance_id)
resp = ssm.send_command(
    InstanceIds=[instance_id],
    DocumentName='AWS-RunShellScript',
    Parameters={'commands': commands},
    TimeoutSeconds=900
)

command_id = resp['Command']['CommandId']
print(f"Command dispatched with ID: {command_id}. Waiting for completion...")

while True:
    time.sleep(5)
    inv = ssm.get_command_invocation(CommandId=command_id, InstanceId=instance_id)
    status = inv['Status']
    print(f"Deployment status: {status}...")
    if status in ['Success', 'Failed', 'TimedOut', 'Cancelled']:
        print("Final Status:", status)
        print("=== STDOUT ===")
        print(inv.get('StandardOutputContent', ''))
        print("=== STDERR ===")
        print(inv.get('StandardErrorContent', ''))
        break

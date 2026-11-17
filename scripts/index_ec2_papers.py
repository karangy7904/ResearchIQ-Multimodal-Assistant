import boto3, time

ssm = boto3.client('ssm', region_name='ap-southeast-2')
instance_id = 'i-09f6d429f7c1c7c30'

cmd = """
cd /opt/researchiq
mkdir -p papers
aws s3 sync s3://firstrag/papers/ papers/ --region ap-southeast-2
find papers/ -type f -name "*.pdf" | head -n 4 | while read f; do
    echo "Found paper: $f"
done
/opt/researchiq/.venv/bin/python -c "
import glob
from app.ingestion import ingest_pdf
pdfs = glob.glob('papers/**/*.pdf', recursive=True)[:4]
print(f'Ingesting {len(pdfs)} papers on EC2...')
for p in pdfs:
    print('Ingesting:', p)
    res = ingest_pdf(p, p.split('/')[-1])
    print('Done:', res)
"
"""

resp = ssm.send_command(
    InstanceIds=[instance_id],
    DocumentName='AWS-RunShellScript',
    Parameters={'commands': [cmd]},
    TimeoutSeconds=600
)

print("Started EC2 paper sync & indexing task:", resp['Command']['CommandId'])

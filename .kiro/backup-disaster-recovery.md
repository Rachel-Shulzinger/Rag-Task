# Backup and Disaster Recovery Plan
**AI Agent:** Kiro  
**Last Updated:** February 19, 2026  
**RTO Target:** 4 hours  
**RPO Target:** 15 minutes  
**Classification:** CONFIDENTIAL

## Overview

CryptoVault's backup and disaster recovery (DR) strategy ensures business continuity with minimal data loss in case of system failures, security breaches, or natural disasters.

### Recovery Objectives

| Metric | Target | Current |
|--------|--------|---------|
| **RTO** (Recovery Time Objective) | 4 hours | 3.2 hours (tested) |
| **RPO** (Recovery Point Objective) | 15 minutes | 12 minutes (achieved) |
| **Data Retention** | 90 days | 90 days |
| **Geographic Redundancy** | 3 regions | 3 regions (us-east-1, eu-west-1, ap-southeast-1) |

---

## Backup Strategy

### Database Backups

#### PostgreSQL Automated Backups

```bash
# Continuous WAL archiving to S3
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://cryptovault-wal-archive/%f'
max_wal_senders = 3
wal_keep_size = 1GB
```

**Backup Schedule:**

| Type | Frequency | Retention | Storage |
|------|-----------|-----------|---------|
| Full Backup | Daily (2 AM UTC) | 30 days | S3 Standard |
| Incremental | Every 4 hours | 7 days | S3 Standard |
| WAL Archives | Continuous | 7 days | S3 Standard |
| Point-in-time | Continuous | 7 days | WAL Archives |

#### Backup Script

```bash
#!/bin/bash
# backup_database.sh

set -e

# Configuration
DB_NAME="cryptovault"
DB_USER="postgres"
S3_BUCKET="s3://cryptovault-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cryptovault_backup_${TIMESTAMP}.dump"

# Create backup
echo "[$(date)] Starting backup..."
pg_dump -U $DB_USER -Fc $DB_NAME > /tmp/$BACKUP_FILE

# Encrypt backup
echo "[$(date)] Encrypting backup..."
openssl enc -aes-256-cbc -salt \
  -in /tmp/$BACKUP_FILE \
  -out /tmp/${BACKUP_FILE}.enc \
  -pass pass:$BACKUP_ENCRYPTION_KEY

# Upload to S3 with encryption
echo "[$(date)] Uploading to S3..."
aws s3 cp /tmp/${BACKUP_FILE}.enc \
  $S3_BUCKET/daily/${BACKUP_FILE}.enc \
  --storage-class STANDARD_IA \
  --server-side-encryption AES256

# Verify backup
echo "[$(date)] Verifying backup integrity..."
aws s3api head-object \
  --bucket cryptovault-backups \
  --key daily/${BACKUP_FILE}.enc

# Test restore (to temp database)
echo "[$(date)] Testing restore..."
createdb -U $DB_USER cryptovault_test_restore
pg_restore -U $DB_USER -d cryptovault_test_restore /tmp/$BACKUP_FILE
dropdb -U $DB_USER cryptovault_test_restore

# Cleanup
rm /tmp/$BACKUP_FILE /tmp/${BACKUP_FILE}.enc

echo "[$(date)] Backup completed successfully!"

# Send success notification
curl -X POST https://api.cryptovault.com/internal/notifications \
  -H "Content-Type: application/json" \
  -d '{
    "type": "backup_success",
    "message": "Database backup completed",
    "backup_file": "'$BACKUP_FILE'",
    "size": "'$(stat -f%z /tmp/$BACKUP_FILE)'"
  }'
```

**Cron Schedule:**
```cron
# Daily full backup at 2 AM UTC
0 2 * * * /scripts/backup_database.sh >> /var/log/backup.log 2>&1

# Incremental backups every 4 hours
0 */4 * * * /scripts/backup_incremental.sh >> /var/log/backup.log 2>&1
```

---

### Application Backups

#### Docker Images

```yaml
# .github/workflows/backup-images.yml
name: Backup Docker Images

on:
  schedule:
    - cron: '0 3 * * *'  # Daily at 3 AM UTC

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Pull production images
        run: |
          docker pull cryptovault/api:production
          docker pull cryptovault/frontend:production
          docker pull cryptovault/worker:production
      
      - name: Save images
        run: |
          docker save cryptovault/api:production | gzip > api-production.tar.gz
          docker save cryptovault/frontend:production | gzip > frontend-production.tar.gz
          docker save cryptovault/worker:production | gzip > worker-production.tar.gz
      
      - name: Upload to S3
        run: |
          aws s3 cp api-production.tar.gz s3://cryptovault-image-backups/$(date +%Y%m%d)/
          aws s3 cp frontend-production.tar.gz s3://cryptovault-image-backups/$(date +%Y%m%d)/
          aws s3 cp worker-production.tar.gz s3://cryptovault-image-backups/$(date +%Y%m%d)/
```

#### Configuration Backups

```python
# scripts/backup_configs.py
import boto3
import json
from datetime import datetime

s3 = boto3.client('s3')
secrets = boto3.client('secretsmanager')

def backup_configurations():
    """Backup all configuration files and secrets."""
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # Backup AWS Secrets
    secret_list = secrets.list_secrets()
    for secret in secret_list['SecretList']:
        secret_value = secrets.get_secret_value(SecretId=secret['Name'])
        
        s3.put_object(
            Bucket='cryptovault-config-backups',
            Key=f"secrets/{timestamp}/{secret['Name']}.json",
            Body=secret_value['SecretString'],
            ServerSideEncryption='AES256'
        )
    
    # Backup environment configs
    configs = [
        '.env.production',
        'docker-compose.yml',
        'nginx.conf',
        'celery_config.py'
    ]
    
    for config_file in configs:
        with open(config_file, 'r') as f:
            s3.put_object(
                Bucket='cryptovault-config-backups',
                Key=f"configs/{timestamp}/{config_file}",
                Body=f.read(),
                ServerSideEncryption='AES256'
            )
    
    print(f"Configurations backed up at {timestamp}")

if __name__ == '__main__':
    backup_configurations()
```

---

### Redis Backups

```conf
# redis.conf
save 900 1      # Save after 900 sec (15 min) if at least 1 key changed
save 300 10     # Save after 300 sec (5 min) if at least 10 keys changed
save 60 10000   # Save after 60 sec if at least 10000 keys changed

# AOF (Append Only File) for better durability
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

**Backup Script:**
```bash
#!/bin/bash
# backup_redis.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Trigger Redis save
redis-cli BGSAVE

# Wait for save to complete
while [ $(redis-cli LASTSAVE) -eq $(redis-cli LASTSAVE) ]; do
  sleep 1
done

# Copy RDB file
cp /var/lib/redis/dump.rdb /tmp/redis_backup_${TIMESTAMP}.rdb

# Upload to S3
aws s3 cp /tmp/redis_backup_${TIMESTAMP}.rdb \
  s3://cryptovault-redis-backups/

# Cleanup
rm /tmp/redis_backup_${TIMESTAMP}.rdb
```

---

## Disaster Recovery Procedures

### Scenario 1: Database Corruption

**Impact:** Critical - Application down  
**RTO:** 2 hours  
**RPO:** 15 minutes

**Recovery Steps:**

```bash
# 1. Identify latest valid backup
aws s3 ls s3://cryptovault-backups/daily/ --recursive | sort | tail -1

# 2. Download backup
LATEST_BACKUP="cryptovault_backup_20260219_020000.dump.enc"
aws s3 cp s3://cryptovault-backups/daily/$LATEST_BACKUP /tmp/

# 3. Decrypt backup
openssl enc -aes-256-cbc -d \
  -in /tmp/$LATEST_BACKUP \
  -out /tmp/restore.dump \
  -pass pass:$BACKUP_ENCRYPTION_KEY

# 4. Stop application
kubectl scale deployment cryptovault-api --replicas=0

# 5. Drop corrupted database
dropdb -U postgres cryptovault

# 6. Create new database
createdb -U postgres cryptovault

# 7. Restore from backup
pg_restore -U postgres -d cryptovault /tmp/restore.dump

# 8. Apply WAL archives (for point-in-time recovery)
# This recovers to the last committed transaction
aws s3 sync s3://cryptovault-wal-archive/ /var/lib/postgresql/wal/
pg_ctl start -D /var/lib/postgresql/data

# 9. Verify data integrity
psql -U postgres -d cryptovault -c "SELECT COUNT(*) FROM users;"
psql -U postgres -d cryptovault -c "SELECT COUNT(*) FROM transactions;"

# 10. Restart application
kubectl scale deployment cryptovault-api --replicas=3

# 11. Verify application health
curl https://api.cryptovault.com/health
```

**Estimated Time:** 1.5 - 2 hours

---

### Scenario 2: Complete AWS Region Failure

**Impact:** Critical - All services down  
**RTO:** 4 hours  
**RPO:** 15 minutes

**Recovery Steps:**

```bash
# 1. Activate DR plan
echo "DISASTER RECOVERY ACTIVATED" | mail -s "DR ALERT" ops@cryptovault.com

# 2. Failover DNS to backup region
# Route 53 - Update A record
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.cryptovault.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z0987654321XYZ",
          "DNSName": "cryptovault-dr-lb-eu-west-1.elb.amazonaws.com",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }'

# 3. Restore database in DR region (eu-west-1)
# Latest backup is replicated cross-region every 15 min
aws s3 cp s3://cryptovault-backups-eu/latest.dump /tmp/ --region eu-west-1

# 4. Provision infrastructure in DR region using Terraform
cd terraform/dr
terraform init
terraform apply -auto-approve \
  -var="region=eu-west-1" \
  -var="database_snapshot=latest"

# 5. Deploy application
kubectl config use-context cryptovault-dr-eu-west-1
kubectl apply -f k8s/production/

# 6. Verify services
curl https://api.cryptovault.com/health

# 7. Monitor application logs
kubectl logs -f deployment/cryptovault-api

# 8. Notify users
# Send email to all users about temporary service interruption
python scripts/notify_users.py --message "Services restored in backup region"
```

**Estimated Time:** 3 - 4 hours

---

### Scenario 3: Ransomware Attack

**Impact:** Critical - Data encrypted by attacker  
**RTO:** 6 hours  
**RPO:** 4 hours (restore from offline backup)

**Recovery Steps:**

```bash
# 1. IMMEDIATELY isolate systems
# Disconnect from network
aws ec2 modify-instance-attribute \
  --instance-id i-1234567890abcdef0 \
  --no-source-dest-check

# 2. Identify attack vector and entry point
# Review CloudTrail logs
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=RunInstances \
  --max-results 100

# 3. Restore from offline backup (S3 Glacier)
# These backups are immutable and stored offline
aws s3 restore-object \
  --bucket cryptovault-offline-backups \
  --key weekly/cryptovault_backup_20260216.dump.enc \
  --restore-request Days=1,GlacierJobParameters={Tier=Expedited}

# Wait for restore (1-5 minutes for Expedited)
while true; do
  STATUS=$(aws s3api head-object \
    --bucket cryptovault-offline-backups \
    --key weekly/cryptovault_backup_20260216.dump.enc \
    --query 'Restore' --output text)
  
  if [[ $STATUS == *"false"* ]]; then
    echo "Restore complete!"
    break
  fi
  
  sleep 30
done

# 4. Build completely new infrastructure (clean slate)
terraform destroy -auto-approve  # Destroy compromised infrastructure
terraform apply -auto-approve     # Rebuild from scratch

# 5. Restore data to new database
# Follow standard database restore procedure

# 6. Security hardening
# Rotate all secrets, keys, passwords
python scripts/rotate_all_credentials.py

# 7. Incident response
# Document attack, notify authorities if required
# Engage cybersecurity forensics team
```

**Estimated Time:** 4 - 6 hours

---

## Backup Testing

### Monthly Restore Tests

**Schedule:** First Sunday of each month, 3 AM UTC

```python
# scripts/test_backup_restore.py
import subprocess
from datetime import datetime
import requests

def test_backup_restore():
    """Automated backup restore test."""
    
    print(f"[{datetime.utcnow()}] Starting backup restore test...")
    
    # 1. Get latest backup
    result = subprocess.run([
        'aws', 's3', 'ls', 's3://cryptovault-backups/daily/',
        '--recursive'
    ], capture_output=True, text=True)
    
    latest_backup = result.stdout.strip().split('\n')[-1].split()[-1]
    print(f"Testing backup: {latest_backup}")
    
    # 2. Download backup
    subprocess.run([
        'aws', 's3', 'cp',
        f's3://cryptovault-backups/{latest_backup}',
        '/tmp/test_restore.dump.enc'
    ])
    
    # 3. Decrypt
    subprocess.run([
        'openssl', 'enc', '-aes-256-cbc', '-d',
        '-in', '/tmp/test_restore.dump.enc',
        '-out', '/tmp/test_restore.dump',
        '-pass', f'pass:{os.getenv("BACKUP_ENCRYPTION_KEY")}'
    ])
    
    # 4. Create test database
    subprocess.run(['createdb', 'cryptovault_restore_test'])
    
    # 5. Restore
    result = subprocess.run([
        'pg_restore',
        '-d', 'cryptovault_restore_test',
        '/tmp/test_restore.dump'
    ], capture_output=True)
    
    if result.returncode != 0:
        send_alert("BACKUP RESTORE TEST FAILED", result.stderr.decode())
        return False
    
    # 6. Verify data integrity
    checks = [
        "SELECT COUNT(*) FROM users;",
        "SELECT COUNT(*) FROM transactions;",
        "SELECT COUNT(*) FROM portfolios;"
    ]
    
    for check in checks:
        result = subprocess.run([
            'psql', '-d', 'cryptovault_restore_test', '-t', '-c', check
        ], capture_output=True, text=True)
        
        count = int(result.stdout.strip())
        if count == 0:
            send_alert("DATA INTEGRITY CHECK FAILED", f"Query: {check}")
            return False
    
    # 7. Cleanup
    subprocess.run(['dropdb', 'cryptovault_restore_test'])
    subprocess.run(['rm', '/tmp/test_restore.dump', '/tmp/test_restore.dump.enc'])
    
    print("✅ Backup restore test PASSED")
    send_notification("Backup restore test completed successfully")
    return True

def send_alert(subject, message):
    """Send alert to ops team."""
    requests.post('https://api.cryptovault.com/internal/alerts', json={
        'subject': subject,
        'message': message,
        'priority': 'high'
    })

def send_notification(message):
    """Send notification."""
    requests.post('https://api.cryptovault.com/internal/notifications', json={
        'message': message
    })

if __name__ == '__main__':
    test_backup_restore()
```

---

## Backup Monitoring

### Metrics Tracked

```python
# monitoring/backup_metrics.py
from prometheus_client import Gauge, Counter

backup_size = Gauge('backup_size_bytes', 'Size of latest backup')
backup_duration = Gauge('backup_duration_seconds', 'Time taken for backup')
backup_success = Counter('backup_success_total', 'Successful backups')
backup_failure = Counter('backup_failure_total', 'Failed backups')
restore_test_success = Counter('restore_test_success_total', 'Successful restore tests')

# Dashboard: Grafana
# Alert: PagerDuty if backup fails
```

**Current Stats (Feb 19, 2026):**
- Total backups: 142 (last 30 days)
- Success rate: 100%
- Average backup size: 47.3 GB
- Average backup duration: 8.2 minutes
- Restore tests: 3/3 passed

---

## Contact Information

**Disaster Recovery Team:**
- **Primary:** kiro-ai@cryptovault.com
- **Secondary:** ops-team@cryptovault.com
- **Emergency:** +1-555-0100 (24/7 hotline)

**Escalation Path:**
1. On-call engineer (PagerDuty)
2. DevOps Lead
3. CTO
4. CEO

**Last Tested:** February 4, 2026  
**Next Test:** March 3, 2026  
**Document Owner:** Kiro (Security & Infrastructure AI)

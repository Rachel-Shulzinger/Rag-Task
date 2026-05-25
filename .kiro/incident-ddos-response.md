# Incident Response - DDoS Attack (Feb 10, 2026)
**AI Agent:** Kiro  
**Incident ID:** INC-2026-002  
**Severity:** HIGH 🔴  
**Status:** RESOLVED ✅  
**Duration:** 3 hours 24 minutes

## Timeline

### Detection (10:15 UTC)
- **Alert triggered:** Abnormal traffic spike detected
- **Monitoring:** DataDog alerts: 15,000+ req/s (normal: ~500 req/s)
- **Initial symptoms:**
  - API response times increased from 85ms → 3,200ms
  - Error rate spiked to 12%
  - Databctions exhausted (100/100)

### Investigation (10:17-10:30 UTC)

**Analysis by Kiro:**
```
Request pattern analysis:
- 87% of traffic from 234 IP addresses
- All requests hitting /api/market/prices endpoint
- User-Agent: Mix of legitimate browsers (spoofed)
- Request rate: ~60 req/s per IP
- Geographic distribution: Botnet (23 countries)

Conclusion: Distributed Denial of Service (DDoS) attack
```

**Traffic Sample:**
```
10:15:23 203.0.113.42 GET /api/market/prices HTTP/1.1 200 45ms
10:15:23 203.0.113.42 GET /api/market/prices HTTP/1.1 200 46ms
10:15:23 203.0.113.42 GET /api/market/prices HTTP/1.1 200 47ms
[... 57 more requests in same second ...]
```

---

### Response Actions

#### Immediate Actions (10:18-10:25 UTC)

**1. Enable Rate Limiting**
```python
# Applied emergency rate limit
@limiter.limit("10/minute", override_defaults=True)
@router.get("/api/market/prices")
async def get_market_prices():
    pass
```

**Impact:** Reduced attack effectiveness by 40%

**2. CloudFlare "Under Attack" Mode**
```bash
# Enabled via CLI
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/security_level" \
  -H "Authorization: Bearer ${CF_TOKEN}" \
  -d '{"value":"under_attack"}'
```

**Impact:**
- JavaScript challenge added
- Blocked 82% of malicious traffic
- Legitimate users experienced 5-second delay

**3. IP Blocking**
```nginx
# Added to Nginx config
geo $blocked_ip {
    default 0;
    203.0.113.0/24 1;
    198.51.100.0/24 1;
    # ... 18 more suspicious ranges
}

server {
    if ($blocked_ip) {
        return 403;
    }
}
```

---

#### Scaling Actions (10:25-10:40 UTC)

**4. Horizontal Scaling**
```bash
# Increased ECS task count
aws ecs update-service \
  --cluster cryptovault-cluster \
  --service cryptovault-api \
  --desired-count 12  # from 3

# Increased RDS read replicas
aws rds create-db-instance-read-replica \
  --db-instance-identifier cryptovault-read-2 \
  --source-db-instance-identifier cryptovault-primary
```

**Impact:**
- Capacity increased 4x
- Response times improved: 3,200ms → 420ms

**5. Database Connection Pool Adjustment**
```python
# Temporary increase
engine = create_async_engine(
    DATABASE_URL,
    pool_size=50,      # from 20
    max_overflow=30,   # from 10
)
```

---

#### Advanced Mitigation (10:40-11:15 UTC)

**6. Deployed WAF Rules**

```json
{
  "Name": "DDoS-Protection-Rule",
  "Priority": 1,
  "Statement": {
    "RateBasedStatement": {
      "Limit": 2000,
      "AggregateKeyType": "IP"
    }
  },
  "Action": {
    "Block": {
      "CustomResponse": {
        "ResponseCode": 429,
        "CustomResponseBodyKey": "rate-limit-exceeded"
      }
    }
  }
}
```

**7. Implemented CAPTCHA for Suspicious Traffic**

```typescript
// Frontend - Added hCaptcha for high-traffic periods
import HCaptcha from '@hcaptcha/react-hcaptcha';

function MarketPrices() {
  const [captchaToken, setCaptchaToken] = useState('');
  
  if (underAttack && !captchaToken) {
    return (
      <HCaptcha
        sitekey="your-hcaptcha-sitekey"
        onVerify={(token) => setCaptchaToken(token)}
      />
    );
  }
  
  // Normal component
}
```

---

### Recovery (11:15-13:39 UTC)

**Traffic Normalization:**
```
Time    | Requests/s | Error Rate | Avg Response Time
--------|------------|------------|------------------
10:15   | 15,234     | 12.3%      | 3,200ms
10:30   | 8,456      | 4.2%       | 420ms
11:00   | 2,134      | 1.1%       | 180ms
11:30   | 892        | 0.3%       | 95ms
12:00   | 534        | 0.05%      | 87ms ← Normal
```

**All-Clear Declared:** 13:39 UTC

---

## Impact Assessment

### Service Availability

| Metric | Impact |
|--------|--------|
| Total downtime | 0 minutes (service remained online) |
| Degraded performance window | 3 hours 24 minutes |
| Users affected | ~12,000 (experienced slow response) |
| Transactions blocked | 0 (all completed, some delayed) |
| Data loss | None |
| Financial impact | $0 (no lost transactions) |

### Resource Costs

| Resource | Normal Cost | Attack Period | Additional |
|----------|-------------|---------------|------------|
| ECS tasks | $45/day | $128/day | +$83 |
| RDS | $120/day | $145/day | +$25 |
| CloudFlare | $200/mo | $200/mo | $0 |
| **Total** | | | **+$108** |

---

## Root Cause Analysis

### Attack Vector

**Type:** HTTP Flood DDoS  
**Method:** Distributed botnet (234 unique IPs)  
**Target:** Public API endpoint (`/api/market/prices`)  
**Sophistication:** Medium
- Rotating User-Agents
- Realistic request patterns
- Distributed geographically

### Vulnerabilities Exploited

1. **No rate limiting on public endpoints**
   - Public endpoints assumed low traffic
   - Assumption: Invalid

2. **Insufficient connection pool**
   - Database connections: 20 (too low for spike)
   - Redis connections: 50 (adequate)

3. **No DDoS-specific WAF rules**
   - CloudFlare enabled but not configured for DDoS
   - AWS WAF not deployed

---

## Lessons Learned

### What Went Well ✅

1. **Fast detection** - Alert triggered within seconds
2. **Effective response** - Service never went completely down
3. **Good communication** - Team coordinated well
4. **Monitoring** - Had visibility into all metrics

### What Could Improve ⚠️

1. **Prevention** - Should have had DDoS protection before attack
2. **Automation** - Manual scaling was slow
3. **Documentation** - Runbook was outdated
4. **Testing** - Never tested DDoS response

---

## Remediation Actions

### Immediate (Completed) ✅

- [x] Deploy AWS WAF with DDoS rules
- [x] Implement rate limiting on ALL endpoints
- [x] Increase database connection pool
- [x] Add CAPTCHA for high-risk endpoints
- [x] Document incident response procedure

### Short-term (Next 2 weeks)

- [ ] Set up AWS Shield Advanced
- [ ] Implement auto-scaling triggers for traffic spikes
- [ ] Add geographic rate limiting
- [ ] Create DDoS simulation test
- [ ] Train team on incident response

### Long-term (Next quarter)

- [ ] Implement CDN for all static assets
- [ ] Deploy edge computing for API requests
- [ ] Add anomaly detection ML model
- [ ] Quarterly DDoS drills

---

## Updated Runbook

### DDoS Attack Response

**Detection Criteria:**
- Traffic spike >5x normal
- Error rate >5%
- Response time >1000ms
- Multiple alerts from different sources

**Response Steps:**

1. **Confirm Attack (< 2 min)**
   ```bash
   # Check traffic distribution
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ApplicationELB \
     --metric-name RequestCount \
     --dimensions Name=LoadBalancer,Value=app/cryptovault-alb \
     --start-time $(date -u -d '10 minutes ago' +%Y-%m-%dT%H:%M:%S) \
     --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
     --period 60 \
     --statistics Sum
   ```

2. **Enable CloudFlare Under Attack Mode (< 1 min)**
   ```bash
   curl -X PATCH "https://api.cloudflare.com/client/v4/zones/${ZONE_ID}/settings/security_level" \
     -H "Authorization: Bearer ${CF_TOKEN}" \
     -d '{"value":"under_attack"}'
   ```

3. **Scale Infrastructure (< 5 min)**
   ```bash
   # Auto-scale ECS
   aws ecs update-service \
     --cluster cryptovault-cluster \
     --service cryptovault-api \
     --desired-count 12
   ```

4. **Analyze and Block (< 10 min)**
   - Identify attack IPs
   - Add to WAF block list
   - Enable CAPTCHA if needed

5. **Monitor and Adjust (ongoing)**
   - Watch CloudWatch metrics
   - Adjust rate limits as needed
   - Communicate with users

---

## Communication

### Internal Notification (10:16 UTC)

**Slack #incidents:**
```
🚨 INCIDENT: DDoS attack detected
Severity: HIGH
Impact: API response times degraded
Status: Investigating
Incident Lead: @kiro-ai
War Room: https://zoom.us/j/incident-002
```

### Customer Communication

**Status Page Update (10:45 UTC):**
```
⚠️ Degraded Performance - API

We are currently experiencing higher than normal traffic 
which is causing slower API response times. Our team is 
actively working to mitigate the issue.

Next update: 11:15 UTC
```

**Resolution (13:40 UTC):**
```
✅ Resolved - API Performance

All systems are now operating normally. API response times 
have returned to normal levels.

We apologize for any inconvenience.
```

---

## Metrics and Graphs

### Traffic During Attack

```
Requests/sec
   │
16k│     ██
   │    ████
12k│   ██████
   │  ████████
 8k│ ██████████
   │████████████
 4k│██████████████
   │██████████████████
   └─────────────────── Time
   10:00  10:30  11:00  11:30  12:00
```

### Response Time

```
Milliseconds
   │
3k │  █
   │  █
2k │  ██
   │  ███
1k │  ████
   │  █████
 0 │████████████████
   └─────────────────── Time
   10:00  10:30  11:00  11:30  12:00
```

---

**Incident Lead:** Kiro AI  
**Post-Mortem Review:** February 11, 2026  
**Attendees:** CTO, DevOps Team, Security Team  
**Next Review:** March 11, 2026

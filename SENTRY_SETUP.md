# Sentry Integration Guide

Complete guide for setting up Sentry error tracking and performance monitoring in the GenAI Coach Backend.

## What is Sentry?

Sentry provides real-time error tracking, performance monitoring, and detailed debugging information for your application. It helps you:

- **Track Errors**: Capture exceptions with full stack traces
- **Monitor Performance**: Track slow API endpoints and database queries
- **Debug Issues**: See breadcrumbs leading up to errors
- **User Context**: Know which users are affected by issues
- **Alerting**: Get notified when issues occur

## Step 1: Create Sentry Project

### 1.1 Sign Up for Sentry

1. Go to [sentry.io](https://sentry.io)
2. Sign up for free account (Free tier includes 5,000 errors/month)
3. Create a new organization or use existing one

### 1.2 Create Python Project

1. Click "Create Project"
2. Select **Python** as the platform
3. Enter project name: `genai-coach-backend`
4. Choose alert frequency
5. Click "Create Project"

### 1.3 Get Your DSN

After project creation, you'll see a DSN (Data Source Name) like:
```
https://examplePublicKey@o0.ingest.sentry.io/0
```

**Save this DSN** - you'll need it for configuration.

## Step 2: Configure Environment Variables

Add Sentry configuration to your `.env` file:

```bash
# Sentry Configuration
SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
SENTRY_ENVIRONMENT=development  # or production, staging, etc.
SENTRY_TRACES_SAMPLE_RATE=1.0   # 1.0 = 100% of transactions
SENTRY_PROFILES_SAMPLE_RATE=1.0 # 1.0 = 100% of profiles
```

### Environment-Specific Configuration

**Development:**
```bash
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0   # Track all requests
SENTRY_PROFILES_SAMPLE_RATE=1.0 # Profile all requests
```

**Production:**
```bash
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1   # Track 10% of requests (reduce costs)
SENTRY_PROFILES_SAMPLE_RATE=0.1 # Profile 10% of requests
```

**To disable Sentry:**
```bash
SENTRY_DSN=  # Leave empty
```

## Step 3: Verify Installation

### 3.1 Test Error Tracking

Add this test endpoint to verify Sentry is working:

```python
@app.get("/sentry-debug")
async def trigger_error():
    """Test endpoint to trigger Sentry error."""
    division_by_zero = 1 / 0
```

Access: `http://localhost:8000/sentry-debug`

You should see the error in your Sentry dashboard within seconds.

### 3.2 Check Sentry Dashboard

1. Go to your Sentry dashboard
2. Navigate to **Issues**
3. You should see the ZeroDivisionError

## Step 4: What's Being Tracked

### Automatic Error Tracking

All unhandled exceptions are automatically captured:

- **API Errors**: HTTP 500 errors
- **Database Errors**: SQLAlchemy exceptions
- **Validation Errors**: Pydantic validation failures (optional)
- **External API Errors**: OpenAI API failures

### Performance Monitoring

Track performance of key operations:

- **HTTP Requests**: All API endpoint requests
- **Database Queries**: SQL query performance
- **AI Operations**: OpenAI API calls (chat, transcription, feedback)
- **S3 Operations**: File downloads from S3

### User Context

For authenticated requests, Sentry captures:
- User ID
- User email
- User name

### Request Context

- HTTP method and URL
- Request headers
- Query parameters
- Request body (with sensitive data filtered)
- Client IP address

### Custom Breadcrumbs

Track user actions leading to errors:
- Authentication events
- AI service calls
- Database operations
- File uploads

## Step 5: Using Sentry in Code

### Manual Error Capture

```python
from app.core.sentry import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(
        e,
        tags={"service": "payment", "action": "process"},
        extra={"order_id": "12345", "amount": 99.99},
        user={"id": user.id, "email": user.email}
    )
    raise
```

### Manual Message Capture

```python
from app.core.sentry import capture_message

capture_message(
    "User attempted invalid operation",
    level="warning",
    tags={"operation": "delete_account"},
    extra={"user_id": user.id}
)
```

### Performance Tracking

```python
from app.core.sentry import start_transaction, start_span

# Track entire operation
with start_transaction("process_payment", op="payment.process"):
    # Track sub-operations
    with start_span("payment.validate", "Validate payment"):
        validate_payment(data)

    with start_span("payment.charge", "Charge card"):
        charge_result = charge_card(data)
```

### Set User Context

```python
from app.core.sentry import set_user_context

set_user_context(
    user_id=str(user.id),
    email=user.email,
    name=user.name,
    subscription="premium"
)
```

### Add Breadcrumbs

```python
from app.core.sentry import add_breadcrumb

add_breadcrumb(
    "User clicked checkout button",
    category="user_action",
    level="info",
    data={"cart_total": 149.99, "item_count": 3}
)
```

## Step 6: Filtering Sensitive Data

### Automatic Filtering

The following fields are automatically filtered:
- `password`
- `current_password`
- `new_password`
- `token`
- `refresh_token`
- `access_token`

### Add Custom Filters

Edit `app/core/sentry.py`, modify `before_send_filter`:

```python
def before_send_filter(event, hint):
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            # Add custom fields to filter
            for key in ["credit_card", "ssn", "api_key"]:
                if key in data:
                    data[key] = "[FILTERED]"
    return event
```

## Step 7: Sentry Dashboard Features

### Issues View

**Navigate to**: Issues tab

Shows all errors with:
- Error count
- Affected users
- Last seen
- Stack trace
- Breadcrumbs

**Actions:**
- Mark as resolved
- Assign to team member
- Ignore error
- Create Jira/GitHub issue

### Performance View

**Navigate to**: Performance tab

Shows:
- Transaction throughput
- P95 response times
- Slow endpoints
- Database query performance

**Useful for:**
- Identifying slow API endpoints
- Finding N+1 query problems
- Tracking performance regressions

### Releases

Track errors by deployment:

```bash
# Set release in environment
SENTRY_RELEASE=genai-coach-backend@1.0.0
```

Or use git commit SHA:
```bash
SENTRY_RELEASE=$(git rev-parse --short HEAD)
```

### Alerts

Set up alerts for:
1. Go to **Alerts** > **Create Alert**
2. Choose alert type:
   - Issue: Alert on new/regressed errors
   - Metric: Alert on performance degradation
3. Configure conditions:
   - Error count > 10 in 1 hour
   - P95 response time > 2 seconds
4. Choose notification channel (email, Slack, PagerDuty)

## Step 8: Production Best Practices

### Sample Rates

Adjust sample rates based on traffic:

| Traffic/Month | Traces Sample Rate | Cost Impact |
|---------------|-------------------|-------------|
| < 100K requests | 1.0 (100%) | Low |
| 100K - 1M | 0.1 (10%) | Medium |
| > 1M | 0.01 (1%) | High |

### Release Tracking

```bash
# In deployment script
export SENTRY_RELEASE="genai-coach-backend@$(git rev-parse --short HEAD)"
```

### Source Maps

Enable source context for better debugging:

```python
# In sentry.py init
sentry_sdk.init(
    ...
    attach_stacktrace=True,
    include_local_variables=True,
)
```

### Performance Budget

Set performance budgets:
1. API endpoints: < 500ms P95
2. Database queries: < 100ms
3. External API calls: < 2s

Track these in Sentry Performance tab.

## Step 9: Railway Deployment

### Set Environment Variables

```bash
railway variables set SENTRY_DSN="your-sentry-dsn"
railway variables set SENTRY_ENVIRONMENT="production"
railway variables set SENTRY_TRACES_SAMPLE_RATE="0.1"
railway variables set SENTRY_PROFILES_SAMPLE_RATE="0.1"
```

### Verify Deployment

1. Deploy to Railway
2. Trigger an error: `https://your-app.railway.app/sentry-debug`
3. Check Sentry dashboard for the error

## Step 10: Team Setup

### Invite Team Members

1. Go to **Settings** > **Members**
2. Click "Invite Member"
3. Set permissions:
   - **Admin**: Full access
   - **Member**: Can view and resolve issues
   - **Billing**: Can manage billing only

### Notification Rules

Configure who gets notified:
1. **Settings** > **Notifications**
2. Set rules:
   - Notify on first occurrence
   - Notify on regression
   - Notify on spike (10x increase)

## Troubleshooting

### Issue: Sentry not capturing errors

**Check:**
1. SENTRY_DSN is set correctly
2. Check logs for Sentry initialization message
3. Verify network connectivity
4. Check sample rate (set to 1.0 for testing)

### Issue: Too many events (quota exceeded)

**Solutions:**
1. Reduce `SENTRY_TRACES_SAMPLE_RATE`
2. Filter noisy errors in `before_send_filter`
3. Upgrade Sentry plan
4. Use error grouping/ignoring features

### Issue: Missing user context

**Check:**
1. User context is set in `get_current_user` dependency
2. Check middleware order (Sentry before error handler)
3. Verify authentication is working

### Issue: Sensitive data in events

**Solution:**
1. Add fields to `before_send_filter`
2. Use `send_default_pii=False` (disables automatic PII)
3. Review captured data regularly

## Cost Optimization

### Free Tier Limits

- 5,000 errors/month
- 10,000 performance units/month
- 90-day retention

### Tips to Stay in Free Tier

1. **Filter health checks**: Don't track `/health` endpoint
2. **Sample aggressively**: Use 0.1 sample rate in production
3. **Filter validation errors**: Don't send 422 errors to Sentry
4. **Ignore known issues**: Mark recurring non-critical errors as ignored
5. **Delete test data**: Regularly clean up test errors

### Upgrade Plans

| Plan | Price | Errors | Performance |
|------|-------|--------|-------------|
| Developer | Free | 5K | 10K units |
| Team | $26/mo | 50K | 100K units |
| Business | $80/mo | 200K | 1M units |

## Sentry Integrations

### Slack Integration

Get errors in Slack:
1. **Settings** > **Integrations** > **Slack**
2. Connect Slack workspace
3. Choose channel
4. Configure alert rules

### GitHub Integration

Create issues from errors:
1. **Settings** > **Integrations** > **GitHub**
2. Connect GitHub account
3. Link repository
4. Create issues directly from Sentry

### Jira Integration

Track errors in Jira:
1. **Settings** > **Integrations** > **Jira**
2. Connect Jira account
3. Create tickets from Sentry issues

## Metrics to Track

### Error Metrics

- Error count (hourly/daily)
- Affected users
- Error rate (errors per request)
- Resolution time

### Performance Metrics

- P50, P95, P99 response times
- Throughput (requests per second)
- Apdex score
- Slow transactions

## Next Steps

1. ✅ Set up Sentry project
2. ✅ Configure environment variables
3. ✅ Verify error tracking works
4. ✅ Review captured data
5. ✅ Set up alerts
6. ✅ Invite team members
7. ✅ Configure integrations (Slack, GitHub)
8. ✅ Set performance budgets
9. ✅ Review and filter sensitive data
10. ✅ Optimize sample rates for cost

## Resources

- [Sentry Python Documentation](https://docs.sentry.io/platforms/python/)
- [FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Sentry Best Practices](https://docs.sentry.io/product/best-practices/)

---

**Questions or Issues?**

- Check [Sentry Docs](https://docs.sentry.io)
- Join [Sentry Discord](https://discord.gg/sentry)
- Review backend logs for initialization errors

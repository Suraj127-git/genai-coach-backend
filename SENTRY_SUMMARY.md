# Sentry Integration Summary

## Overview

Comprehensive Sentry error tracking and performance monitoring has been integrated throughout the GenAI Coach Backend API.

## What's Been Integrated

### ✅ Core Integration

- **Sentry SDK**: Added `sentry-sdk[fastapi]==2.17.0` to requirements
- **Configuration**: Environment variables for DSN, sample rates, and environment
- **Initialization**: Auto-initializes on application startup
- **Middleware**: Custom middleware for request context and user tracking

### ✅ Error Tracking

**Automatic:**
- All unhandled exceptions captured automatically
- Database errors (SQLAlchemy)
- HTTP exceptions (FastAPI)
- External API failures (OpenAI, S3)

**Manual:**
- Helper functions for explicit error capture
- Tagged and categorized errors
- User context attached to errors

### ✅ Performance Monitoring

**Tracked Operations:**
- HTTP request/response times
- Database query performance
- AI service calls (GPT-4, Whisper)
- S3 file operations

**Spans:**
- Nested transaction tracking
- Operation-level performance data
- Custom span creation available

### ✅ User Context

Automatically captures for authenticated requests:
- User ID
- User email
- User name
- Authentication events

### ✅ Breadcrumbs

Tracks user journey:
- Authentication attempts
- API endpoint calls
- AI service interactions
- Database operations
- File uploads

### ✅ Sensitive Data Filtering

Auto-filtered fields:
- `password`, `current_password`, `new_password`
- `token`, `refresh_token`, `access_token`
- Custom filters extendable

## Files Modified/Created

### New Files:
1. `app/core/sentry.py` - Complete Sentry integration module
2. `app/middleware/sentry_middleware.py` - Request context middleware
3. `app/api/endpoints/debug.py` - Test endpoints for Sentry
4. `SENTRY_SETUP.md` - Complete setup guide
5. `SENTRY_SUMMARY.md` - This file

### Modified Files:
1. `requirements.txt` - Added sentry-sdk
2. `app/core/config.py` - Added Sentry configuration
3. `app/main.py` - Initialized Sentry
4. `app/middleware/error_handler.py` - Added Sentry error capture
5. `app/services/ai_service.py` - Added performance tracking
6. `app/api/deps.py` - Added user context tracking
7. `.env.example` - Added Sentry variables

## Quick Start

### 1. Get Sentry DSN

```bash
# Sign up at https://sentry.io
# Create Python project
# Copy your DSN
```

### 2. Configure Environment

```bash
# Add to .env
SENTRY_DSN=https://your-key@sentry.io/your-project-id
SENTRY_ENVIRONMENT=development
SENTRY_TRACES_SAMPLE_RATE=1.0
```

### 3. Test Integration

```bash
# Start server
uvicorn app.main:app --reload

# Test error tracking
curl http://localhost:8000/debug/sentry-test-error

# Check Sentry dashboard
```

## Usage Examples

### Capture Exception

```python
from app.core.sentry import capture_exception

try:
    risky_operation()
except Exception as e:
    capture_exception(
        e,
        tags={"service": "payment"},
        extra={"order_id": "12345"}
    )
```

### Track Performance

```python
from app.core.sentry import start_span

with start_span("db.query", "Fetch user sessions"):
    sessions = await get_user_sessions(user_id)
```

### Add Breadcrumb

```python
from app.core.sentry import add_breadcrumb

add_breadcrumb(
    "User clicked checkout",
    category="user_action",
    data={"cart_total": 99.99}
)
```

### Set User Context

```python
from app.core.sentry import set_user_context

set_user_context(
    user_id=str(user.id),
    email=user.email
)
```

## Test Endpoints

Available in development mode only (`/debug/*`):

| Endpoint | Description |
|----------|-------------|
| `/debug/sentry-status` | Check Sentry configuration |
| `/debug/sentry-test-error` | Trigger unhandled error |
| `/debug/sentry-test-message` | Send test message |
| `/debug/sentry-test-exception` | Capture handled exception |
| `/debug/sentry-test-auth` | Test with user context |

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | `""` | Sentry project DSN (required) |
| `SENTRY_ENVIRONMENT` | `production` | Environment name |
| `SENTRY_TRACES_SAMPLE_RATE` | `1.0` | % of requests to track (0.0-1.0) |
| `SENTRY_PROFILES_SAMPLE_RATE` | `1.0` | % of profiles to capture (0.0-1.0) |

**Production recommendations:**
- `SENTRY_TRACES_SAMPLE_RATE=0.1` (10% of requests)
- `SENTRY_PROFILES_SAMPLE_RATE=0.1` (10% of profiles)

## What Gets Tracked

### Request Context
✅ HTTP method and URL
✅ Request headers
✅ Query parameters
✅ Request body (sensitive data filtered)
✅ Client IP address
✅ User agent

### Performance Data
✅ Response time
✅ Database query duration
✅ External API call duration
✅ File operation duration
✅ Transaction throughput

### Error Data
✅ Full stack trace
✅ Local variables
✅ Exception type and message
✅ Affected users
✅ Error frequency

### User Data
✅ User ID
✅ Email address
✅ User name
✅ Authentication status

## Features

### Automatic
- ✅ All HTTP requests tracked
- ✅ Database query performance
- ✅ Unhandled exception capture
- ✅ Request/response logging
- ✅ User context from JWT

### Manual
- ✅ Custom exception capture
- ✅ Message logging
- ✅ Custom spans/transactions
- ✅ Breadcrumb trails
- ✅ Custom context

### Advanced
- ✅ Sensitive data filtering
- ✅ 404/422 error filtering
- ✅ Health check filtering
- ✅ SQL query sanitization
- ✅ Token usage tracking

## Cost Optimization

### Free Tier (Sufficient for Development)
- 5,000 errors/month
- 10,000 performance units/month
- 90-day retention

### Production Tips
1. **Sample rate**: Use 0.1 (10%) for high-traffic apps
2. **Filter noise**: Exclude health checks and validation errors
3. **Ignore known issues**: Mark recurring non-critical errors as ignored
4. **Group similar errors**: Let Sentry auto-group related issues

## Monitoring Dashboard

### Key Metrics to Watch

**Errors:**
- Error rate (errors per hour)
- New issues vs recurring
- Affected users
- Resolution time

**Performance:**
- P95 response time
- Slow endpoints
- Database query time
- External API latency

## Alerts

Recommended alert setup:

1. **Critical Error Alert**
   - New error > 10 occurrences in 1 hour
   - Notify: Slack/Email

2. **Performance Degradation**
   - P95 response time > 2 seconds
   - Notify: Slack

3. **High Error Rate**
   - Error rate > 5% of requests
   - Notify: Email/PagerDuty

## Integrations

### Slack
Get real-time error notifications in Slack channels.

### GitHub
Create issues directly from Sentry errors.

### Jira
Track errors as Jira tickets.

## Railway Deployment

```bash
# Set environment variables
railway variables set SENTRY_DSN="your-dsn"
railway variables set SENTRY_ENVIRONMENT="production"
railway variables set SENTRY_TRACES_SAMPLE_RATE="0.1"

# Deploy
railway up
```

## Verification

After deployment:

1. ✅ Check startup logs for "Sentry initialized successfully"
2. ✅ Trigger test error: `/debug/sentry-test-error`
3. ✅ Verify error in Sentry dashboard
4. ✅ Check performance data in Sentry

## Next Steps

1. **Set up Sentry account**: [sentry.io](https://sentry.io)
2. **Get project DSN**: Create Python project
3. **Configure environment**: Add SENTRY_DSN to .env
4. **Test integration**: Use debug endpoints
5. **Deploy to production**: Set Railway variables
6. **Configure alerts**: Set up Slack/email notifications
7. **Monitor dashboard**: Review errors and performance

## Support

- **Setup Guide**: See [SENTRY_SETUP.md](SENTRY_SETUP.md)
- **Sentry Docs**: [docs.sentry.io](https://docs.sentry.io/platforms/python/guides/fastapi/)
- **FastAPI Integration**: [sentry.io/fastapi](https://docs.sentry.io/platforms/python/guides/fastapi/)

## Summary

✅ **Error Tracking**: All errors automatically captured
✅ **Performance Monitoring**: Track slow endpoints and queries
✅ **User Context**: Know which users are affected
✅ **Breadcrumbs**: See user journey before errors
✅ **Production Ready**: Optimized for deployment
✅ **Cost Effective**: Free tier sufficient for most apps
✅ **Easy Testing**: Debug endpoints included
✅ **Well Documented**: Complete setup and usage guides

**Your backend is now fully instrumented with Sentry!**

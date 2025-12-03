# Deployment Guide

Complete deployment guide for GenAI Coach Backend to Railway.com

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **AWS Account**: For S3 file storage
3. **OpenAI Account**: For AI services

## Step 1: Prepare AWS S3

### Create S3 Bucket

1. Go to AWS S3 Console
2. Click "Create bucket"
3. Name: `genai-coach-uploads-prod` (must be globally unique)
4. Region: `us-east-1` (or your preferred region)
5. Uncheck "Block all public access" (we'll use presigned URLs)
6. Click "Create bucket"

### Configure CORS

1. Select your bucket
2. Go to "Permissions" tab
3. Scroll to "Cross-origin resource sharing (CORS)"
4. Click "Edit" and paste:

```json
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "GET",
            "PUT",
            "POST",
            "DELETE"
        ],
        "AllowedOrigins": [
            "*"
        ],
        "ExposeHeaders": [
            "ETag"
        ],
        "MaxAgeSeconds": 3000
    }
]
```

### Create IAM User

1. Go to IAM Console
2. Click "Users" → "Add users"
3. Username: `genai-coach-s3-user`
4. Select "Access key - Programmatic access"
5. Click "Next: Permissions"
6. Click "Attach policies directly"
7. Click "Create policy" and use this JSON:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:HeadObject"
            ],
            "Resource": [
                "arn:aws:s3:::genai-coach-uploads-prod/*",
                "arn:aws:s3:::genai-coach-uploads-prod"
            ]
        }
    ]
}
```

8. Name the policy `GenAICoachS3Policy`
9. Attach the policy to your user
10. **Save the Access Key ID and Secret Access Key**

## Step 2: Get OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign in or create account
3. Go to "API keys"
4. Click "Create new secret key"
5. **Save the API key** (you won't see it again)

## Step 3: Deploy to Railway

### Option A: Using Railway CLI (Recommended)

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
# or
brew install railway
```

2. **Login to Railway**
```bash
railway login
```

3. **Navigate to backend directory**
```bash
cd genai-coach-backend
```

4. **Initialize Railway project**
```bash
railway init
```

5. **Add MySQL database**
```bash
railway add
# Select "MySQL" from the list
```

6. **Set environment variables**
```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Set all required variables
railway variables set SECRET_KEY="$SECRET_KEY"
railway variables set AWS_ACCESS_KEY_ID="your-aws-access-key-here"
railway variables set AWS_SECRET_ACCESS_KEY="your-aws-secret-key-here"
railway variables set AWS_REGION="us-east-1"
railway variables set S3_BUCKET_NAME="genai-coach-uploads-prod"
railway variables set OPENAI_API_KEY="your-openai-key-here"
railway variables set ENVIRONMENT="production"
railway variables set DEBUG="False"
railway variables set CORS_ORIGINS="https://your-frontend-domain.com"
```

7. **Deploy**
```bash
railway up
```

8. **Generate domain**
```bash
railway domain
```

9. **View logs**
```bash
railway logs
```

### Option B: Using Railway Dashboard

1. **Create new project**
   - Go to [railway.app/new](https://railway.app/new)
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Select the backend directory

2. **Add MySQL database**
   - Click "+ New"
   - Select "Database"
   - Choose "MySQL"

3. **Configure environment variables**
   - Click on your service
   - Go to "Variables" tab
   - Add these variables:

   ```
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   AWS_ACCESS_KEY_ID=<your-aws-access-key>
   AWS_SECRET_ACCESS_KEY=<your-aws-secret-key>
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=genai-coach-uploads-prod
   OPENAI_API_KEY=<your-openai-key>
   ENVIRONMENT=production
   DEBUG=False
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

4. **Configure build**
   - Go to "Settings" tab
   - Root Directory: `/genai-coach-backend`
   - Build Command: (leave default)
   - Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. **Generate domain**
   - Go to "Settings" tab
   - Click "Generate Domain"
   - Copy the URL (e.g., `https://your-app.up.railway.app`)

6. **Deploy**
   - Railway will automatically deploy on git push
   - Or click "Deploy" button manually

## Step 4: Verify Deployment

### Test Health Endpoint
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{"status": "healthy"}
```

### Test API Documentation
Open in browser:
```
https://your-app.railway.app/docs
```

### Test Authentication
```bash
# Register a user
curl -X POST https://your-app.railway.app/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "name": "Test User"
  }'
```

## Step 5: Update Frontend Configuration

Update your frontend's `.env` file:

```
EXPO_PUBLIC_API_URL=https://your-app.railway.app
EXPO_PUBLIC_API_WS=wss://your-app.railway.app
```

## Step 6: Setup Monitoring

### View Logs
```bash
railway logs --follow
```

### Set up Alerts
1. Go to Railway dashboard
2. Select your project
3. Go to "Observability" tab
4. Configure alerts for:
   - High CPU usage
   - High memory usage
   - Error rate spikes

## Troubleshooting

### Database Connection Issues

**Problem**: `Can't connect to MySQL server`

**Solution**:
1. Check if DATABASE_URL is automatically set by Railway
2. Verify MySQL service is running
3. Check logs: `railway logs`

### Migration Errors

**Problem**: `alembic upgrade head` fails

**Solution**:
1. Check database connection
2. Run migrations manually:
```bash
railway run alembic upgrade head
```

### CORS Errors

**Problem**: Frontend can't connect to API

**Solution**:
1. Verify CORS_ORIGINS includes your frontend domain
2. Update variable:
```bash
railway variables set CORS_ORIGINS="https://frontend.com,https://www.frontend.com"
```

### S3 Upload Errors

**Problem**: Presigned URL generation fails

**Solution**:
1. Verify AWS credentials are correct
2. Check IAM policy permissions
3. Verify S3 bucket exists and name matches
4. Check AWS region matches

### OpenAI API Errors

**Problem**: AI chat or transcription fails

**Solution**:
1. Verify OPENAI_API_KEY is correct
2. Check OpenAI account has credits
3. View detailed error in logs: `railway logs`

## Scaling Considerations

### Vertical Scaling
- Railway automatically scales based on plan
- Upgrade plan for more resources

### Database Optimization
1. Add indexes for frequently queried fields
2. Enable query caching
3. Consider read replicas for high traffic

### Redis Integration (Optional)
Add Redis for caching:
```bash
railway add
# Select Redis

# Update code to use Redis for:
# - Session caching
# - Rate limiting
# - Response caching
```

### CDN for Static Assets
Use CloudFront or Cloudflare for:
- API response caching
- DDoS protection
- Rate limiting

## Security Checklist

- [x] Secure SECRET_KEY (32+ characters)
- [x] Enable HTTPS (Railway provides this)
- [x] Restrict CORS origins to your domains
- [x] Use environment variables for secrets
- [x] Enable rate limiting (add middleware)
- [x] Regular dependency updates
- [x] Monitor error logs
- [x] Setup alerts for suspicious activity

## Backup Strategy

### Database Backups
Railway provides automatic backups. To manual backup:

```bash
# Export database
railway run mysqldump -u root -p genai_coach > backup.sql

# Restore database
railway run mysql -u root -p genai_coach < backup.sql
```

### S3 Versioning
Enable S3 versioning for uploaded files:
1. Go to S3 bucket
2. Properties → Versioning
3. Enable versioning

## Cost Estimation

**Railway Costs** (as of 2024):
- Hobby Plan: $5/month (includes $5 credits)
- Pro Plan: $20/month (includes $20 credits)
- Compute: ~$0.000463/min ($20/month for 24/7)

**AWS S3 Costs**:
- Storage: $0.023/GB/month
- PUT requests: $0.005/1000 requests
- Bandwidth: $0.09/GB (first 10TB)

**OpenAI Costs**:
- GPT-4o-mini: $0.150/1M input tokens, $0.600/1M output tokens
- Whisper: $0.006/minute

**Estimated Monthly Cost** (1000 active users):
- Railway: $20-40
- S3: $5-10
- OpenAI: $50-100
- **Total: ~$75-150/month**

## Production Checklist

Before going live:

- [ ] Set DEBUG=False
- [ ] Configure proper CORS origins
- [ ] Setup error monitoring (Sentry)
- [ ] Enable database backups
- [ ] Setup S3 bucket lifecycle policies
- [ ] Configure rate limiting
- [ ] Add API key authentication for sensitive endpoints
- [ ] Setup logging aggregation
- [ ] Configure health checks
- [ ] Test disaster recovery
- [ ] Document API for frontend team
- [ ] Setup staging environment
- [ ] Load testing
- [ ] Security audit

## Support

For deployment issues:
- Railway Docs: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- GitHub Issues: Open an issue in your repository

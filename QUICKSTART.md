# Quick Start Guide

Get the GenAI Coach Backend running locally in 5 minutes.

## Prerequisites

- Python 3.11+
- MySQL 8.0+ (or use Docker)
- AWS Account + S3 Bucket
- OpenAI API Key

## Option 1: Quick Start with Docker (Recommended)

This is the fastest way to get started:

```bash
# 1. Navigate to backend directory
cd genai-coach-backend

# 2. Copy environment file
cp .env.example .env

# 3. Edit .env and set these required values:
#    - AWS_ACCESS_KEY_ID
#    - AWS_SECRET_ACCESS_KEY
#    - S3_BUCKET_NAME
#    - OPENAI_API_KEY

# 4. Start everything with Docker Compose
docker-compose up -d

# 5. Wait for services to be ready (about 30 seconds)
docker-compose logs -f api

# 6. API is ready when you see: "Application startup complete"
# Access at: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

That's it! Skip to the "Test the API" section below.

## Option 2: Manual Setup (Without Docker)

### Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Setup MySQL Database

```bash
# Start MySQL (if not running)
# macOS with Homebrew:
brew services start mysql

# Linux:
sudo systemctl start mysql

# Create database
mysql -u root -p
```

In MySQL console:
```sql
CREATE DATABASE genai_coach;
CREATE USER 'genai_user'@'localhost' IDENTIFIED BY 'genai_password';
GRANT ALL PRIVILEGES ON genai_coach.* TO 'genai_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with minimum required values:
```env
DATABASE_URL=mysql+aiomysql://genai_user:genai_password@localhost:3306/genai_coach
SECRET_KEY=your-secret-key-change-this-min-32-characters-long
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name
OPENAI_API_KEY=your-openai-key
```

### Step 4: Run Database Migrations

```bash
# Create tables
alembic upgrade head
```

### Step 5: Start the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Test the API

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected response: `{"status":"healthy"}`

### 2. Register a User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "name": "Test User"
  }'
```

You should receive a response with user data and tokens.

### 3. Try the Interactive API Docs

Open in browser: http://localhost:8000/docs

This gives you a Swagger UI to test all endpoints interactively.

## Next Steps

### Create a Test User via Script

```bash
# Creates user: test@example.com / test123
python scripts/create_test_user.py
```

### Test with Frontend

Update your frontend's `.env`:
```env
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_API_WS=ws://localhost:8000
```

### View Logs

Docker:
```bash
docker-compose logs -f api
```

Manual:
```bash
# Logs are printed to console when running uvicorn
```

## Common Issues

### Issue: "Can't connect to MySQL server"

**Solution 1**: Check if MySQL is running
```bash
# macOS
brew services list

# Linux
sudo systemctl status mysql
```

**Solution 2**: Verify credentials in `.env`
```bash
mysql -u genai_user -p
# Enter password: genai_password
```

### Issue: "ModuleNotFoundError"

**Solution**: Activate virtual environment
```bash
source venv/bin/activate  # Must run this first!
pip install -r requirements.txt
```

### Issue: "Table doesn't exist"

**Solution**: Run migrations
```bash
alembic upgrade head
```

### Issue: "Invalid AWS credentials"

**Solution**: Verify AWS credentials
```bash
# Test AWS CLI (if installed)
aws s3 ls s3://your-bucket-name --profile default

# Or verify in .env file
cat .env | grep AWS
```

### Issue: Port 8000 already in use

**Solution**: Kill existing process or use different port
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

## Quick Commands Reference

```bash
# Start development server
uvicorn app.main:app --reload

# Run with custom port
uvicorn app.main:app --port 8001

# Create database migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Create test user
python scripts/create_test_user.py

# Start with Docker
docker-compose up -d

# View Docker logs
docker-compose logs -f

# Stop Docker services
docker-compose down

# Reset database (Docker)
docker-compose down -v
docker-compose up -d
```

## What's Next?

1. **Read the full README.md** for detailed documentation
2. **Check DEPLOYMENT.md** for Railway deployment guide
3. **Explore API docs** at http://localhost:8000/docs
4. **Connect your frontend** and test the full flow

## Getting Help

- Check [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guides
- Review logs for error messages
- Check if all environment variables are set correctly

## Project Structure Quick Reference

```
genai-coach-backend/
├── app/
│   ├── main.py              # Start here - entry point
│   ├── api/endpoints/       # API routes
│   ├── models/              # Database models
│   ├── schemas/             # Request/response schemas
│   └── services/            # Business logic
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
├── .env                     # Configuration (create from .env.example)
└── requirements.txt         # Python dependencies
```

Happy coding!

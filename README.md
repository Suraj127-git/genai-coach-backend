# GenAI Coach Backend

AI-powered mock interview coach backend API built with FastAPI, SQLAlchemy, and MySQL.

## Features

- **Authentication**: JWT-based authentication with access and refresh tokens
- **File Upload**: S3 presigned URL generation for secure file uploads
- **AI Integration**: OpenAI GPT for chat and Whisper for transcription
- **WebSocket**: Real-time transcription support
- **Interview Sessions**: Track and analyze interview practice sessions
- **Feedback Generation**: AI-powered interview feedback with scores

## Tech Stack

- **Framework**: FastAPI 0.115.0
- **Database**: MySQL with SQLAlchemy 2.0 (async)
- **Authentication**: JWT with python-jose
- **File Storage**: AWS S3 with boto3
- **AI Services**: OpenAI GPT-4 and Whisper
- **WebSocket**: Native FastAPI WebSocket support
- **Migrations**: Alembic

## Architecture

This backend follows clean architecture principles with clear separation of concerns:

```
genai-coach-backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependency injection
│   │   └── endpoints/           # API route handlers
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── upload.py        # File upload endpoints
│   │       ├── sessions.py      # Interview session endpoints
│   │       ├── ai.py            # AI chat endpoints
│   │       └── websocket.py     # WebSocket endpoints
│   ├── core/
│   │   ├── config.py            # Application configuration
│   │   ├── security.py          # Security utilities (JWT, password hashing)
│   │   └── logging.py           # Logging configuration
│   ├── db/
│   │   └── base.py              # Database session management
│   ├── models/                  # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── session.py
│   │   └── upload.py
│   ├── schemas/                 # Pydantic schemas for validation
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── upload.py
│   │   └── ai.py
│   ├── services/                # Business logic layer
│   │   ├── user_service.py
│   │   ├── session_service.py
│   │   ├── s3_service.py
│   │   └── ai_service.py
│   ├── middleware/              # Custom middleware
│   │   ├── cors.py
│   │   └── error_handler.py
│   └── main.py                  # Application entry point
├── alembic/                     # Database migrations
├── scripts/                     # Utility scripts
├── tests/                       # Test suite
├── Dockerfile                   # Docker configuration
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment variables template
```

## Design Patterns

1. **Repository Pattern**: Service layer abstracts data access logic
2. **Dependency Injection**: FastAPI's dependency system for clean dependencies
3. **Factory Pattern**: Database session and service creation
4. **Singleton Pattern**: Configuration and service instances
5. **Strategy Pattern**: Multiple AI providers can be swapped

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout user
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile

### Upload
- `POST /upload/s3-presign` - Get S3 presigned URL
- `POST /upload/confirm` - Confirm upload completion

### Sessions
- `POST /sessions` - Create interview session
- `GET /sessions` - List user sessions with stats
- `GET /sessions/{id}` - Get specific session
- `GET /sessions/{id}/feedback` - Get session feedback
- `POST /sessions/{id}/complete` - Complete session and generate feedback

### AI
- `POST /ai/chat` - Send chat message to AI

### WebSocket
- `WS /ws/transcribe` - Real-time transcription WebSocket

## Setup Instructions

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- AWS Account (for S3)
- OpenAI API Key

### Local Development

1. **Clone the repository**
```bash
cd genai-coach-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```
DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/genai_coach
SECRET_KEY=your-secret-key-min-32-chars
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name
OPENAI_API_KEY=your-openai-key
```

5. **Create database**
```bash
mysql -u root -p
CREATE DATABASE genai_coach;
```

6. **Run migrations**
```bash
alembic upgrade head
```

7. **Create test user (optional)**
```bash
python scripts/create_test_user.py
```

8. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migration:
```bash
alembic downgrade -1
```

## Docker Deployment

### Build Docker image
```bash
docker build -t genai-coach-backend .
```

### Run with Docker Compose
```bash
docker-compose up -d
```

## Railway Deployment

### Prerequisites
- Railway account
- Railway CLI installed

### Deployment Steps

1. **Install Railway CLI**
```bash
npm install -g @railway/cli
```

2. **Login to Railway**
```bash
railway login
```

3. **Initialize project**
```bash
railway init
```

4. **Add MySQL plugin**
```bash
railway add
# Select MySQL from the list
```

5. **Set environment variables**
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set AWS_ACCESS_KEY_ID="your-aws-key"
railway variables set AWS_SECRET_ACCESS_KEY="your-aws-secret"
railway variables set S3_BUCKET_NAME="your-bucket"
railway variables set OPENAI_API_KEY="your-openai-key"
```

6. **Deploy**
```bash
railway up
```

Railway will automatically:
- Build the Docker image
- Run database migrations
- Start the application
- Provide a public URL

### Environment Variables for Railway

Railway automatically provides `DATABASE_URL` when you add the MySQL plugin. Set these additional variables:

```
SECRET_KEY=your-secret-key-min-32-chars
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket
OPENAI_API_KEY=your-openai-api-key
CORS_ORIGINS=https://your-frontend-url.com
ENVIRONMENT=production
DEBUG=False
```

### Post-Deployment

1. Check logs:
```bash
railway logs
```

2. Get deployment URL:
```bash
railway domain
```

3. Test the API:
```bash
curl https://your-app.railway.app/health
```

## AWS S3 Setup

1. Create an S3 bucket
2. Configure CORS policy:
```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "PUT", "POST"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

3. Create IAM user with permissions:
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
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-bucket-name/*",
                "arn:aws:s3:::your-bucket-name"
            ]
        }
    ]
}
```

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

## Security Best Practices

1. **JWT Tokens**: Short-lived access tokens (30 min) with refresh tokens (7 days)
2. **Password Hashing**: Bcrypt with automatic salt generation
3. **CORS**: Configured for specific origins
4. **SQL Injection**: Protected by SQLAlchemy parameterized queries
5. **Input Validation**: Pydantic schemas validate all inputs
6. **Rate Limiting**: Implement rate limiting for production (use nginx or Cloudflare)

## Performance Optimization

1. **Database**:
   - Connection pooling (10 connections, 20 max overflow)
   - Async queries with asyncio
   - Proper indexing on foreign keys and query fields

2. **Caching**:
   - Add Redis for session caching (optional)
   - Cache AI responses for common questions

3. **File Upload**:
   - Direct S3 upload via presigned URLs (no backend bandwidth)
   - Async file processing

## Monitoring and Logging

- Structured logging with Python logging module
- Log levels configurable via environment variable
- Health check endpoint: `/health`
- Metrics endpoint: Consider adding Prometheus metrics

## Troubleshooting

### Database connection issues
```bash
# Check MySQL is running
mysql -u user -p -h localhost

# Test connection
python -c "from app.db.base import engine; import asyncio; asyncio.run(engine.connect())"
```

### Migration issues
```bash
# Check current revision
alembic current

# View migration history
alembic history

# Reset database (⚠️ destroys data)
alembic downgrade base
alembic upgrade head
```

### S3 upload issues
- Verify AWS credentials
- Check S3 bucket CORS configuration
- Ensure bucket region matches configuration

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open a GitHub issue.

# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Mobile Frontend                           │
│                    (React Native + Expo)                         │
└────────────────┬────────────────────────────────┬───────────────┘
                 │                                │
                 │ REST API                       │ WebSocket
                 │ (HTTPS)                        │ (WSS)
                 │                                │
┌────────────────▼────────────────────────────────▼───────────────┐
│                     FastAPI Backend                              │
│                   (Railway/Docker)                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API Layer (Endpoints)                        │  │
│  │  • Authentication  • Upload  • Sessions  • AI  • WS      │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │           Business Logic (Services)                       │  │
│  │  • User Service  • Session Service  • S3  • AI Service   │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                              │                                   │
│  ┌──────────────────────────▼───────────────────────────────┐  │
│  │         Data Access (Models + Database)                   │  │
│  │  • User Model  • Session Model  • Upload Model           │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              │               │               │
    ┌─────────▼─────┐  ┌─────▼──────┐  ┌────▼──────┐
    │               │  │            │  │           │
    │  MySQL DB     │  │  AWS S3    │  │  OpenAI   │
    │  (Railway)    │  │  Storage   │  │    API    │
    │               │  │            │  │           │
    └───────────────┘  └────────────┘  └───────────┘
```

## Request Flow

### 1. Authentication Flow

```
┌──────┐     POST /auth/register      ┌─────────────┐
│      │ ──────────────────────────> │             │
│Client│                              │   FastAPI   │
│      │ <────────────────────────── │             │
└──────┘     { user, token, refresh } └──────┬──────┘
                                             │
                                             │
                                       ┌─────▼─────┐
                                       │   MySQL   │
                                       │   Users   │
                                       └───────────┘

Steps:
1. Client sends email + password
2. FastAPI validates input (Pydantic)
3. UserService hashes password (bcrypt)
4. User saved to database
5. JWT tokens generated (python-jose)
6. Tokens returned to client
```

### 2. File Upload Flow

```
┌──────┐  1. POST /upload/s3-presign   ┌─────────────┐
│      │ ──────────────────────────> │             │
│Client│ <────────────────────────── │   FastAPI   │
│      │  { url: presigned_url }       │             │
└───┬──┘                               └─────────────┘
    │                                         │
    │ 2. PUT (file)                           │
    │    to presigned_url                     │
    │                                         │
    ▼                                         │
┌───────┐                                     │
│ AWS S3│                                     │
└───┬───┘                                     │
    │ 3. Upload success                       │
    │                                         │
    └────────> Client ─────────────────────> │
                4. POST /upload/confirm       │
                      { key }                 │
                                              │
                                        ┌─────▼─────┐
                                        │   MySQL   │
                                        │  Uploads  │
                                        └───────────┘

Steps:
1. Client requests presigned URL from backend
2. Backend generates URL with S3 service
3. Client uploads directly to S3
4. Client confirms upload to backend
5. Backend records upload in database
```

### 3. Interview Session Flow

```
┌──────┐  1. Start Session              ┌─────────────┐
│      │ ──────────────────────────>  │   FastAPI   │
│Client│                                │             │
│      │  2. WS /ws/transcribe          │             │
│      │ ════════════════════════════> │  WebSocket  │
│      │                                │   Manager   │
│      │  3. Record Audio               └──────┬──────┘
│      │                                       │
│      │  4. Upload to S3                      │
│      │ ──────────> AWS S3                    │
│      │                                       │
│      │  5. Send S3 key via WS                │
│      │ ════════════════════════════> │       │
│      │                                │  ┌────▼─────┐
│      │                                │  │ OpenAI   │
│      │  6. Transcript                 │  │ Whisper  │
│      │ <════════════════════════════ │  └────┬─────┘
│      │                                │       │
│      │  7. Complete Session           │       │
│      │ ──────────────────────────>  │  ┌────▼─────┐
│      │                                │  │   AI     │
│      │  8. Feedback                   │  │ Feedback │
│      │ <────────────────────────────  │  │Generator │
└──────┘                                └──┴──────────┘

Steps:
1. Client creates interview session
2. Opens WebSocket connection
3. Records audio
4. Uploads audio to S3
5. Sends S3 key via WebSocket
6. Backend transcribes with Whisper
7. Client completes session
8. Backend generates AI feedback
```

## Layer Architecture

### Presentation Layer (API Endpoints)

```python
# app/api/endpoints/auth.py
@router.post("/register")
async def register(user_data: UserCreate):
    """Handle registration logic"""
    # Validate input (automatic via Pydantic)
    # Call service layer
    # Return response
```

**Responsibilities:**
- HTTP request/response handling
- Input validation
- Authentication checks
- Response formatting

### Business Logic Layer (Services)

```python
# app/services/user_service.py
class UserService:
    @staticmethod
    async def create_user(db, user_data):
        """Business logic for user creation"""
        # Hash password
        # Create user model
        # Save to database
        # Return user
```

**Responsibilities:**
- Business rules
- Data transformation
- External service calls
- Transaction management

### Data Access Layer (Models)

```python
# app/models/user.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    # ... other fields
```

**Responsibilities:**
- Database schema
- Data relationships
- Query building
- Data persistence

## Security Architecture

### Authentication Pipeline

```
1. Client Request
   └─> Header: Authorization: Bearer {token}

2. API Endpoint
   └─> Depends(get_current_user)

3. Security Dependency
   ├─> Extract token from header
   ├─> Decode JWT
   ├─> Validate signature
   ├─> Check expiration
   └─> Load user from database

4. Endpoint Handler
   └─> Access to authenticated user
```

### Token Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ Login
       ▼
┌─────────────┐
│  FastAPI    │ ─────> Generate Access Token (30 min)
│   /login    │ ─────> Generate Refresh Token (7 days)
└──────┬──────┘
       │
       │ Return both tokens
       ▼
┌─────────────┐
│   Client    │ ─────> Store in Redux + AsyncStorage
│   Store     │
└──────┬──────┘
       │
       │ API Request with Access Token
       ▼
┌─────────────┐
│  FastAPI    │ ─────> Verify Access Token
│  Endpoint   │
└──────┬──────┘
       │
       │ 401 Unauthorized
       ▼
┌─────────────┐
│   Client    │ ─────> Auto-refresh using Refresh Token
│ Interceptor │
└──────┬──────┘
       │
       │ POST /auth/refresh
       ▼
┌─────────────┐
│  FastAPI    │ ─────> New Access Token
│  /refresh   │
└─────────────┘
```

## Database Architecture

### Entity Relationship Diagram

```
┌─────────────────┐
│     USERS       │
├─────────────────┤
│ PK id           │
│    email        │◄─────────┐
│    name         │          │
│    password     │          │
│    created_at   │          │
└─────────────────┘          │
                             │
                        FK user_id
                             │
                   ┌─────────┴──────────┐
                   │                    │
         ┌─────────▼────────┐  ┌────────▼──────────┐
         │ INTERVIEW_SESSION │  │     UPLOADS       │
         ├──────────────────┤  ├───────────────────┤
         │ PK id            │  │ PK id             │
         │ FK user_id       │  │ FK user_id        │
         │    title         │  │    s3_key         │
         │    question      │  │    content_type   │
         │    transcript    │  │    file_size      │
         │    audio_s3_key  │  │    uploaded_at    │
         │    scores        │  └───────────────────┘
         │    feedback      │
         │    created_at    │
         └──────────────────┘
```

### Indexes

```sql
-- Users
CREATE INDEX idx_users_email ON users(email);

-- Interview Sessions
CREATE INDEX idx_sessions_user_id ON interview_sessions(user_id);
CREATE INDEX idx_sessions_created_at ON interview_sessions(created_at);

-- Uploads
CREATE INDEX idx_uploads_user_id ON uploads(user_id);
CREATE INDEX idx_uploads_s3_key ON uploads(s3_key);
```

## Scalability Architecture

### Horizontal Scaling

```
              ┌──────────────┐
              │ Load Balancer│
              │   (Railway)  │
              └───────┬──────┘
                      │
         ┌────────────┼────────────┐
         │            │            │
    ┌────▼───┐   ┌───▼────┐   ┌───▼────┐
    │FastAPI │   │FastAPI │   │FastAPI │
    │Instance│   │Instance│   │Instance│
    │   1    │   │   2    │   │   3    │
    └────┬───┘   └───┬────┘   └───┬────┘
         │           │            │
         └───────────┼────────────┘
                     │
              ┌──────▼──────┐
              │MySQL Primary│
              └──────┬──────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼───┐  ┌───▼────┐  ┌───▼────┐
    │ Read   │  │ Read   │  │ Read   │
    │Replica │  │Replica │  │Replica │
    └────────┘  └────────┘  └────────┘
```

### Caching Layer (Future)

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ FastAPI  │────>│  Redis   │────>│  MySQL   │
│ Instance │<────│  Cache   │<────│  Primary │
└──────────┘     └──────────┘     └──────────┘
                      │
                      ├─ Session data
                      ├─ User profiles
                      ├─ API rate limits
                      └─ AI responses
```

## Deployment Architecture

### Railway Deployment

```
┌─────────────────────────────────────────────┐
│            Railway Platform                  │
│                                              │
│  ┌─────────────┐      ┌─────────────┐      │
│  │  Web Service│      │   MySQL DB  │      │
│  │  (FastAPI)  │─────>│  (Managed)  │      │
│  │             │      │             │      │
│  │ • Auto-scale│      │ • Backups   │      │
│  │ • HTTPS     │      │ • Replicas  │      │
│  │ • Logs      │      │ • Monitor   │      │
│  └─────────────┘      └─────────────┘      │
└─────────────────────────────────────────────┘
         │                        │
         │                        │
         ▼                        ▼
┌─────────────┐          ┌─────────────┐
│   AWS S3    │          │  OpenAI API │
│   Storage   │          │   Service   │
└─────────────┘          └─────────────┘
```

### Docker Architecture

```
┌────────────────────────────────────────┐
│        Docker Container                 │
│                                         │
│  ┌──────────────────────────────────┐ │
│  │     Application Layer            │ │
│  │  • FastAPI App                   │ │
│  │  • Uvicorn Server                │ │
│  │  • Python 3.11                   │ │
│  └──────────────────────────────────┘ │
│                                         │
│  ┌──────────────────────────────────┐ │
│  │     Runtime Layer                │ │
│  │  • Python packages               │ │
│  │  • System libraries              │ │
│  └──────────────────────────────────┘ │
│                                         │
│  ┌──────────────────────────────────┐ │
│  │     Base Layer                   │ │
│  │  • Python 3.11-slim              │ │
│  │  • Linux (Debian)                │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

## Error Handling Flow

```
┌──────────┐
│  Client  │
└────┬─────┘
     │ Request
     ▼
┌─────────────┐
│  Endpoint   │ ─────> Validation Error
└────┬────────┘       └──> 422 Response
     │
     │ Valid Request
     ▼
┌─────────────┐
│  Service    │ ─────> Business Logic Error
└────┬────────┘       └──> 400 Response
     │
     │ Valid Operation
     ▼
┌─────────────┐
│  Database   │ ─────> Database Error
└────┬────────┘       └──> 500 Response
     │
     │ Success
     ▼
┌─────────────┐
│  Response   │
└─────────────┘
```

## Monitoring & Observability

```
┌─────────────────────────────────────────────┐
│           Application Metrics                │
├─────────────────────────────────────────────┤
│ • Request rate                               │
│ • Response time                              │
│ • Error rate                                 │
│ • Active connections                         │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│              Logging                         │
├─────────────────────────────────────────────┤
│ • Structured logs (JSON)                     │
│ • Log levels (DEBUG, INFO, WARN, ERROR)     │
│ • Request/response logging                   │
│ • Exception tracking                         │
└────────────────┬────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────┐
│          Health Checks                       │
├─────────────────────────────────────────────┤
│ • /health endpoint                           │
│ • Database connectivity                      │
│ • External service status                    │
└─────────────────────────────────────────────┘
```

## Summary

This architecture provides:

✅ **Scalability**: Horizontal scaling ready
✅ **Maintainability**: Clean separation of concerns
✅ **Security**: Multiple layers of protection
✅ **Performance**: Async operations throughout
✅ **Reliability**: Error handling at every layer
✅ **Observability**: Comprehensive logging and monitoring
✅ **Deployment**: Railway-ready with Docker support

The architecture follows industry best practices and is production-ready for deployment.

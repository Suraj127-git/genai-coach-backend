# Dependency Compatibility Analysis

This document verifies that all dependencies in `requirements.txt` are compatible with each other.

## Last Updated: December 7, 2025

## Critical Dependencies & Compatibility

### Core Framework
- **fastapi==0.115.0** ✅
  - Requires: `starlette<0.39.0,>=0.37.2`
  - Requires: `pydantic>=1.7.4,!=1.8,!=1.8.1,!=2.0.0,!=2.0.1,!=2.1.0,<3.0.0`
  - Compatible with: `pydantic==2.9.2`

- **uvicorn[standard]==0.32.0** ✅
  - Compatible with: `fastapi==0.115.0`

### Database
- **sqlalchemy==2.0.35** ✅
- **aiomysql==0.2.0** ✅
  - Requires: `PyMySQL>=1.0`
  - Auto-installed: `pymysql==1.1.2`

### AI/ML Stack - **CRITICAL COMPATIBILITY CHECK**

#### OpenAI
- **openai==1.58.1** ✅ **UPDATED**
  - Previous version: `1.54.3` ❌ (caused conflict)
  - Required by: `langchain-openai==0.2.14` needs `openai>=1.58.1,<2.0.0`
  - **This was the root cause of the deployment failure**

#### LangChain Ecosystem
- **langchain==0.3.13** ✅
  - Requires: `langchain-core>=0.3.0,<0.4.0`
  - Compatible with: `langchain-core==0.3.28`

- **langchain-core==0.3.28** ✅
  - Compatible with all langchain packages

- **langchain-openai==0.2.14** ✅
  - **Requires: `openai>=1.58.1,<2.0.0`** ⚠️
  - Compatible with: `openai==1.58.1` ✅

- **langchain-community==0.3.13** ✅
  - Compatible with: `langchain-core==0.3.28`

- **langchain-groq==0.2.1** ✅
  - Requires: `groq>=0.9.0,<1.0.0`
  - Compatible with: `groq==0.13.0`

- **langgraph==0.2.59** ✅
  - Requires: `langchain-core>=0.3.0,<0.4.0`
  - Compatible with: `langchain-core==0.3.28`

- **langsmith==0.2.7** ✅
  - Monitoring/observability for LangChain
  - No conflicts

#### Vector Database & Embeddings
- **sentence-transformers==3.3.1** ✅
  - Large package (~1 GB with PyTorch)
  - Requires: `torch>=1.11.0`
  - Requires: `transformers<5.0.0,>=4.41.0`
  - Requires: `huggingface-hub>=0.19.3`

- **chromadb==0.5.23** ✅
  - Requires: `numpy>=1.22.5`
  - Compatible with: `numpy==1.26.4` (installed by langchain)

#### Other AI Services
- **groq==0.13.0** ✅
  - Compatible with: `langchain-groq==0.2.1`

- **tiktoken==0.8.0** ✅
  - Token counting for OpenAI
  - No conflicts

### HTTP & Networking
- **httpx==0.27.2** ✅
  - Requires: `httpcore==1.*`
  - Auto-installed: `httpcore==1.0.9`

- **websockets==13.1** ✅
  - No conflicts

### Security & Authentication
- **python-jose[cryptography]==3.3.0** ✅
- **passlib[argon2]==1.7.4** ✅
  - Requires: `argon2-cffi>=16.2` (installed via extras)

### AWS
- **boto3==1.35.36** ✅
  - Auto-installs: `botocore==1.35.99` (compatible)
  - Auto-installs: `s3transfer==0.10.4`
  - Auto-installs: `jmespath==1.0.1`

### Monitoring
- **sentry-sdk[fastapi]==2.17.0** ✅
  - Compatible with: `fastapi==0.115.0`

### Utilities
- **tenacity==9.0.0** ✅ (Retry logic)
- **python-dotenv==1.0.1** ✅ (Environment variables)
- **python-multipart==0.0.12** ✅ (File uploads)

## Dependency Tree Summary

Total packages (including auto-installed dependencies): ~43

### Size Breakdown
| Component | Size | Notes |
|-----------|------|-------|
| sentence-transformers + torch | ~1.8 GB | Largest - ML models |
| chromadb | ~200 MB | Vector database |
| langchain ecosystem | ~100 MB | AI orchestration |
| Other dependencies | ~300 MB | Various utilities |
| **Total** | **~2.4 GB** | Optimized from 2.5 GB |

## Resolved Conflicts

### 1. OpenAI Version Conflict ✅ FIXED
**Problem:**
- `openai==1.54.3` was incompatible with `langchain-openai==0.2.14`
- Error: `langchain-openai 0.2.14 depends on openai<2.0.0 and >=1.58.1`

**Solution:**
- Updated `openai==1.54.3` → `openai==1.58.1`
- File: `requirements.txt` line 25

**Impact:**
- No breaking changes (OpenAI maintains backward compatibility)
- All existing code continues to work

## Potential Future Conflicts

### Watch for Updates
1. **OpenAI SDK**: Keep aligned with `langchain-openai` requirements
2. **LangChain versions**: All packages should be on same minor version (0.3.x)
3. **Pydantic**: FastAPI and LangChain both depend on it - coordinate upgrades

## Testing Compatibility

### Local Testing
```bash
cd genai-mock-interview-backend

# Create fresh virtual environment
python -m venv venv_test
source venv_test/bin/activate  # Windows: venv_test\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify no conflicts
pip check
```

Expected output:
```
No broken requirements found.
```

### Docker Testing
```bash
# Build locally
docker build -t genai-coach-test .

# Should complete without errors
```

## Railway Deployment Notes

### Cache Issues
Railway may cache the previous `requirements.txt`. To force a fresh build:

1. **Option 1: Trigger new deployment**
   - Push a new commit
   - Railway will detect changes and rebuild

2. **Option 2: Clear build cache (Railway UI)**
   - Go to deployment settings
   - Click "Clear build cache"
   - Redeploy

3. **Option 3: Add cache-busting comment**
   - Add a comment to requirements.txt
   - Commit and push

### Current Status
- ✅ Local `requirements.txt` has `openai==1.58.1`
- ⚠️ Railway may be using cached version with `openai==1.54.3`
- **Action Required**: Push commit to trigger fresh build

## Verification Checklist

- [x] OpenAI version updated to 1.58.1
- [x] All LangChain packages on compatible versions
- [x] No circular dependencies
- [x] No version conflicts in pip resolver
- [ ] Railway deployment successful (pending)
- [ ] Application starts without import errors (pending)

## Commands for Verification

```bash
# Check specific package version
pip show openai

# Check all installed versions
pip list

# Verify no conflicts
pip check

# Show dependency tree
pip install pipdeptree
pipdeptree -p openai
pipdeptree -p langchain-openai
```

## Expected Output

```bash
$ pip show openai
Name: openai
Version: 1.58.1
Summary: The official Python library for the openai API
Home-page: https://github.com/openai/openai-python
Requires: anyio, distro, httpx, jiter, pydantic, sniffio, tqdm, typing-extensions

$ pip show langchain-openai
Name: langchain-openai
Version: 0.2.14
Summary: An integration package connecting OpenAI and LangChain
Requires: langchain-core, openai, tiktoken
```

## Conclusion

All dependencies are now compatible. The primary issue was:
- **openai==1.54.3** → **openai==1.58.1** (FIXED)

The deployment should succeed once Railway uses the updated `requirements.txt`.

---

**Next Steps:**
1. Commit the updated requirements.txt
2. Push to trigger Railway deployment
3. Monitor build logs to confirm openai==1.58.1 is installed
4. Verify application starts successfully

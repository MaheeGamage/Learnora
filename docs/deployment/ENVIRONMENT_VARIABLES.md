# Environment Variables Configuration

## Summary of Changes

The deployment pipeline and Docker Compose setup have been improved to handle optional environment variables properly, avoiding validation errors when values are not set.

## What Changed

### 1. Docker Compose (`docker-compose.yml`)
- Now uses default values for optional variables: `${VAR:-default}`
- Explicitly includes `env_file: .env` directive
- Only includes variables with sensible defaults to avoid empty string issues

### 2. GitHub Actions Pipeline (`.github/workflows/deploy-core-service.yml`)
- Uses fallback values for optional secrets: `${{ secrets.VAR || 'default' }}`
- Only adds truly optional variables (like `DB_POOL_SIZE`) if they are set
- Prevents empty string values from being passed to the container

### 3. Environment Files
- `.env.example`: Clarified required vs optional variables
- `.env.docker`: New minimal template for local Docker testing

## Required GitHub Secrets

You **must** set these in GitHub repository settings:

```
VM_SSH_KEY          # SSH private key for VM access
SECRET_KEY          # Generate with: openssl rand -hex 32
DATABASE_URL        # Your database connection string
GOOGLE_API_KEY      # Your Google AI API key
```

## Optional GitHub Secrets

These have sensible defaults if not set:

```
APP_ENV             # Default: production
DEBUG               # Default: False
DB_ECHO             # Default: False
LANGSMITH_TRACING   # Default: false
LANGSMITH_ENDPOINT  # Default: https://eu.api.smith.langchain.com
```

## Truly Optional Secrets

Only add these if you actually need them:

```
DB_POOL_SIZE        # Leave unset for SQLite or auto-pooling
DB_MAX_OVERFLOW     # Leave unset for SQLite or auto-pooling
LANGSMITH_API_KEY   # Only if using LangSmith
LANGSMITH_PROJECT   # Only if using LangSmith
```

## Local Testing with Docker Compose

### Option 1: Using `.env` file (Recommended)

```bash
cd core-service
copy .env.docker .env
# Edit .env with your values
docker-compose up
```

### Option 2: Minimal `.env` for testing

Create `core-service/.env`:
```env
APP_ENV=development
DEBUG=True
SECRET_KEY=test-secret-key
DATABASE_URL=sqlite:///./learnora.db
DB_ECHO=False
GOOGLE_API_KEY=your_google_api_key_here
LANGSMITH_TRACING=false
```

## How It Works

### Before (Problem)
```yaml
environment:
  - DB_POOL_SIZE=${DB_POOL_SIZE}  # Empty string if not set → validation error
```

### After (Solution)
1. **Docker Compose** skips optional variables or uses defaults
2. **GitHub Actions** only adds variables that are actually set
3. **Pydantic** receives valid values or no value at all (uses model defaults)

## Validation Flow

```
GitHub Secrets (optional empty)
    ↓
Pipeline checks if set → Only adds if non-empty
    ↓
.env file (only valid values)
    ↓
Docker Compose reads .env → Uses defaults for missing
    ↓
Container environment (all valid)
    ↓
Pydantic Settings (validates successfully)
```

## Error Prevention

### ❌ What Caused Errors Before
- Empty strings passed to boolean/integer fields
- Docker Compose sending `VAR=''` to container
- Pydantic unable to parse empty strings

### ✅ What Prevents Errors Now
- Optional variables only added if they have values
- Default values for common configuration
- Environment variables either have valid values or aren't set at all
- Pydantic uses its own defaults for unset variables

## Testing Checklist

Before deploying:
- [ ] Set required GitHub Secrets (SECRET_KEY, DATABASE_URL, GOOGLE_API_KEY)
- [ ] Optionally set other secrets based on your needs
- [ ] Test locally with `docker-compose up` first
- [ ] Verify `.env` file has no empty values for boolean/integer fields
- [ ] Push to trigger deployment

## Troubleshooting

### If you get validation errors:
1. Check GitHub Secrets - are required ones set?
2. Check `.env` file on VM - any empty values?
3. Check Docker logs: `docker-compose logs`
4. Verify optional secrets either have values or aren't set at all

### If deployment fails:
1. Check GitHub Actions logs
2. Verify VM has Docker and Docker Compose installed
3. Verify SSH key is properly formatted in secrets
4. Test SSH connection manually: `ssh ubuntu@86.50.20.100`

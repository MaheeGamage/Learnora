# Deployment Guide

## Prerequisites

### On the VM (86.50.20.100)
1. Docker and Docker Compose installed
2. SSH access configured
3. Port 8000 open for the application

### On GitHub Repository
Configure the following secrets in your GitHub repository (Settings > Secrets and variables > Actions):

#### Required Secrets:
- `VM_SSH_KEY`: Private SSH key for accessing ubuntu@86.50.20.100

#### Required Application Secrets:
- `SECRET_KEY`: Generate with `openssl rand -hex 32`
- `DATABASE_URL`: Your database connection string
- `GOOGLE_API_KEY`: Your Google AI API key

#### Optional Application Secrets (with defaults if not provided):
- `APP_ENV`: `production` or `staging` (default: `production`)
- `DEBUG`: `False` for production (default: `False`)
- `DB_ECHO`: `False` for production (default: `False`)
- `LANGSMITH_TRACING`: `true` or `false` (default: `false`)
- `LANGSMITH_ENDPOINT`: LangSmith endpoint URL (default: `https://eu.api.smith.langchain.com`)

#### Optional Application Secrets (only add if needed):
- `DB_POOL_SIZE`: Connection pool size (leave unset for auto/SQLite)
- `DB_MAX_OVERFLOW`: Max overflow connections (leave unset for auto)
- `LANGSMITH_API_KEY`: Your LangSmith API key (only if using LangSmith)
- `LANGSMITH_PROJECT`: Your LangSmith project name (only if using LangSmith)

## Setup Instructions

### 1. VM Setup

Connect to your VM:
```bash
ssh ubuntu@86.50.20.100
```

Install Docker and Docker Compose:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Log out and back in for group changes to take effect
exit
```

Install Docker Compose:
```bash
sudo apt install docker-compose-plugin -y
```

### 2. GitHub Secrets Setup

1. Generate SSH key pair (if not already done):
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-deploy"
   ```

2. Add the public key to VM's authorized_keys:
   ```bash
   cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
   ```

3. Copy private key content and add to GitHub Secrets as `VM_SSH_KEY`:
   ```bash
   cat ~/.ssh/id_ed25519
   ```

4. Add all environment variable secrets listed above to GitHub Secrets

### 3. Deploy

The deployment will trigger automatically when:
- You push to `main` or `mahee-dev` branch
- Changes are made to the `core-service/` directory

Or manually trigger the workflow:
1. Go to Actions tab in GitHub
2. Select "Deploy Core Service to VM"
3. Click "Run workflow"

## Deployment Process

The GitHub Actions workflow will:
1. Checkout the latest code
2. Setup SSH connection to the VM
3. Create `.env` file with secrets
4. Copy files to VM using rsync
5. Build Docker image
6. Start containers with Docker Compose
7. Perform health check
8. Clean up

## Manual Deployment

If needed, you can deploy manually:

```bash
# On your local machine
cd core-service

# Copy files to VM
rsync -avz --exclude='.venv' --exclude='__pycache__' ./ ubuntu@86.50.20.100:/home/ubuntu/learnora/core-service/

# SSH into VM
ssh ubuntu@86.50.20.100

# Navigate to deployment directory
cd /home/ubuntu/learnora/core-service

# Create .env file with your environment variables
nano .env

# Deploy with Docker Compose
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Monitoring

### Check container status:
```bash
ssh ubuntu@86.50.20.100
cd /home/ubuntu/learnora/core-service
docker-compose ps
```

### View logs:
```bash
docker-compose logs -f
```

### Restart service:
```bash
docker-compose restart
```

### Stop service:
```bash
docker-compose down
```

## Troubleshooting

### Container won't start:
1. Check logs: `docker-compose logs`
2. Verify .env file exists and has correct values
3. Check port 8000 is not already in use

### Database connection issues:
1. Verify DATABASE_URL is correct
2. Check network connectivity from VM to database
3. Verify database credentials

### Health check fails:
1. Wait a bit longer for the app to start
2. Check if port 8000 is accessible: `curl http://86.50.20.100:8000/docs`
3. Review container logs for errors

## Accessing the Application

Once deployed, the application will be available at:
- API Documentation: http://86.50.20.100:8000/docs
- API Base URL: http://86.50.20.100:8000

## Updating the Application

Simply push your changes to the configured branch (main or mahee-dev). The GitHub Actions workflow will automatically deploy the updates.

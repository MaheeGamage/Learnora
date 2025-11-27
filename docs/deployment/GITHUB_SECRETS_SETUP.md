# GitHub Secrets Setup Guide

## SSH Key Setup for VM Deployment

### Problem
The error `Load key "/home/runner/.ssh/deploy_key": error in libcrypto` occurs when the SSH private key stored in GitHub Secrets has formatting issues.

### Solution: Properly Format SSH Key

#### Step 1: Generate SSH Key on Your Local Machine (if needed)

```bash
# Generate a new ED25519 SSH key (recommended)
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/learnora_deploy_key -N ""

# Or if your system doesn't support ed25519, use RSA
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/learnora_deploy_key -N ""
```

#### Step 2: Copy Public Key to VM

```bash
# Copy the public key to your VM
ssh-copy-id -i ~/.ssh/learnora_deploy_key.pub ubuntu@86.50.20.100

# Or manually add it
cat ~/.ssh/learnora_deploy_key.pub
# Then SSH into your VM and add it to ~/.ssh/authorized_keys
```

#### Step 3: Prepare Private Key for GitHub Secrets

The key must be in the **exact correct format**:

```bash
# View your private key
cat ~/.ssh/learnora_deploy_key
```

**Important formatting rules:**
1. Must start with `-----BEGIN OPENSSH PRIVATE KEY-----` or `-----BEGIN RSA PRIVATE KEY-----`
2. Must end with `-----END OPENSSH PRIVATE KEY-----` or `-----END RSA PRIVATE KEY-----`
3. Must include ALL lines including the header and footer
4. Must have proper line breaks (not all on one line)
5. No extra spaces or characters at the beginning or end

**Example of correct format:**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACBqRFDr+ynJJr3yVqF8JmNdCMo2HKwG3JvkMlp0l7eQ9gAAAJhGCk2sRgpN
rAAAAAtzc2gtZWQyNTUxOQAAACBqRFDr+ynJJr3yVqF8JmNdCMo2HKwG3JvkMlp0l7eQ9g
AAAECvMDmT4E8fU7D8iJDVF5QYG9B3eP5xF7yVqF8JmNdCMo2HKwG3JvkMlp0l7eQ9gAA
AGdpdGh1Yi1hY3Rpb25zLWRlcGxveQECAwQFBg==
-----END OPENSSH PRIVATE KEY-----
```

#### Step 4: Add to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `VM_SSH_KEY`
5. Value: Paste the **entire private key** (including BEGIN and END lines)
6. Click **Add secret**

### Alternative: Use the Correct Key Type

If you continue having issues, try using a different key type:

#### Option A: Use RSA Key (Most Compatible)

```bash
# Generate RSA key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/learnora_rsa -N ""

# Add public key to VM
cat ~/.ssh/learnora_rsa.pub
# Copy this to your VM's ~/.ssh/authorized_keys

# Add private key to GitHub Secrets
cat ~/.ssh/learnora_rsa
# Copy the entire output to GitHub Secrets as VM_SSH_KEY
```

#### Option B: Convert ED25519 to PEM Format

If you have an ed25519 key causing issues:

```bash
# Convert to PEM format
ssh-keygen -p -f ~/.ssh/learnora_deploy_key -m pem -N ""

# Now use this converted key
cat ~/.ssh/learnora_deploy_key
# Copy to GitHub Secrets
```

### Testing the SSH Key

After setting up the key in GitHub Secrets, the workflow will test it in the "Setup SSH" step.

### Common Issues and Solutions

#### Issue 1: "error in libcrypto"
**Cause:** Key has wrong format or corrupted
**Solution:** Regenerate the key and ensure proper formatting

#### Issue 2: "Permission denied (publickey)"
**Cause:** Public key not added to VM or wrong key used
**Solution:** 
```bash
# On your VM
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

#### Issue 3: Key has extra characters
**Cause:** Copy-paste added extra spaces or newlines
**Solution:** Use `cat` command to get raw key, don't manually copy

### Verification Checklist

Before adding to GitHub Secrets, verify:
- [ ] Key starts with `-----BEGIN` line
- [ ] Key ends with `-----END` line
- [ ] No extra blank lines at the start or end
- [ ] No extra spaces or tabs
- [ ] Public key is added to VM's `~/.ssh/authorized_keys`
- [ ] VM's `~/.ssh/authorized_keys` has correct permissions (600)
- [ ] VM's `~/.ssh` directory has correct permissions (700)

### Quick Test on VM

```bash
# SSH into your VM
ssh ubuntu@86.50.20.100

# Check authorized_keys
cat ~/.ssh/authorized_keys

# Check permissions
ls -la ~/.ssh/
# Should show:
# drwx------ for .ssh directory
# -rw------- for authorized_keys file

# Fix permissions if needed
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

## All Required GitHub Secrets

Make sure you have set up all these secrets:

### SSH Configuration
- `VM_SSH_KEY` - Private SSH key for VM access

### Application Environment
- `APP_ENV` - production
- `DEBUG` - False
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `DATABASE_URL` - Your database URL
- `DB_ECHO` - False
- `DB_POOL_SIZE` - (optional) e.g., 5
- `DB_MAX_OVERFLOW` - (optional) e.g., 10
- `LANGSMITH_TRACING` - true/false
- `LANGSMITH_API_KEY` - Your LangSmith API key
- `LANGSMITH_PROJECT` - Your project name
- `LANGSMITH_ENDPOINT` - https://eu.api.smith.langchain.com
- `GOOGLE_API_KEY` - Your Google AI API key

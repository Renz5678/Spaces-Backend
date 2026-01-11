# GitHub Actions Workflows

This directory contains automated workflows for the Spaces backend.

## 📋 Available Workflows

### 1. Health Check Monitor (`health-check.yml`)

**Purpose**: Monitors backend availability by pinging the `/health` endpoint every 10 minutes.

**Schedule**: Every 10 minutes (`*/10 * * * *`)

**What it does**:
- ✅ Pings `/health` endpoint
- ✅ Verifies HTTP 200 response
- ✅ Fetches health details (cache stats, environment)
- ✅ Checks cache statistics
- ❌ Fails workflow if backend is down

**Setup Required**:
1. Go to your GitHub repository settings
2. Navigate to **Settings → Secrets and variables → Actions**
3. Add a new secret: `BACKEND_URL`
4. Set value to your deployed backend URL (e.g., `https://api.yourdomain.com`)

**Manual Trigger**:
```bash
# Go to Actions tab → Health Check Monitor → Run workflow
```

---

### 2. Docker Build (`docker-build.yml`)

**Purpose**: Automatically builds and pushes Docker image to GitHub Container Registry on every push to `main`.

**Triggers**:
- Push to `main` branch
- Pull requests to `main`
- Manual workflow dispatch

**What it does**:
- ✅ Builds Docker image using multi-stage Dockerfile
- ✅ Pushes to GitHub Container Registry (`ghcr.io`)
- ✅ Tags with branch name, SHA, and `latest`
- ✅ Uses build cache for faster builds
- ✅ Generates build summary

**Image Location**:
```
ghcr.io/renz5678/spaces-backend:latest
```

**Pull the image**:
```bash
docker pull ghcr.io/renz5678/spaces-backend:latest
```

**No setup required** - uses `GITHUB_TOKEN` automatically!

---

## 🚀 Usage

### After Pushing to GitHub

1. **First push** will trigger the Docker build workflow
2. **Every 10 minutes** the health check will run (once deployed)
3. View workflow runs in the **Actions** tab

### Viewing Workflow Results

```
GitHub Repository → Actions tab
```

You'll see:
- ✅ Green checkmark = Success
- ❌ Red X = Failure
- 🟡 Yellow dot = Running

---

## 🔧 Configuration

### Health Check Workflow

Edit `.github/workflows/health-check.yml`:

```yaml
schedule:
  - cron: '*/10 * * * *'  # Change frequency here
```

**Cron examples**:
- `*/5 * * * *` - Every 5 minutes
- `*/15 * * * *` - Every 15 minutes
- `0 * * * *` - Every hour
- `0 */6 * * *` - Every 6 hours

### Docker Build Workflow

Edit `.github/workflows/docker-build.yml`:

```yaml
on:
  push:
    branches:
      - main  # Add more branches if needed
```

---

## 📊 Monitoring

### Health Check Notifications

To get notified when health checks fail, add notification steps:

**Slack Example**:
```yaml
- name: Notify Slack on Failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "🚨 Backend health check failed!"
      }
```

**Discord Example**:
```yaml
- name: Notify Discord on Failure
  if: failure()
  run: |
    curl -H "Content-Type: application/json" \
         -d '{"content":"🚨 Backend health check failed!"}' \
         ${{ secrets.DISCORD_WEBHOOK_URL }}
```

---

## 🎯 Next Steps

1. **Deploy your backend** to a hosting platform
2. **Add `BACKEND_URL` secret** in GitHub settings
3. **Push to main** to trigger Docker build
4. **Monitor Actions tab** for workflow results
5. **Optional**: Add notification integrations

---

## 📝 Notes

- Health checks only work after backend is deployed
- Docker images are stored in GitHub Container Registry (free for public repos)
- Workflows run on GitHub's servers (free for public repos)
- Build cache speeds up subsequent builds significantly

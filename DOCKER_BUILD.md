# Docker Build Instructions

## Prerequisites

Before building the Docker image, ensure Docker Desktop is installed and running:

1. **Check if Docker is installed**:
   ```bash
   docker --version
   ```

2. **Start Docker Desktop**:
   - Open Docker Desktop application
   - Wait for it to fully start (whale icon in system tray should be steady)

---

## Building the Docker Image

### Option 1: Build Locally

Once Docker Desktop is running, build the image:

```bash
cd c:\Users\Lawrenz\Desktop\Spaces\backend
docker build -t spaces-backend .
```

**Expected Output**:
```
[+] Building 45.2s (12/12) FINISHED
 => [internal] load build definition from Dockerfile
 => => transferring dockerfile: 1.23kB
 => [internal] load .dockerignore
 => [stage-1 1/6] FROM docker.io/library/python:3.11-slim
 => [builder 2/4] COPY requirements.txt .
 => [builder 3/4] RUN pip install --no-cache-dir --user -r requirements.txt
 => [stage-1 5/6] COPY --from=builder /root/.local /home/appuser/.local
 => [stage-1 6/6] COPY --chown=appuser:appuser . .
 => exporting to image
 => => naming to docker.io/library/spaces-backend
```

---

### Option 2: Using Docker Compose

Build and start the container in one command:

```bash
cd c:\Users\Lawrenz\Desktop\Spaces\backend
docker-compose up -d --build
```

This will:
1. Build the image
2. Create and start the container
3. Run in detached mode (background)

---

## Verify the Build

### Check Image Exists
```bash
docker images | findstr spaces-backend
```

**Expected Output**:
```
spaces-backend    latest    abc123def456    2 minutes ago    245MB
```

---

## Running the Container

### Option 1: Docker Run
```bash
docker run -d --name spaces-backend -p 8000:8000 --env-file .env spaces-backend
```

### Option 2: Docker Compose (Recommended)
```bash
docker-compose up -d
```

---

## Verify Container is Running

```bash
docker ps
```

**Expected Output**:
```
CONTAINER ID   IMAGE            COMMAND                  STATUS         PORTS
abc123def456   spaces-backend   "gunicorn main:app..."   Up 10 seconds  0.0.0.0:8000->8000/tcp
```

---

## Test the Containerized API

```bash
# Test health endpoint
curl http://localhost:8000/health

# Or using PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
```

---

## View Container Logs

```bash
# Docker run
docker logs spaces-backend -f

# Docker compose
docker-compose logs -f backend
```

---

## Stop and Remove Container

```bash
# Docker run
docker stop spaces-backend
docker rm spaces-backend

# Docker compose
docker-compose down
```

---

## Troubleshooting

### Docker Desktop Not Running
**Error**: `error during connect: Head "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping"`

**Solution**: 
1. Open Docker Desktop
2. Wait for it to fully start
3. Try the build command again

### Build Fails Due to Dependencies
**Solution**: 
- Ensure you have a stable internet connection
- The build downloads Python packages from PyPI

### Port Already in Use
**Error**: `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solution**:
1. Stop the local uvicorn server first
2. Or change the port mapping: `-p 8001:8000`

---

## Next Steps After Building

1. ✅ Build the image: `docker build -t spaces-backend .`
2. ✅ Test locally: `docker run -p 8000:8000 --env-file .env spaces-backend`
3. ✅ Verify endpoints work
4. 🚀 Deploy to production (cloud provider, VPS, etc.)
5. 🔒 Set up HTTPS with reverse proxy (nginx/traefik)
6. 📊 Configure monitoring and logging

---

## Production Deployment

For production deployment, consider:

- **Cloud Platforms**: AWS ECS, Google Cloud Run, Azure Container Instances
- **Container Orchestration**: Kubernetes, Docker Swarm
- **Platform-as-a-Service**: Railway, Render, Fly.io, Heroku

See [`deployment_guide.md`](deployment_guide.md) for detailed production deployment instructions.

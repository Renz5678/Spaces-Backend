# Spaces API - Deployment Guide

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run Development Server**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

1. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with production values
   ```

2. **Build and Run**
   ```bash
   docker-compose up -d
   ```

3. **View Logs**
   ```bash
   docker-compose logs -f backend
   ```

4. **Stop Services**
   ```bash
   docker-compose down
   ```

### Using Docker Directly

1. **Build Image**
   ```bash
   docker build -t spaces-backend .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name spaces-backend \
     -p 8000:8000 \
     --env-file .env \
     spaces-backend
   ```

---

## ⚙️ Environment Configuration

Create a `.env` file based on `.env.example`:

| Variable | Description | Default | Production Value |
|----------|-------------|---------|------------------|
| `ENVIRONMENT` | Environment mode | `development` | `production` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:5173` | `https://yourdomain.com` |
| `LOG_LEVEL` | Logging level | `INFO` | `WARNING` or `ERROR` |
| `RATE_LIMIT` | Requests per minute per IP | `60` | Adjust based on traffic |
| `CACHE_SIZE` | Max cached computations | `100` | Increase for high traffic |
| `CACHE_TTL` | Cache time-to-live (seconds) | `3600` | Adjust based on needs |
| `HOST` | Server host | `0.0.0.0` | `0.0.0.0` |
| `PORT` | Server port | `8000` | `8000` |

### Example Production `.env`

```env
ENVIRONMENT=production
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
LOG_LEVEL=WARNING
RATE_LIMIT=100
CACHE_SIZE=200
CACHE_TTL=7200
HOST=0.0.0.0
PORT=8000
```

---

## 🔍 API Endpoints

### Health & Monitoring

- **`GET /`** - Basic health check
- **`GET /health`** - Detailed health status with cache stats
- **`GET /api/cache/stats`** - Cache performance metrics
- **`DELETE /api/cache/clear`** - Clear computation cache

### Core Functionality

- **`POST /api/compute`** - Compute matrix subspaces (rate limited)
- **`GET /api/examples`** - Get example matrices

### Example Request

```bash
curl -X POST http://localhost:8000/api/compute \
  -H "Content-Type: application/json" \
  -d '{"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}'
```

---

## 📊 Performance Features

### Caching
- **Type**: TTL-based in-memory cache
- **Key**: SHA256 hash of matrix data
- **Benefits**: Instant responses for repeated computations
- **Monitoring**: Check `/api/cache/stats` for hit rates

### Compression
- **Type**: GZip compression
- **Threshold**: Responses > 1KB
- **Benefits**: Reduced bandwidth usage

### Rate Limiting
- **Default**: 60 requests/minute per IP
- **Response**: HTTP 429 when exceeded
- **Headers**: `X-RateLimit-*` headers in responses

---

## 🛡️ Security Features

### Production Security Headers
- `Strict-Transport-Security` (HSTS)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection`

### CORS Configuration
- Development: Allows `localhost:5173` and `localhost:3000`
- Production: **Must configure specific domains** in `ALLOWED_ORIGINS`

### Best Practices
1. Never use `ALLOWED_ORIGINS=*` in production
2. Use HTTPS in production (configure reverse proxy)
3. Set strong rate limits based on expected traffic
4. Monitor logs regularly
5. Keep dependencies updated

---

## 🚢 Production Deployment Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure `ALLOWED_ORIGINS` with your frontend domain(s)
- [ ] Set appropriate `LOG_LEVEL` (WARNING or ERROR)
- [ ] Adjust `RATE_LIMIT` based on expected traffic
- [ ] Configure `CACHE_SIZE` and `CACHE_TTL` for your needs
- [ ] Build Docker image: `docker build -t spaces-backend .`
- [ ] Test locally: `docker run -p 8000:8000 --env-file .env spaces-backend`
- [ ] Verify health endpoint: `curl http://localhost:8000/health`
- [ ] Test API endpoints with sample data
- [ ] Set up reverse proxy (nginx/traefik) with HTTPS
- [ ] Configure monitoring and alerting
- [ ] Set up log aggregation (optional)
- [ ] Deploy to production environment
- [ ] Verify CORS settings work with frontend
- [ ] Monitor cache hit rates and performance

---

## 📈 Monitoring & Troubleshooting

### Check Application Health
```bash
curl http://localhost:8000/health
```

### View Cache Statistics
```bash
curl http://localhost:8000/api/cache/stats
```

### Clear Cache (if needed)
```bash
curl -X DELETE http://localhost:8000/api/cache/clear
```

### View Docker Logs
```bash
docker-compose logs -f backend
```

### Common Issues

**Issue**: CORS errors from frontend
- **Solution**: Verify `ALLOWED_ORIGINS` includes your frontend URL

**Issue**: Rate limit errors
- **Solution**: Increase `RATE_LIMIT` in `.env`

**Issue**: Slow performance
- **Solution**: Check cache hit rate at `/api/cache/stats`, increase `CACHE_SIZE`

**Issue**: Container won't start
- **Solution**: Check logs with `docker-compose logs backend`

---

## 🔧 Advanced Configuration

### Custom Gunicorn Settings

Edit `Dockerfile` CMD to adjust workers:

```dockerfile
CMD ["gunicorn", "main:app", \
     "--workers", "8", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

**Worker Count Formula**: `(2 × CPU_CORES) + 1`

### Reverse Proxy (Nginx Example)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📝 API Documentation

Once deployed, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🆘 Support

For issues or questions:
1. Check logs for error messages
2. Verify environment configuration
3. Test endpoints with curl/Postman
4. Review cache and rate limit statistics

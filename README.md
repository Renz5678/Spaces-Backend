# Spaces Backend

Production-ready FastAPI backend for computing the four fundamental subspaces of linear algebra.

## Features

- ⚡ **High Performance**: TTL-based caching, gzip compression, async operations
- 🛡️ **Security**: Rate limiting, CORS configuration, security headers
- 📊 **Monitoring**: Health checks, cache statistics, structured logging
- 🐳 **Docker Ready**: Multi-stage builds, docker-compose configuration
- 🔧 **Production Ready**: Environment-based config, gunicorn deployment

## Quick Start

See [deployment_guide.md](deployment_guide.md) for detailed instructions.

### Development
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

### Production (Docker)
```bash
cp .env.example .env
# Edit .env with production values
docker-compose up -d
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

- `POST /api/compute` - Compute matrix subspaces
- `GET /api/examples` - Get example matrices
- `GET /health` - Health check with cache stats
- `GET /api/cache/stats` - Cache performance metrics

## Tech Stack

- FastAPI 0.109.0
- SymPy 1.12 (symbolic mathematics)
- Uvicorn/Gunicorn (ASGI server)
- Cachetools (TTL caching)
- SlowAPI (rate limiting)

"""
FastAPI Backend for Spaces - Linear Algebra Subspace Calculator
Optimized for production with caching, compression, and rate limiting.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Any, Dict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from cachetools import TTLCache
import hashlib
import json
import logging
import time
from contextlib import asynccontextmanager

from matrix_engine import MatrixEngine
from config import get_settings

# Load settings
settings = get_settings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize cache for computation results
computation_cache = TTLCache(maxsize=settings.cache_size, ttl=settings.cache_ttl)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting Spaces API in {settings.environment} mode")
    logger.info(f"Cache configured: size={settings.cache_size}, ttl={settings.cache_ttl}s")
    logger.info(f"Rate limit: {settings.rate_limit} requests/minute")
    yield
    logger.info("Shutting down Spaces API")


app = FastAPI(
    title="Spaces API",
    description="Compute the four fundamental subspaces of linear algebra",
    version="1.0.0",
    lifespan=lifespan,
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.3f}s"
    )
    
    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    return response


class MatrixInput(BaseModel):
    """Input model for matrix computation."""
    matrix: List[List[Any]] = Field(
        ...,
        description="2D array representing the matrix (max 5x5)",
        examples=[[[1, 2, 3], [4, 5, 6], [7, 8, 9]]]
    )

    @field_validator("matrix")
    @classmethod
    def validate_matrix(cls, v):
        if not v:
            raise ValueError("Matrix cannot be empty")
        if not isinstance(v, list):
            raise ValueError("Matrix must be a 2D array")
        return v


class SpaceResult(BaseModel):
    """Result model for a single subspace."""
    basis: List[List[Any]]
    latex: List[str]
    dimension: int
    description: str


class ComputationResult(BaseModel):
    """Full computation result."""
    matrix: Dict[str, Any]
    rank: int
    rref: Dict[str, Any]
    column_space: SpaceResult
    row_space: SpaceResult
    null_space: SpaceResult
    left_null_space: SpaceResult
    dimension_check: Dict[str, Any]
    cached: bool = False


def generate_cache_key(matrix_data: List[List[Any]]) -> str:
    """
    Generate a unique cache key for a matrix.
    Uses SHA256 hash of the JSON representation.
    """
    matrix_json = json.dumps(matrix_data, sort_keys=True)
    return hashlib.sha256(matrix_json.encode()).hexdigest()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Spaces API - Linear Algebra Subspace Calculator",
        "version": "1.0.0",
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check():
    """
    Comprehensive health check endpoint.
    Returns system status and cache statistics.
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
        "cache": {
            "size": len(computation_cache),
            "max_size": settings.cache_size,
            "ttl": settings.cache_ttl,
        },
        "timestamp": time.time(),
    }


@app.post("/api/compute", response_model=ComputationResult)
@limiter.limit(f"{settings.rate_limit}/minute")
async def compute_subspaces(request: Request, input_data: MatrixInput):
    """
    Compute all four fundamental subspaces for the given matrix.
    
    Features:
    - Response caching for identical matrices
    - Rate limiting to prevent abuse
    - Comprehensive error handling
    
    Returns:
        - Column Space basis
        - Row Space basis  
        - Null Space basis
        - Left Null Space basis
        - RREF and rank information
    """
    try:
        # Generate cache key
        cache_key = generate_cache_key(input_data.matrix)
        
        # Check cache first
        if cache_key in computation_cache:
            logger.info(f"Cache hit for matrix hash: {cache_key[:8]}...")
            cached_result = computation_cache[cache_key]
            cached_result["cached"] = True
            return cached_result
        
        logger.info(f"Cache miss - computing matrix hash: {cache_key[:8]}...")
        
        # Compute the result
        start_time = time.time()
        engine = MatrixEngine(input_data.matrix)
        result = engine.compute_all_spaces()
        computation_time = time.time() - start_time
        
        logger.info(f"Computation completed in {computation_time:.3f}s")
        
        # Add cached flag
        result["cached"] = False
        
        # Store in cache
        computation_cache[cache_key] = result
        
        return result
        
    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Computation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Computation error: {str(e)}")


@app.get("/api/examples")
async def get_examples():
    """Return example matrices for testing."""
    return {
        "examples": [
            {
                "name": "3×3 Rank 2",
                "description": "A 3×3 matrix with rank 2 (linearly dependent rows)",
                "matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            },
            {
                "name": "3×3 Identity",
                "description": "The 3×3 identity matrix (full rank)",
                "matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
            },
            {
                "name": "2×2 Identity",
                "description": "The 2×2 identity matrix",
                "matrix": [[1, 0], [0, 1]],
            },
            {
                "name": "4×4 Identity",
                "description": "The 4×4 identity matrix",
                "matrix": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
            },
            {
                "name": "5×5 Identity",
                "description": "The 5×5 identity matrix (max size)",
                "matrix": [[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]],
            },
            {
                "name": "2×3 Rectangular",
                "description": "A rectangular matrix with more columns than rows",
                "matrix": [[1, 2, 3], [4, 5, 6]],
            },
            {
                "name": "3×2 Rectangular",
                "description": "A rectangular matrix with more rows than columns",
                "matrix": [[1, 2], [3, 4], [5, 6]],
            },
            {
                "name": "3×4 Full Row Rank",
                "description": "3×4 matrix with full row rank",
                "matrix": [[1, 0, 2, 1], [0, 1, 1, 2], [0, 0, 0, 0]],
            },
            {
                "name": "2×2 Singular",
                "description": "A singular 2×2 matrix (rank 1)",
                "matrix": [[1, 2], [2, 4]],
            },
            {
                "name": "3×3 Zero Matrix",
                "description": "The zero matrix (rank 0)",
                "matrix": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
            },
            {
                "name": "2×5 Wide Matrix",
                "description": "A wide 2×5 matrix",
                "matrix": [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]],
            },
            {
                "name": "5×2 Tall Matrix",
                "description": "A tall 5×2 matrix",
                "matrix": [[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]],
            },
        ]
    }


@app.get("/api/cache/stats")
async def cache_stats():
    """
    Get cache statistics.
    Useful for monitoring cache performance.
    """
    return {
        "current_size": len(computation_cache),
        "max_size": settings.cache_size,
        "ttl_seconds": settings.cache_ttl,
        "utilization_percent": (len(computation_cache) / settings.cache_size) * 100,
    }


@app.delete("/api/cache/clear")
async def clear_cache():
    """
    Clear the computation cache.
    Useful for testing or if cache becomes stale.
    """
    computation_cache.clear()
    logger.info("Cache cleared manually")
    return {"message": "Cache cleared successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development"
    )

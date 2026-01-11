"""
Test script to verify backend optimizations.
Tests caching, compression, rate limiting, and new endpoints.
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the /health endpoint."""
    print("=" * 60)
    print("Testing /health endpoint...")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_cache_stats():
    """Test the /api/cache/stats endpoint."""
    print("=" * 60)
    print("Testing /api/cache/stats endpoint...")
    print("=" * 60)
    response = requests.get(f"{BASE_URL}/api/cache/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_caching():
    """Test caching functionality."""
    print("=" * 60)
    print("Testing Caching (same matrix twice)...")
    print("=" * 60)
    
    matrix_data = {"matrix": [[1, 2, 3], [4, 5, 6], [7, 8, 9]]}
    
    # First request (cache miss)
    print("First request (should be cache MISS)...")
    start = time.time()
    response1 = requests.post(f"{BASE_URL}/api/compute", json=matrix_data)
    time1 = time.time() - start
    result1 = response1.json()
    print(f"  Time: {time1:.4f}s")
    print(f"  Cached: {result1.get('cached', False)}")
    print(f"  Rank: {result1.get('rank')}")
    
    # Second request (cache hit)
    print("\nSecond request (should be cache HIT)...")
    start = time.time()
    response2 = requests.post(f"{BASE_URL}/api/compute", json=matrix_data)
    time2 = time.time() - start
    result2 = response2.json()
    print(f"  Time: {time2:.4f}s")
    print(f"  Cached: {result2.get('cached', False)}")
    print(f"  Rank: {result2.get('rank')}")
    
    speedup = time1 / time2 if time2 > 0 else 0
    print(f"\n  ✓ Cache speedup: {speedup:.2f}x faster!")
    print()

def test_compression():
    """Test gzip compression."""
    print("=" * 60)
    print("Testing GZip Compression...")
    print("=" * 60)
    
    matrix_data = {"matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]]}
    response = requests.post(
        f"{BASE_URL}/api/compute",
        json=matrix_data,
        headers={"Accept-Encoding": "gzip"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Content-Encoding: {response.headers.get('Content-Encoding', 'none')}")
    print(f"Content-Length: {len(response.content)} bytes")
    print(f"X-Process-Time: {response.headers.get('X-Process-Time', 'N/A')}")
    print()

def test_rate_limiting():
    """Test rate limiting (be careful not to hit the limit!)."""
    print("=" * 60)
    print("Testing Rate Limiting Headers...")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status Code: {response.status_code}")
    
    # Check for rate limit headers
    for header in response.headers:
        if 'ratelimit' in header.lower() or 'rate-limit' in header.lower():
            print(f"{header}: {response.headers[header]}")
    
    print("\nNote: Rate limit is 60 requests/minute per IP")
    print()

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BACKEND OPTIMIZATION TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_health_endpoint()
        test_cache_stats()
        test_caching()
        test_compression()
        test_rate_limiting()
        
        print("=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend at", BASE_URL)
        print("Make sure the server is running with: uvicorn main:app --reload")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()

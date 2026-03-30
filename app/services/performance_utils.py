import time
import logging
import functools
import os
from datetime import datetime

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("performance")

def measure_performance(func):
    """Decorator to measure and log function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Allow disabling timing via ENV
        if os.environ.get("DEBUG_PERFORMANCE", "True").lower() != "true":
            return func(*args, **kwargs)
            
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        logger.info(f"PERF: {func.__name__} executed in {duration:.4f} seconds")
        return result
    return wrapper

class ResultCache:
    """Simple in-memory cache for processed results to avoid redundant PDF parsing."""
    _cache = {}
    
    @classmethod
    def get(cls, file_hash):
        return cls._cache.get(file_hash)
    
    @classmethod
    def set(cls, file_hash, data):
        # Simple TTL could be added here, but for this app result, session is enough
        cls._cache[file_hash] = {
            "data": data,
            "timestamp": datetime.now()
        }
        # Keep cache size small
        if len(cls._cache) > 20:
            # Pop oldest
            oldest = min(cls._cache.keys(), key=lambda k: cls._cache[k]["timestamp"])
            cls._cache.pop(oldest)

import hashlib

def get_file_hash(file_bytes):
    """Generates a SHA256 hash for the given file content."""
    return hashlib.sha256(file_bytes).hexdigest()

def get_file_stats(filepath):
    """Helper to generate a unique key for files (path + size + mtime)."""
    if not os.path.exists(filepath):
        return None
    stats = os.stat(filepath)
    return f"{filepath}_{stats.st_size}_{stats.st_mtime}"

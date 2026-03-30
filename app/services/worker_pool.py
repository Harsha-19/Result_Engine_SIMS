from concurrent.futures import ThreadPoolExecutor
import os

# Initialize a global worker pool for CPU/IO tasks
# Number of workers can be tuned for Render (usually 2-4 for a basic instance)
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 4))
executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

def run_in_background(func, *args, **kwargs):
    """Offloads a function to the global thread pool."""
    return executor.submit(func, *args, **kwargs)

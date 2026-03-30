import multiprocessing
import os

# Gunicorn configuration file for Render deployment
# Ref: https://docs.gunicorn.org/en/stable/configure.html

bind = "0.0.0.0:" + os.environ.get("PORT", "5000")

# High performance settings for a CPU-bound extraction task
# Generally, 2-4 workers per core is recommended
# Render basic instance usually has 0.1 - 2 CPUs. 
# We optimize for a responsive dashboard.
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
threads = int(os.environ.get("GUNICORN_THREADS", 2))

# Timeout to allow longer PDF processing for large files
timeout = 120

# Workers to handle requests concurrently
worker_class = "gthread"

# Log to stdout for Render logs
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload app code to share memory between workers
preload_app = True

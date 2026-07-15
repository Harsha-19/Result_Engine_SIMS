# Timeout Root Cause Analysis

## Executive Summary
The `net::ERR_CONNECTION_TIMED_OUT` on the React frontend when calling `/upload` is caused by a combination of a stale IP address in the frontend configuration and a severe CPU-bound blocking issue in the backend that monopolizes the Python Global Interpreter Lock (GIL).

## 1. Primary Root Cause: Stale IP Configuration
The frontend is explicitly configured to use `http://10.142.66.21:5000` via `.env`.
Network diagnostics (`ipconfig`) reveal that this machine's actual IP is `10.92.209.212`. The IP `10.142.66.21` is unreachable, meaning the browser's TCP handshake (SYN packets) fails, resulting directly in `ERR_CONNECTION_TIMED_OUT`. 
- **Why it "sometimes" works**: If the system moves between networks (e.g., VPN, office Wi-Fi), the IP may occasionally be correct, leading to intermittent success.

## 2. Secondary Root Cause: GIL Blocking & Performance
When the request does reach the server, it takes **25.7 seconds** to process.
Specifically, `extract_pdf_data` takes **24.3 seconds**.
Because `pdfplumber` is CPU-bound, it heavily utilizes the CPU and holds the Python **Global Interpreter Lock (GIL)**.
While the GIL is held for 24 seconds:
- The Flask development server cannot process other incoming requests.
- Health checks (`/health`) will hang.
- Additional upload requests will queue up. If the queue overflows, the OS will drop connections, which also leads to `ERR_CONNECTION_TIMED_OUT` under load.

## Permanent Code Fixes Required

### 1. Fix Frontend Connectivity
Change `UI/.env` to use localhost to make it resilient to network changes:
```env
VITE_API_URL=http://localhost:5000
```

### 2. Bypass the GIL (Backend)
Without modifying the core extraction logic, we can keep the server responsive by offloading the CPU-bound task to a separate process.
In `app/services/worker_pool.py`:
```python
# Change ThreadPoolExecutor to ProcessPoolExecutor
from concurrent.futures import ProcessPoolExecutor
executor = ProcessPoolExecutor(max_workers=MAX_WORKERS)
```
In `api.py` upload route:
```python
# Use the worker pool to run extraction in a separate process, freeing the GIL
future = run_in_background(process_results, marks_path, caste_path, ui_meta)
results = future.result()
```

### 3. Enable Result Caching
In `app/main.py`:
```python
# Uncomment to enable instant responses for identical files
cached_core = ResultCache.get(cache_key)
```

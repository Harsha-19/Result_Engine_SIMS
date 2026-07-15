# Performance Report: Long Running Operations

## Function Execution Timings
We ran a complete performance profile on the backend using the sample files (PDF size: 1.31 MB, Excel size: 44.2 KB). 

| Operation | Component | Execution Time | Evaluation |
| :--- | :--- | :--- | :--- |
| **`upload()`** | `api.py` | 24.67s | ⚠ **CRITICAL** (Exceeds 5s threshold) |
| **`extract_pdf_metadata()`** | `app.main` | 0.32s | ✓ Fast |
| **`extract_pdf_data()`** | `pdf_extractor`| 24.32s | ⚠ **CRITICAL** (Exceeds 5s threshold) |
| **`extract_excel_data()`** | `app.main` | 0.00s* | ✓ Fast (*cached internally, 1.08s first run) |
| **`process_results()`** | `app.main` | 24.65s | ⚠ **CRITICAL** (Bottlenecked by PDF extraction) |

## Root Cause for Execution Exceeding 5 Seconds
The bottleneck is explicitly isolated to **`extract_pdf_data()`**.
- **Reason:** The function iterates through every single page of the PDF sequentially using `pdfplumber.extract_text()`.
- `pdfplumber` relies on `pdfminer.six`, which performs highly complex spatial and visual text parsing on the CPU.
- Because Python execution is bound by the **Global Interpreter Lock (GIL)**, this long-running CPU operation completely locks the Python process for 24+ seconds.

### The Network Implication
When the backend process GIL is blocked for ~25 seconds:
1. TCP `accept()` loops and other Flask background threads cannot execute.
2. Load balancers, Proxies, and corporate firewalls consider the connection idle or dead.
3. Client browsers give up on the TCP handshake if the backlog is full, returning `net::ERR_CONNECTION_TIMED_OUT`.

## Working & Broken Components
- ✓ **Working:** Pandas Excel Extraction (`extract_excel_data`), Metadata regex parsing (`extract_pdf_metadata`)
- ⚠ **Slow Components:** `pdfplumber` full-text extraction logic (`extract_pdf_data`)
- ✗ **Broken Components:** Single-threaded execution architecture on the `/upload` endpoint, making the slow PDF parsing fatal to server health.

# API Response Report
## Overview
The `POST /upload` response body was inspected to guarantee the frontend receives accurately structured payloads.

## ✅ Working Components
- **Data Blocks**: The API safely returns all standard required payload blocks:
  - `metadata`
  - `summary`
  - `rankers`
  - `subjects`
  - `demographics`
  - `centum`
  - `total`
- **Data Integrity**: Arrays are populated. No arbitrary missing keys, empty standard demographic mappings, or broken schema types.

## ⚠️ Suspicious Components
- **Student Totals**: Total returned mapped to `total: 80`, which relies upon the backend match intersections. Ensure backend logic validates matching properly over the dataset.

## ❌ Broken Components
- **Validation Block Caching Mismatch**: The `validation` key in the response payload returned an empty object `{}`. 
  - **Root Cause**: The Flask `ResultCache` layer stored the computation from an earlier state before the latest backend modifications (where `missingStudents` was added to the validation dict) were applied. As a result, the old cached payload was served instantly. 
  - **Suggested Fix**: Clear the backend caching layer (e.g. `ResultCache.clear()`), invalidate the specific `cache_key` for these file hashes, or simply touch the test files to break the cache and force a fresh parsing cycle.

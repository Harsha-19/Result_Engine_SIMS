# Result Engine SIMS

Result Engine SIMS is a comprehensive web application designed to automate the process of analyzing university exam results. It extracts student marks from PDF result sheets, correlates them with demographic data (such as caste categories) from Excel files, and generates formatted Result Analysis reports in DOCX format.

## Key Features

- **Automated Data Extraction:** Parses student results directly from official PDF documents using `pdfplumber`.
- **Demographic Analysis:** Filters and categorizes student performance based on caste (General, SC, ST, OBC) using uploaded Excel sheets.
- **Detailed Reporting:** Generates comprehensive result summaries, top rankers lists, subject-wise performance, and demographic breakdowns.
- **DOCX Generation:** Exports the finalized analysis into an "Approved Result Analysis" DOCX template using `python-docx`.
- **Modern UI:** Built with React, Vite, and Tailwind CSS for a seamless and responsive user experience.

## Tech Stack

**Frontend (`/UI`):**
- React 18
- Vite
- TypeScript
- Tailwind CSS
- shadcn/ui & Radix UI (for components)
- Recharts (for data visualization)

**Backend (`/backend`):**
- Python 3
- Flask (API Framework)
- Pandas & OpenPyXL (Data manipulation & Excel handling)
- pdfplumber (PDF data extraction)
- python-docx (DOCX report generation)

## Prerequisites

Ensure you have the following installed on your system:
- [Node.js](https://nodejs.org/) (v18 or higher recommended)
- [Python 3.8+](https://www.python.org/)
- `pip` (Python package installer)

## Getting Started

### 1. Running the Backend

The backend is built with Flask and serves as the data processing engine.

```bash
# Navigate to the backend directory
cd backend

# (Optional but recommended) Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install the required Python packages
pip install -r requirements.txt

# Start the Flask API server
python api.py
```
The backend API will start running on `http://localhost:5000`.

### 2. Running the Frontend

The frontend is a Vite-powered React application. Open a **new terminal** and run the following commands:

```bash
# Navigate to the UI directory
cd UI

# Install dependencies
npm install

# Start the development server
npm run dev
```
The UI development server will start, typically accessible at `http://localhost:5173` or similar.

## API Endpoints Overview

- `GET /health` - Health check for the API.
- `POST /upload-caste-filter` - Uploads a PDF and filters results by the provided caste.
- `POST /upload` - Uploads both the marks PDF and the caste Excel file, processes the data, and returns JSON analysis.
- `GET /generate-report` / `POST /download` - Generates and downloads the final Approved Result Analysis DOCX file based on uploaded data.
- `GET /files` - Lists uploaded PDF files.
- `DELETE /files/<filename>` - Deletes a specific uploaded file.

## Project Structure

```
Result_Engine_SIMS/
├── backend/                  # Python Flask API & Data Processing
│   ├── api.py                # Main API routes
│   ├── requirements.txt      # Python dependencies
│   ├── app/                  # Core processing logic (extractors, services)
│   ├── templates/            # DOCX templates for report generation
│   └── uploads/              # Temporary storage for uploaded files
├── UI/                       # React Frontend
│   ├── src/                  # React source code and components
│   ├── package.json          # Node dependencies and scripts
│   ├── tailwind.config.ts    # Tailwind styling configuration
│   └── index.html            # Entry HTML file
└── README.md                 # Project documentation (this file)
```

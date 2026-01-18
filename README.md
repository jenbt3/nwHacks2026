# Cognitive Bridge - Local Setup Guide

This project consists of a FastAPI backend and a dashboard frontend. Here's how to run it locally.

## Prerequisites

- Python 3.8+ 
- pip (Python package manager)
- API keys for:
  - Google Gemini API
  - ElevenLabs API

## Setup Steps

### 1. Install Dependencies

Create a virtual environment (recommended):

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

**Note:** If you're running on a Raspberry Pi, use `requirements_pi.txt` instead.

### 2. Configure Environment Variables

Create a `.env` file in the `backend/` directory with your API keys:

```bash
cd backend
touch .env
```

Add the following to `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

**How to get API keys:**
- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **ElevenLabs API Key**: Get from [ElevenLabs Dashboard](https://elevenlabs.io/)

### 3. Run the Backend

From the project root directory:

```bash
# Make sure you're in the project root
cd /Users/jennifertran/nwHacks2026-2

# Run the FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or use Python directly:

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at:
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs` (FastAPI auto-generated Swagger UI)

### 4. Run the Dashboard

Open the dashboard in your browser. You can either:

**Option A: Serve with a simple HTTP server** (recommended to avoid CORS issues)

```bash
# Using Python's built-in server
cd dashboard
python3 -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

**Option B: Serve with npx (if you have Node.js)**
```bash
cd dashboard
npx serve
```

## Project Structure

```
.
├── backend/           # FastAPI backend
│   ├── api/          # API routes (people, alerts, scripts)
│   ├── core/         # Configuration and WebSocket manager
│   ├── db/           # Database models and schemas
│   ├── data/         # SQLite database storage
│   ├── services/     # External API integrations (Gemini, ElevenLabs)
│   └── main.py       # FastAPI application entry point
├── dashboard/        # Frontend dashboard (HTML/CSS/JS)
│   ├── index.html
│   ├── main.js
│   └── styles.css
└── edge_pi/          # Edge device code (for Raspberry Pi)
```

## Database

The application uses SQLite, which is automatically created at `backend/data/bridge.db` on first run. The database schema is automatically initialized when the FastAPI server starts.

## Features

- **Visitor Recognition**: Enroll visitors with face recognition
- **Real-time Alerts**: WebSocket-based alerts for wandering detection
- **Camera Control**: Joystick-based pan-tilt control (requires hardware)
- **Memory Anchors**: Store contextual information about visitors

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, change it:
```bash
uvicorn backend.main:app --reload --port 8080
```
Then update `dashboard/main.js` to use `localhost:8080` instead of `localhost:8000`.

### Missing API Keys Error
Make sure your `.env` file is in the `backend/` directory and contains valid API keys.

### Database Issues
Delete `backend/data/bridge.db` to reset the database. It will be recreated on next startup.

### CORS Issues
The backend already has CORS middleware configured to allow all origins. If you're still having issues, ensure you're serving the dashboard over HTTP, not just opening the HTML file directly.

## Development

- The backend auto-reloads when you use the `--reload` flag with uvicorn
- Check the FastAPI docs at `http://localhost:8000/docs` to test API endpoints
- Database models are in `backend/db/models.py`
- API routes are in `backend/api/`

# Movie Recommendation System

An end-to-end, AI-powered movie discovery and recommendation platform featuring a luxury glassmorphic web UI built with **Streamlit** and a high-performance **FastAPI** backend driven by **TF-IDF content-based filtering** and **TMDB API integration**.

---

## 🌐 Live Demos & Deployment Links

- 🎨 **Frontend Web App (Streamlit Cloud)**: [Deploy Streamlit App](https://share.streamlit.io/)
- ⚡ **Backend REST API (Render)**: [`https://movie-recommendation-system-ho30.onrender.com`](https://movie-recommendation-system-ho30.onrender.com)
- 📖 **Interactive API Docs (Swagger UI)**: [`https://movie-recommendation-system-ho30.onrender.com/docs`](https://movie-recommendation-system-ho30.onrender.com/docs)

---

## ✨ Features

- 🧠 **Content-Based Recommendation Engine**: Leverages Scikit-Learn TF-IDF vectorization and cosine similarity matching over preprocessed movie datasets.
- 🎭 **Mood & Vibe Picker**: Instant discovery tailored to specific moods (*Mind-Bending Sci-Fi*, *Adrenaline Action*, *Cozy Feel-Good*, *Late-Night Horror*, *Heartfelt Romance*).
- 🎬 **Complete Movie Details**: Displays TMDB ratings, release dates, high-resolution backdrops, cast profiles, watch providers, and official YouTube trailers.
- 📌 **Personalized Watchlist**: Fully persistent watchlist functionality powered by SQLite (`cinepulse.db`).
- 💎 **Luxury Responsive UI**: Custom CSS glassmorphism, responsive grid layout, and sleek animations built with Google's *Outfit* typography.
- 🔍 **Instant Search & Autocomplete**: Real-time TMDB title matching with instant preview suggestions.

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit, Custom CSS3 / HTML5
- **Backend API**: FastAPI, Uvicorn, Pydantic, HTTPX, SQLite3
- **Machine Learning & Data Science**: Scikit-Learn (`TfidfVectorizer`), Pandas, NumPy, SciPy, Pickle
- **External API**: The Movie Database (TMDB API v3)
- **Hosting & Cloud**: Render (FastAPI Web Service), Streamlit Community Cloud (Frontend UI)

---

## 📁 Repository Structure

```
Movie-Recommendation-System/
├── app.py                # Streamlit Frontend Web Application
├── main.py               # FastAPI Backend Service & Routes
├── requirements.txt      # Project Dependencies
├── df.pkl                # Preprocessed Movies Dataframe
├── indices.pkl           # Movie Title to Index Mapping
├── tfidf.pkl             # Trained TF-IDF Vectorizer
├── tfidf_matrix.pkl      # Precomputed TF-IDF Matrix
├── cinepulse.db          # Local SQLite Watchlist Database
└── README.md             # Project Documentation
```

---

## 🚀 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/tilaktmg987/Movie-Recommendation-System.git
cd Movie-Recommendation-System
```

### 2. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
TMDB_API_KEY=your_tmdb_api_key_here
API_BASE=http://127.0.0.1:8000
```

---

## 💻 Running Locally

### Step 1: Start FastAPI Backend
```bash
uvicorn main:app --reload --port 8000
```
*API will be available at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.*

### Step 2: Start Streamlit Frontend
Open a second terminal window and run:
```bash
streamlit run app.py
```
*Frontend will automatically open in your browser at `http://localhost:8501`.*

---

## ☁️ Deployment Guide

### Deploying Backend on Render
1. Create a **New Web Service** on [Render](https://render.com).
2. Connect repository `tilaktmg987/Movie-Recommendation-System`.
3. Set **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add **Environment Variable**: `TMDB_API_KEY = your_key`

### Deploying Frontend on Streamlit Cloud
1. Connect repository on [Streamlit Community Cloud](https://share.streamlit.io/).
2. Set **Main file path**: `app.py`
3. Add **Secrets** under Advanced Settings:
   ```toml
   API_BASE = "https://movie-recommendation-system-ho30.onrender.com"
   ```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

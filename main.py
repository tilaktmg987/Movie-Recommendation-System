import os
import pickle
import asyncio
import sqlite3
from typing import Optional, List, Dict, Any, Tuple

import numpy as np
import pandas as pd
import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# =========================
# ENV & CONFIG
# =========================
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG_500 = "https://image.tmdb.org/t/p/w500"
TMDB_IMG_ORIGINAL = "https://image.tmdb.org/t/p/original"
TMDB_IMG_PROFILE = "https://image.tmdb.org/t/p/w185"

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY missing. Put it in .env as TMDB_API_KEY=xxxx")

# =========================
# FASTAPI APP SETUP
# =========================
app = FastAPI(title="Movie Recommendation System API", version="4.5")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# SQLITE DATABASE SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cinepulse.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            poster_url TEXT,
            release_date TEXT,
            vote_average REAL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# PICKLE GLOBALS & CACHE
# =========================
DF_PATH = os.path.join(BASE_DIR, "df.pkl")
INDICES_PATH = os.path.join(BASE_DIR, "indices.pkl")
TFIDF_MATRIX_PATH = os.path.join(BASE_DIR, "tfidf_matrix.pkl")
TFIDF_PATH = os.path.join(BASE_DIR, "tfidf.pkl")

df: Optional[pd.DataFrame] = None
indices_obj: Any = None
tfidf_matrix: Any = None
tfidf_obj: Any = None

TITLE_TO_IDX: Optional[Dict[str, int]] = None
CARD_CACHE: Dict[str, Optional["TMDBMovieCard"]] = {}

# =========================
# DATA MODELS
# =========================
class TMDBMovieCard(BaseModel):
    tmdb_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None
    overview: Optional[str] = None

class TMDBMovieDetails(BaseModel):
    tmdb_id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    genres: List[dict] = []
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    tagline: Optional[str] = None
    runtime: Optional[int] = None

class CastMember(BaseModel):
    person_id: int
    name: str
    character: Optional[str] = None
    profile_url: Optional[str] = None

class WatchProvider(BaseModel):
    provider_id: int
    provider_name: str
    logo_url: Optional[str] = None

class TrailerInfo(BaseModel):
    key: str
    name: str
    site: str
    youtube_url: str

class TFIDFRecItem(BaseModel):
    title: str
    score: float
    tmdb: Optional[TMDBMovieCard] = None

class SearchBundleResponse(BaseModel):
    query: str
    movie_details: TMDBMovieDetails
    tfidf_recommendations: List[TFIDFRecItem]
    genre_recommendations: List[TMDBMovieCard]
    similar_recommendations: List[TMDBMovieCard] = []
    cast: List[CastMember] = []
    providers: List[WatchProvider] = []
    trailer: Optional[TrailerInfo] = None

class WatchlistItem(BaseModel):
    tmdb_id: int
    title: str
    poster_url: Optional[str] = None
    release_date: Optional[str] = None
    vote_average: Optional[float] = None

# =========================
# UTILS & HELPERS
# =========================
def _norm_title(t: str) -> str:
    return str(t).strip().lower()

def _safe_int(val, default: int = 12) -> int:
    if hasattr(val, "default"):
        val = val.default
    try:
        return int(val)
    except Exception:
        return default

def make_img_url(path: Optional[str], size: str = "w500") -> Optional[str]:
    if not path:
        return None
    if size == "original":
        base = TMDB_IMG_ORIGINAL
    elif size == "profile":
        base = TMDB_IMG_PROFILE
    else:
        base = TMDB_IMG_500
    return f"{base}{path}"

async def tmdb_get(path: str, params: Dict[str, Any]) -> Dict[str, Any]:
    q = dict(params)
    q["api_key"] = TMDB_API_KEY

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(f"{TMDB_BASE}{path}", params=q)
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"TMDB request error: {type(e).__name__}",
        )

    if r.status_code != 200:
        raise HTTPException(
            status_code=502, detail=f"TMDB error {r.status_code}: {r.text}"
        )

    return r.json()

async def tmdb_cards_from_results(
    results: List[dict], limit: int = 20
) -> List[TMDBMovieCard]:
    limit_int = _safe_int(limit, 20)
    out: List[TMDBMovieCard] = []
    for m in (results or [])[:limit_int]:
        if not m.get("id"):
            continue
        out.append(
            TMDBMovieCard(
                tmdb_id=int(m["id"]),
                title=m.get("title") or m.get("name") or "Untitled",
                poster_url=make_img_url(m.get("poster_path")),
                release_date=m.get("release_date"),
                vote_average=round(float(m.get("vote_average", 0)), 1) if m.get("vote_average") else None,
                overview=m.get("overview", ""),
            )
        )
    return out

async def tmdb_movie_details(movie_id: int) -> TMDBMovieDetails:
    data = await tmdb_get(f"/movie/{movie_id}", {"language": "en-US"})
    return TMDBMovieDetails(
        tmdb_id=int(data["id"]),
        title=data.get("title") or "",
        overview=data.get("overview"),
        release_date=data.get("release_date"),
        poster_url=make_img_url(data.get("poster_path")),
        backdrop_url=make_img_url(data.get("backdrop_path"), size="original"),
        genres=data.get("genres", []) or [],
        vote_average=round(float(data.get("vote_average", 0)), 1) if data.get("vote_average") else None,
        vote_count=data.get("vote_count"),
        tagline=data.get("tagline"),
        runtime=data.get("runtime"),
    )

async def tmdb_movie_credits(movie_id: int, limit: int = 8) -> List[CastMember]:
    try:
        data = await tmdb_get(f"/movie/{movie_id}/credits", {"language": "en-US"})
        cast = data.get("cast", [])[:limit]
        out = []
        for c in cast:
            out.append(
                CastMember(
                    person_id=int(c["id"]),
                    name=c.get("name", "Unknown"),
                    character=c.get("character"),
                    profile_url=make_img_url(c.get("profile_path"), size="profile"),
                )
            )
        return out
    except Exception:
        return []

async def tmdb_movie_providers(movie_id: int) -> List[WatchProvider]:
    try:
        data = await tmdb_get(f"/movie/{movie_id}/watch/providers", {})
        results = data.get("results", {})
        us = results.get("US") or results.get("GB") or {}
        flatrate = us.get("flatrate", [])
        out = []
        for p in flatrate:
            out.append(
                WatchProvider(
                    provider_id=int(p["provider_id"]),
                    provider_name=p.get("provider_name", ""),
                    logo_url=make_img_url(p.get("logo_path")),
                )
            )
        return out
    except Exception:
        return []

async def tmdb_movie_trailer(movie_id: int) -> Optional[TrailerInfo]:
    try:
        data = await tmdb_get(f"/movie/{movie_id}/videos", {"language": "en-US"})
        results = data.get("results", [])
        trailers = [
            v for v in results 
            if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser")
        ]
        if not trailers and results:
            trailers = [v for v in results if v.get("site") == "YouTube"]
        if trailers:
            t = trailers[0]
            key = t["key"]
            return TrailerInfo(
                key=key,
                name=t.get("name", "Official Trailer"),
                site="YouTube",
                youtube_url=f"https://www.youtube.com/watch?v={key}",
            )
        return None
    except Exception:
        return None

async def tmdb_search_movies(query: str, page: int = 1) -> Dict[str, Any]:
    return await tmdb_get(
        "/search/movie",
        {
            "query": query,
            "include_adult": "false",
            "language": "en-US",
            "page": page,
        },
    )

async def tmdb_search_first(query: str) -> Optional[dict]:
    data = await tmdb_search_movies(query=query, page=1)
    results = data.get("results", [])
    return results[0] if results else None

async def tmdb_similar_movies(movie_id: int, limit: int = 16) -> List[TMDBMovieCard]:
    try:
        data = await tmdb_get(f"/movie/{movie_id}/recommendations", {"language": "en-US", "page": 1})
        results = data.get("results", [])
        if not results:
            data = await tmdb_get(f"/movie/{movie_id}/similar", {"language": "en-US", "page": 1})
            results = data.get("results", [])
        cards = await tmdb_cards_from_results(results, limit=limit)
        return [c for c in cards if c.tmdb_id != movie_id]
    except Exception:
        return []

# =========================
# TF-IDF HELPERS
# =========================
def build_title_to_idx_map(indices: Any) -> Dict[str, int]:
    title_to_idx: Dict[str, int] = {}
    if isinstance(indices, dict):
        for k, v in indices.items():
            title_to_idx[_norm_title(k)] = int(v)
        return title_to_idx

    try:
        for k, v in indices.items():
            title_to_idx[_norm_title(k)] = int(v)
        return title_to_idx
    except Exception:
        raise RuntimeError("indices.pkl format unsupported")

def get_local_idx_by_title(title: str) -> Optional[int]:
    global TITLE_TO_IDX
    if TITLE_TO_IDX is None:
        return None
    key = _norm_title(title)
    if key in TITLE_TO_IDX:
        return int(TITLE_TO_IDX[key])

    # Fuzzy / substring match fallback
    for k, idx in TITLE_TO_IDX.items():
        if len(k) > 3 and (key in k or k in key):
            return int(idx)
    return None

def tfidf_recommend_titles(
    query_title: str, top_n: int = 12
) -> List[Tuple[str, float]]:
    global df, tfidf_matrix
    if df is None or tfidf_matrix is None:
        return []

    idx = get_local_idx_by_title(query_title)
    if idx is None:
        return []

    qv = tfidf_matrix[idx]
    if getattr(qv, "nnz", 0) == 0:
        return []

    scores = (tfidf_matrix @ qv.T).toarray().ravel()
    scores[idx] = 0.0

    order = np.argsort(-scores)

    out: List[Tuple[str, float]] = []
    for i in order:
        score_val = float(scores[int(i)])
        if score_val <= 0.01:
            break
        try:
            title_i = str(df.iloc[int(i)]["title"])
        except Exception:
            continue
        out.append((title_i, round(score_val, 4)))
        if len(out) >= top_n:
            break
    return out

async def attach_tmdb_card_by_title(title: str) -> Optional[TMDBMovieCard]:
    norm = _norm_title(title)
    if norm in CARD_CACHE:
        return CARD_CACHE[norm]
    try:
        m = await tmdb_search_first(title)
        if not m:
            CARD_CACHE[norm] = None
            return None
        card = TMDBMovieCard(
            tmdb_id=int(m["id"]),
            title=m.get("title") or title,
            poster_url=make_img_url(m.get("poster_path")),
            release_date=m.get("release_date"),
            vote_average=round(float(m.get("vote_average", 0)), 1) if m.get("vote_average") else None,
            overview=m.get("overview", ""),
        )
        CARD_CACHE[norm] = card
        return card
    except Exception:
        CARD_CACHE[norm] = None
        return None

# =========================
# LIFECYCLE EVENT & CLEANUP
# =========================
@app.on_event("startup")
def load_pickles():
    global df, indices_obj, tfidf_matrix, tfidf_obj, TITLE_TO_IDX

    with open(DF_PATH, "rb") as f:
        df = pickle.load(f)

    with open(INDICES_PATH, "rb") as f:
        indices_obj = pickle.load(f)

    with open(TFIDF_MATRIX_PATH, "rb") as f:
        tfidf_matrix = pickle.load(f)

    with open(TFIDF_PATH, "rb") as f:
        tfidf_obj = pickle.load(f)

    TITLE_TO_IDX = build_title_to_idx_map(indices_obj)

    try:
        feature_names = tfidf_obj.get_feature_names_out()
        bad_tokens = {"nan", "null", "none"}
        bad_indices = [i for i, feat in enumerate(feature_names) if str(feat).lower() in bad_tokens]
        if bad_indices:
            csc = tfidf_matrix.tocsc()
            for b_idx in bad_indices:
                csc.data[csc.indptr[b_idx]:csc.indptr[b_idx+1]] = 0
            tfidf_matrix = csc.tocsr()
            tfidf_matrix.eliminate_zeros()
    except Exception as e:
        print(f"Matrix cleanup warning: {e}")

    if df is None or "title" not in df.columns:
        raise RuntimeError("df.pkl must contain a DataFrame with a 'title' column")

# =========================
# ROUTE HANDLERS
# =========================
@app.get("/health")
def health():
    return {"status": "ok", "cached_cards": len(CARD_CACHE)}

# ---------- WATCHLIST ROUTES (SQLITE) ----------
@app.get("/watchlist", response_model=List[WatchlistItem])
def get_watchlist():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT tmdb_id, title, poster_url, release_date, vote_average FROM watchlist ORDER BY added_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [
        WatchlistItem(
            tmdb_id=r[0], title=r[1], poster_url=r[2], release_date=r[3], vote_average=r[4]
        )
        for r in rows
    ]

@app.post("/watchlist")
def add_to_watchlist(item: WatchlistItem):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO watchlist (tmdb_id, title, poster_url, release_date, vote_average)
        VALUES (?, ?, ?, ?, ?)
    """, (item.tmdb_id, item.title, item.poster_url, item.release_date, item.vote_average))
    conn.commit()
    conn.close()
    return {"status": "added", "tmdb_id": item.tmdb_id}

@app.delete("/watchlist/{tmdb_id}")
def remove_from_watchlist(tmdb_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE tmdb_id = ?", (tmdb_id,))
    conn.commit()
    conn.close()
    return {"status": "removed", "tmdb_id": tmdb_id}

@app.get("/watchlist/check/{tmdb_id}")
def check_watchlist(tmdb_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM watchlist WHERE tmdb_id = ?", (tmdb_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return {"in_watchlist": exists}

# ---------- MOOD / VIBE RECOMMENDATIONS ----------
MOOD_GENRE_MAP = {
    "mind_bending": ("878,9648", "vote_average.desc"),
    "action": ("28,12", "popularity.desc"),
    "cozy": ("35,10751", "popularity.desc"),
    "horror": ("27,53", "popularity.desc"),
    "romance": ("10749", "popularity.desc"),
}

@app.get("/home/mood", response_model=List[TMDBMovieCard])
async def get_mood_feed(mood: str = Query("mind_bending"), limit: int = Query(24)):
    limit_int = _safe_int(limit, 24)
    genres, sort_by = MOOD_GENRE_MAP.get(mood, ("878", "popularity.desc"))
    discover = await tmdb_get(
        "/discover/movie",
        {
            "with_genres": genres,
            "sort_by": sort_by,
            "vote_count.gte": 300,
            "language": "en-US",
            "page": 1,
        },
    )
    return await tmdb_cards_from_results(discover.get("results", []), limit=limit_int)

# ---------- ACTOR FILMOGRAPHY ROUTE ----------
@app.get("/person/{person_id}/movies", response_model=List[TMDBMovieCard])
async def get_actor_movies(person_id: int, limit: int = Query(24)):
    limit_int = _safe_int(limit, 24)
    data = await tmdb_get(f"/person/{person_id}/movie_credits", {"language": "en-US"})
    cast_movies = data.get("cast", [])
    cast_movies.sort(key=lambda x: x.get("popularity", 0), reverse=True)
    return await tmdb_cards_from_results(cast_movies, limit=limit_int)

# ---------- HOME FEED (TMDB) ----------
@app.get("/home", response_model=List[TMDBMovieCard])
async def home(
    category: str = Query("popular"),
    limit: int = Query(24, ge=1, le=50),
):
    try:
        limit_int = _safe_int(limit, 24)
        if category == "trending":
            data = await tmdb_get("/trending/movie/day", {"language": "en-US"})
            return await tmdb_cards_from_results(data.get("results", []), limit=limit_int)

        if category not in {"popular", "top_rated", "upcoming", "now_playing"}:
            raise HTTPException(status_code=400, detail="Invalid category")

        data = await tmdb_get(f"/movie/{category}", {"language": "en-US", "page": 1})
        return await tmdb_cards_from_results(data.get("results", []), limit=limit_int)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Home route failed: {e}")

@app.get("/tmdb/search")
async def tmdb_search(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1, le=10),
):
    return await tmdb_search_movies(query=query, page=page)

@app.get("/movie/id/{tmdb_id}", response_model=TMDBMovieDetails)
async def movie_details_route(tmdb_id: int):
    return await tmdb_movie_details(tmdb_id)

@app.get("/recommend/genre", response_model=List[TMDBMovieCard])
async def recommend_genre(
    tmdb_id: int = Query(...),
    limit: int = Query(18, ge=1, le=50),
):
    limit_int = _safe_int(limit, 18)
    details = await tmdb_movie_details(tmdb_id)
    if not details.genres:
        return []

    genre_id = details.genres[0]["id"]
    discover = await tmdb_get(
        "/discover/movie",
        {
            "with_genres": genre_id,
            "language": "en-US",
            "sort_by": "popularity.desc",
            "page": 1,
        },
    )
    cards = await tmdb_cards_from_results(discover.get("results", []), limit=limit_int)
    return [c for c in cards if c.tmdb_id != tmdb_id]

@app.get("/recommend/tfidf")
async def recommend_tfidf(
    title: str = Query(..., min_length=1),
    top_n: int = Query(12, ge=1, le=50),
):
    top_int = _safe_int(top_n, 12)
    recs = tfidf_recommend_titles(title, top_n=top_int)
    return [{"title": t, "score": s} for t, s in recs]

# ---------- DIRECT BUNDLE BY TMDB ID ----------
@app.get("/movie/bundle/{tmdb_id}", response_model=SearchBundleResponse)
async def movie_bundle_by_id(
    tmdb_id: int,
    tfidf_top_n: int = Query(12, ge=1, le=30),
    genre_limit: int = Query(12, ge=1, le=30),
):
    tfidf_n = _safe_int(tfidf_top_n, 12)
    g_limit = _safe_int(genre_limit, 12)

    # 1. Concurrent execution of Details, Similar, Cast, Providers, and Trailer by exact TMDB ID!
    details_task = tmdb_movie_details(tmdb_id)
    similar_task = tmdb_similar_movies(tmdb_id, limit=g_limit)
    cast_task = tmdb_movie_credits(tmdb_id, limit=8)
    providers_task = tmdb_movie_providers(tmdb_id)
    trailer_task = tmdb_movie_trailer(tmdb_id)

    details, similar_recs, cast_list, provider_list, trailer_info = await asyncio.gather(
        details_task, similar_task, cast_task, providers_task, trailer_task
    )

    # 2. TF-IDF recommendations with fuzzy title lookup & parallel card attachment
    tfidf_items: List[TFIDFRecItem] = []
    recs: List[Tuple[str, float]] = []
    try:
        recs = tfidf_recommend_titles(details.title, top_n=tfidf_n)
    except Exception:
        recs = []

    if recs:
        cards = await asyncio.gather(*[attach_tmdb_card_by_title(t) for t, s in recs])
        for (title, score), card in zip(recs, cards):
            tfidf_items.append(TFIDFRecItem(title=title, score=score, tmdb=card))

    # 3. Genre recommendations (TMDB discover by first genre)
    genre_recs: List[TMDBMovieCard] = []
    if details.genres:
        genre_id = details.genres[0]["id"]
        discover = await tmdb_get(
            "/discover/movie",
            {
                "with_genres": genre_id,
                "language": "en-US",
                "sort_by": "popularity.desc",
                "page": 1,
            },
        )
        cards = await tmdb_cards_from_results(
            discover.get("results", []), limit=g_limit
        )
        genre_recs = [c for c in cards if c.tmdb_id != details.tmdb_id]

    return SearchBundleResponse(
        query=details.title,
        movie_details=details,
        tfidf_recommendations=tfidf_items,
        genre_recommendations=genre_recs,
        similar_recommendations=similar_recs,
        cast=cast_list,
        providers=provider_list,
        trailer=trailer_info,
    )

# Backward-compatibility alias
@app.get("/movie/search", response_model=SearchBundleResponse)
async def search_bundle(
    query: str = Query(..., min_length=1),
    tfidf_top_n: int = Query(12, ge=1, le=30),
    genre_limit: int = Query(12, ge=1, le=30),
):
    best = await tmdb_search_first(query)
    if not best:
        raise HTTPException(status_code=404, detail=f"No TMDB movie found for query: {query}")
    return await movie_bundle_by_id(int(best["id"]), tfidf_top_n=tfidf_top_n, genre_limit=genre_limit)
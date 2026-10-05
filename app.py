import os
import requests
import streamlit as st

# ==========================================================
# CONFIG & PAGE SETUP
# ==========================================================
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================================
# FULLY RESPONSIVE LUXURY CINEMA STYLES
# ==========================================================
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Global Reset & Typography */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: #0B0E17 !important;
    color: #E2E8F0;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stApp { background-color: #0B0E17; }

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 3rem;
    max-width: 1440px;
}

/* Brand Navbar Header */
.brand-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #FF3B30 0%, #E50914 50%, #FF6B00 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.brand-tag {
    font-size: 0.78rem;
    font-weight: 500;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    background: rgba(255, 255, 255, 0.05);
    padding: 3px 10px;
    border-radius: 20px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Poster Card Frame */
.poster-card-frame {
    position: relative;
    border-radius: 14px;
    overflow: hidden;
    background: #151C2C;
    border: 1px solid rgba(255, 255, 255, 0.07);
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.3s ease;
    margin-bottom: 8px;
}

.poster-card-frame:hover {
    transform: translateY(-6px);
    box-shadow: 0 18px 35px -8px rgba(229, 9, 20, 0.25);
    border-color: rgba(229, 9, 20, 0.4);
}

.card-img {
    width: 100%;
    aspect-ratio: 2 / 3;
    object-fit: cover;
    display: block;
    border-radius: 14px 14px 0 0;
}

.no-poster {
    width: 100%;
    aspect-ratio: 2 / 3;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1E293B;
    color: #64748B;
    font-size: 0.9rem;
    border-radius: 14px 14px 0 0;
}

/* Badges */
.badge-container {
    position: absolute;
    top: 8px;
    left: 8px;
    right: 8px;
    display: flex;
    justify-content: space-between;
    gap: 4px;
    z-index: 10;
    pointer-events: none;
}

.badge-rating {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(8px);
    color: #FACD15;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 8px;
    border: 1px solid rgba(250, 205, 21, 0.25);
}

.badge-year {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(8px);
    color: #CBD5E1;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 3px 8px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.badge-match {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.9), rgba(5, 150, 105, 0.9));
    backdrop-filter: blur(8px);
    color: #FFFFFF;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
}

.card-info {
    padding: 10px 12px 12px 12px;
}

.card-title {
    font-size: 0.9rem;
    font-weight: 600;
    color: #F8FAFC;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    line-height: 1.3;
}

/* Cast Avatars */
.cast-card {
    text-align: center;
    padding: 8px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    margin-bottom: 8px;
}

.cast-img {
    width: 75px;
    height: 75px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto 8px auto;
    display: block;
    border: 2px solid rgba(229, 9, 20, 0.5);
}

.cast-name {
    font-size: 0.82rem;
    font-weight: 600;
    color: #F8FAFC;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.cast-char {
    font-size: 0.72rem;
    color: #94A3B8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Provider Logos */
.provider-logo {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    object-fit: cover;
    border: 1px solid rgba(255,255,255,0.15);
}

/* Hero Banner */
.hero-backdrop {
    position: relative;
    width: 100%;
    height: 340px;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.hero-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: brightness(0.45);
}

.hero-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 2.5rem;
    background: linear-gradient(to top, #0B0E17 10%, rgba(11, 14, 23, 0.8) 50%, transparent 100%);
}

.hero-title {
    font-size: 2.4rem;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 0.4rem;
    letter-spacing: -0.5px;
}

.hero-tagline {
    font-style: italic;
    color: #94A3B8;
    font-size: 1rem;
    margin-bottom: 0.8rem;
}

.hero-meta-row {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.meta-pill {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #E2E8F0;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 500;
}

.glass-panel {
    background: rgba(21, 28, 44, 0.65);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.section-heading {
    font-size: 1.25rem;
    font-weight: 600;
    color: #F8FAFC;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Custom Streamlit Touch Buttons */
.stButton > button {
    background: rgba(255, 255, 255, 0.06) !important;
    color: #CBD5E1 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 6px 12px !important;
    min-height: 42px !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    background: #E50914 !important;
    color: #FFFFFF !important;
    border-color: #E50914 !important;
    box-shadow: 0 4px 14px rgba(229, 9, 20, 0.35) !important;
}

/* Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    flex-wrap: wrap;
}

.stTabs [data-baseweb="tab"] {
    font-size: 0.88rem !important;
    padding: 8px 14px !important;
    border-radius: 10px !important;
    background: rgba(255, 255, 255, 0.04) !important;
    color: #94A3B8 !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(229, 9, 20, 0.2) !important;
    color: #FF3B30 !important;
    border-bottom: 2px solid #E50914 !important;
}

/* RESPONSIVE MEDIA QUERIES FOR MOBILE, TABLETS & ULTRA-WIDE */
@media (max-width: 1024px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    .hero-backdrop {
        height: 260px !important;
    }
    .hero-title {
        font-size: 1.8rem !important;
    }
    .hero-overlay {
        padding: 1.5rem !important;
    }
}

@media (max-width: 768px) {
    .brand-logo {
        font-size: 1.3rem !important;
    }
    .brand-tag {
        font-size: 0.68rem !important;
        padding: 2px 6px !important;
    }
    .hero-backdrop {
        height: 220px !important;
        border-radius: 14px !important;
    }
    .hero-title {
        font-size: 1.4rem !important;
    }
    .hero-tagline {
        font-size: 0.85rem !important;
    }
    .meta-pill {
        font-size: 0.72rem !important;
        padding: 2px 8px !important;
    }
    .cast-img {
        width: 55px !important;
        height: 55px !important;
    }
    .cast-name {
        font-size: 0.75rem !important;
    }
    .cast-char {
        font-size: 0.65rem !important;
    }
    
    /* Responsive 2-column flex grid for Streamlit columns on mobile screens */
    [data-testid="column"] {
        flex: 1 1 calc(50% - 0.75rem) !important;
        min-width: calc(50% - 0.75rem) !important;
    }
}

@media (max-width: 480px) {
    .hero-backdrop {
        height: 180px !important;
    }
    .hero-title {
        font-size: 1.2rem !important;
    }
    .badge-rating, .badge-year, .badge-match {
        font-size: 0.65rem !important;
        padding: 2px 5px !important;
    }
    .card-title {
        font-size: 0.8rem !important;
    }
}

</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# STATE & ROUTING SYNCHRONIZATION
# ==========================================================
if "view" not in st.session_state:
    st.session_state.view = "home"
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None
if "selected_person" not in st.session_state:
    st.session_state.selected_person = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")

if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except Exception:
        pass
elif qp_view in ("home", "details", "watchlist", "actor"):
    st.session_state.view = qp_view


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_watchlist():
    st.session_state.view = "watchlist"
    st.query_params["view"] = "watchlist"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


def goto_actor(person_id: int, person_name: str):
    st.session_state.view = "actor"
    st.session_state.selected_person = {"id": person_id, "name": person_name}
    st.session_state.selected_tmdb_id = None
    st.query_params["view"] = "actor"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


# ==========================================================
# API CLIENT (ERROR-SAFE CACHING)
# ==========================================================
@st.cache_data(ttl=120, show_spinner=False)
def _raw_api_get(url: str, params_tuple: tuple | None = None):
    params = dict(params_tuple) if params_tuple else None
    r = requests.get(url, params=params, timeout=20)
    if r.status_code >= 400:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    return r.json()


def api_get_json(path: str, params_tuple: tuple | None = None):
    url = f"{API_BASE}{path}"
    try:
        data = _raw_api_get(url, params_tuple)
        return data, None
    except Exception:
        try:
            params = dict(params_tuple) if params_tuple else None
            r = requests.get(url, params=params, timeout=20)
            if r.status_code < 400:
                return r.json(), None
            return None, f"HTTP {r.status_code}: {r.text[:200]}"
        except Exception as retry_err:
            return None, f"Request failed: {retry_err}"


def api_get_uncached(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=10)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:200]}"
        return r.json(), None
    except Exception as e:
        return None, str(e)


def api_post_json(path: str, payload: dict):
    try:
        r = requests.post(f"{API_BASE}{path}", json=payload, timeout=10)
        st.cache_data.clear()
        return r.json(), None
    except Exception as e:
        return None, str(e)


def api_delete_json(path: str):
    try:
        r = requests.delete(f"{API_BASE}{path}", timeout=10)
        st.cache_data.clear()
        return r.json(), None
    except Exception as e:
        return None, str(e)


# ==========================================================
# POSTER GRID COMPONENT
# ==========================================================
def poster_grid(cards, cols=6, key_prefix="grid", show_match_score=False):
    if not cards:
        st.info("No movies to display.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")
            vote = m.get("vote_average")
            release = m.get("release_date")
            year = (release or "")[:4]
            score = m.get("score")

            with colset[c]:
                badge_html = ""
                if vote and vote > 0:
                    badge_html += f"<span class='badge-rating'>★ {vote}</span>"
                if year:
                    badge_html += f"<span class='badge-year'>{year}</span>"
                if show_match_score and score is not None:
                    match_pct = int(round(score * 100))
                    badge_html += f"<span class='badge-match'>⚡ {match_pct}%</span>"

                img_html = (
                    f"<img src='{poster}' class='card-img' loading='lazy'/>"
                    if poster
                    else "<div class='no-poster'>🎬 No Poster</div>"
                )

                card_content = f"""
                <div class='poster-card-frame'>
                    <div class='badge-container'>{badge_html}</div>
                    {img_html}
                    <div class='card-info'>
                        <div class='card-title' title='{title}'>{title}</div>
                    </div>
                </div>
                """
                st.markdown(card_content, unsafe_allow_html=True)

                if st.button(
                    "▶ Explore",
                    key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}",
                    use_container_width=True,
                ):
                    if tmdb_id:
                        goto_details(tmdb_id)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                    "vote_average": tmdb.get("vote_average"),
                    "release_date": tmdb.get("release_date"),
                    "score": x.get("score"),
                }
            )
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    keyword_l = keyword.strip().lower()
    raw_items = []

    if isinstance(data, dict) and "results" in data:
        for m in data.get("results") or []:
            title = (m.get("title") or m.get("name") or "").strip()
            tmdb_id = m.get("id")
            if not title or not tmdb_id:
                continue
            poster_path = m.get("poster_path")
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                    "vote_average": round(float(m.get("vote_average", 0)), 1)
                    if m.get("vote_average")
                    else None,
                }
            )
    elif isinstance(data, list):
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": m.get("poster_url"),
                    "release_date": m.get("release_date", ""),
                    "vote_average": m.get("vote_average"),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]
    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = final_list[:limit]
    return suggestions, cards


# ==========================================================
# BRAND NAVBAR HEADER
# ==========================================================
nav_left, nav_mid, nav_right = st.columns([2.5, 1.2, 1.2])
with nav_left:
    st.markdown(
        """
        <div class='brand-logo'>
            <span>🍿</span> Movie Recommendation System
        </div>
        """,
        unsafe_allow_html=True,
    )
with nav_mid:
    if st.button("📌 My Watchlist", use_container_width=True):
        goto_watchlist()
with nav_right:
    if st.session_state.view != "home":
        if st.button("🏠 Home Catalogue", use_container_width=True):
            goto_home()

st.markdown(
    "<div style='border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:1.5rem;'></div>",
    unsafe_allow_html=True,
)

# ==========================================================
# VIEW: HOME CATALOGUE & VIBES
# ==========================================================
if st.session_state.view == "home":
    search_col1, search_col2 = st.columns([3.2, 1.2])
    with search_col1:
        typed = st.text_input(
            "Search Cinema",
            placeholder="Search movie title (e.g. Inception, Avatar, Batman...)",
            label_visibility="collapsed",
        )
    with search_col2:
        feed_mode = st.selectbox(
            "Feed Filter",
            ["popular", "trending", "top_rated", "now_playing", "upcoming", "vibe_picker"],
            format_func=lambda x: {
                "popular": "🔥 Popular Now",
                "trending": "📈 Trending Today",
                "top_rated": "⭐ Top Rated",
                "now_playing": "🎟️ In Theaters",
                "upcoming": "🚀 Upcoming Releases",
                "vibe_picker": "🎭 Mood / Vibe Picker",
            }[x],
            label_visibility="collapsed",
        )

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # SEARCH MODE
    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("🔍 Type at least 2 characters...")
        else:
            params_tuple = (("query", typed.strip()),)
            data, err = api_get_json("/tmdb/search", params_tuple)

            if err or data is None:
                st.error(f"Search error: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                if suggestions:
                    sug_col1, sug_col2 = st.columns([2.5, 1])
                    with sug_col1:
                        labels = ["-- Instant Suggestions --"] + [
                            s[0] for s in suggestions
                        ]
                        selected = st.selectbox(
                            "Suggestions",
                            labels,
                            index=0,
                            label_visibility="collapsed",
                        )

                        if selected != "-- Instant Suggestions --":
                            label_to_id = {s[0]: s[1] for s in suggestions}
                            goto_details(label_to_id[selected])

                st.markdown(
                    f"<div class='section-heading'>🔍 Results for '{typed.strip()}'</div>",
                    unsafe_allow_html=True,
                )
                poster_grid(cards, cols=6, key_prefix="search_results")

        st.stop()

    # MOOD / VIBE PICKER MODE
    if feed_mode == "vibe_picker":
        st.markdown("<div class='section-heading'>🎭 Select Your Vibe</div>", unsafe_allow_html=True)
        mood_selected = st.radio(
            "Vibe",
            ["mind_bending", "action", "cozy", "horror", "romance"],
            format_func=lambda x: {
                "mind_bending": "🧠 Mind-Bending Sci-Fi & Mystery",
                "action": "💥 Adrenaline Action & Adventure",
                "cozy": "🍿 Cozy Feel-Good Comedy",
                "horror": "😱 Late Night Thrills & Horror",
                "romance": "💖 Heartfelt Romance",
            }[x],
            horizontal=True,
            label_visibility="collapsed",
        )
        params_tuple = (("mood", mood_selected), ("limit", 24))
        mood_cards, err = api_get_json("/home/mood", params_tuple)
        if not err and mood_cards:
            poster_grid(mood_cards, cols=6, key_prefix="mood_feed")
        else:
            st.error("Could not load mood feed.")
        st.stop()

    # STANDARD FEED MODE
    feed_title_map = {
        "popular": "🔥 Popular Movies",
        "trending": "📈 Trending Today",
        "top_rated": "⭐ All-Time Top Rated",
        "now_playing": "🎟️ Currently In Theaters",
        "upcoming": "🚀 Upcoming Releases",
    }
    st.markdown(
        f"<div class='section-heading'>{feed_title_map[feed_mode]}</div>",
        unsafe_allow_html=True,
    )

    params_tuple = (("category", feed_mode), ("limit", 24))
    home_cards, err = api_get_json("/home", params_tuple)
    if err or not home_cards:
        st.error(f"Unable to load feed: {err or 'API Offline'}")
        st.stop()

    poster_grid(home_cards, cols=6, key_prefix="home_feed")

# ==========================================================
# VIEW: WATCHLIST (SQLITE PERSISTED)
# ==========================================================
elif st.session_state.view == "watchlist":
    st.markdown("<div class='section-heading'>📌 My Personal Watchlist</div>", unsafe_allow_html=True)
    watchlist_items, err = api_get_uncached("/watchlist")

    if err or not watchlist_items:
        st.info("Your Watchlist is empty! Click '❤️ Add to Watchlist' on any movie details page.")
    else:
        poster_grid(watchlist_items, cols=6, key_prefix="watchlist_grid")

        if watchlist_items:
            st.markdown("<div class='section-heading'>✨ Tailored Recommendations for Your Watchlist</div>", unsafe_allow_html=True)
            top_saved_id = watchlist_items[0].get("tmdb_id")
            if top_saved_id:
                bundle, err2 = api_get_json(f"/movie/bundle/{top_saved_id}")
                if not err2 and bundle:
                    poster_grid(to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")), cols=6, key_prefix="wl_recs", show_match_score=True)

# ==========================================================
# VIEW: ACTOR FILMOGRAPHY
# ==========================================================
elif st.session_state.view == "actor":
    actor = st.session_state.selected_person
    if not actor:
        goto_home()
        st.stop()

    st.markdown(f"<div class='section-heading'>🎭 Filmography — {actor['name']}</div>", unsafe_allow_html=True)
    params_tuple = (("limit", 24),)
    actor_cards, err = api_get_json(f"/person/{actor['id']}/movies", params_tuple)
    if not err and actor_cards:
        poster_grid(actor_cards, cols=6, key_prefix="actor_feed")
    else:
        st.info("No movie credits found for this actor.")

# ==========================================================
# VIEW: MOVIE DETAILS & BUNDLE RECOMMENDATIONS
# ==========================================================
elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    wl_check, _ = api_get_uncached(f"/watchlist/check/{tmdb_id}")
    in_watchlist = wl_check.get("in_watchlist", False) if wl_check else False

    bundle, err = api_get_json(f"/movie/bundle/{tmdb_id}")
    if err or not bundle:
        st.error(f"Failed to load movie bundle: {err or 'Unknown error'}")
        st.stop()

    data = bundle.get("movie_details", {})
    backdrop = data.get("backdrop_url") or data.get("poster_url")
    title = data.get("title", "Untitled")
    tagline = data.get("tagline", "")
    release = data.get("release_date") or ""
    year = release[:4] if release else ""
    vote = data.get("vote_average")
    runtime = data.get("runtime")
    runtime_str = f"{runtime // 60}h {runtime % 60}m" if runtime and runtime > 0 else ""
    genres = [g["name"] for g in data.get("genres", [])]

    meta_pills_html = ""
    if year:
        meta_pills_html += f"<span class='meta-pill'>📅 {year}</span>"
    if vote and vote > 0:
        meta_pills_html += f"<span class='meta-pill'>⭐ {vote} / 10</span>"
    if runtime_str:
        meta_pills_html += f"<span class='meta-pill'>⏱️ {runtime_str}</span>"
    for g in genres:
        meta_pills_html += f"<span class='meta-pill'>{g}</span>"

    # Hero Banner
    if backdrop:
        st.markdown(
            f"""
            <div class='hero-backdrop'>
                <img src='{backdrop}' class='hero-img' />
                <div class='hero-overlay'>
                    <div class='hero-title'>{title}</div>
                    {"<div class='hero-tagline'>\"" + tagline + "\"</div>" if tagline else ""}
                    <div class='hero-meta-row'>{meta_pills_html}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Watchlist Action Button + Poster
    col_poster, col_details = st.columns([1, 2.5], gap="large")

    with col_poster:
        if data.get("poster_url"):
            st.markdown(
                f"<img src='{data['poster_url']}' style='width:100%; border-radius:16px; box-shadow:0 15px 30px rgba(0,0,0,0.5); border:1px solid rgba(255,255,255,0.1); margin-bottom:12px;'/>",
                unsafe_allow_html=True,
            )

        if in_watchlist:
            if st.button("💔 Remove from Watchlist", use_container_width=True, key="btn_wl_remove"):
                api_delete_json(f"/watchlist/{tmdb_id}")
                st.rerun()
        else:
            if st.button("❤️ Add to Watchlist", use_container_width=True, key="btn_wl_add"):
                api_post_json(
                    "/watchlist",
                    {
                        "tmdb_id": tmdb_id,
                        "title": title,
                        "poster_url": data.get("poster_url"),
                        "release_date": release,
                        "vote_average": vote,
                    },
                )
                st.rerun()

    with col_details:
        st.markdown(
            f"""
            <div class='glass-panel'>
                <h3 style='margin-top:0; color:#F8FAFC;'>Synopsis</h3>
                <p style='color:#CBD5E1; font-size:1.02rem; line-height:1.6;'>
                    {data.get('overview') or 'No synopsis available.'}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # YouTube Trailer Embed Section
    trailer = bundle.get("trailer")
    if trailer and isinstance(trailer, dict) and trailer.get("youtube_url"):
        st.markdown("<div class='section-heading'>🎬 Official Trailer</div>", unsafe_allow_html=True)
        try:
            st.video(trailer["youtube_url"])
        except Exception:
            st.caption(f"Trailer link: {trailer['youtube_url']}")

    # Where to Watch (Streaming Providers)
    providers = bundle.get("providers", [])
    if providers:
        st.markdown("<div class='section-heading'>📺 Streaming On</div>", unsafe_allow_html=True)
        prov_cols = st.columns(len(providers) if len(providers) <= 8 else 8)
        for idx, p in enumerate(providers[:8]):
            with prov_cols[idx]:
                if p.get("logo_url"):
                    st.markdown(
                        f"<img src='{p['logo_url']}' class='provider-logo' title='{p.get('provider_name')}'/>",
                        unsafe_allow_html=True,
                    )
                st.caption(p.get("provider_name", ""))

    # Top Cast Avatars
    cast = bundle.get("cast", [])
    if cast:
        st.markdown("<div class='section-heading'>👥 Top Cast</div>", unsafe_allow_html=True)
        cast_cols = st.columns(len(cast) if len(cast) <= 8 else 8)
        for idx, c in enumerate(cast[:8]):
            with cast_cols[idx]:
                profile = c.get("profile_url") or "https://via.placeholder.com/185x185?text=No+Photo"
                st.markdown(
                    f"""
                    <div class='cast-card'>
                        <img src='{profile}' class='cast-img'/>
                        <div class='cast-name'>{c.get('name')}</div>
                        <div class='cast-char'>{c.get('character') or ''}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                pid = c.get("person_id", idx)
                if st.button("Filmography", key=f"cast_btn_{pid}_{idx}", use_container_width=True):
                    goto_actor(c["person_id"], c["name"])

    # Multi-Tier Recommendations Tabs
    st.markdown("<div class='section-heading'>🎯 Recommendations Engine</div>", unsafe_allow_html=True)
    tab_tfidf, tab_similar, tab_genre = st.tabs(
        [
            "⚡ AI Content Similarity (TF-IDF)",
            "🎬 Related & Similar",
            "🎭 Genre Discover",
        ]
    )

    with tab_tfidf:
        tfidf_cards = to_cards_from_tfidf_items(bundle.get("tfidf_recommendations"))
        if tfidf_cards:
            poster_grid(tfidf_cards, cols=6, key_prefix="details_tfidf", show_match_score=True)
        else:
            st.info("No direct TF-IDF matches found in local vector dataset. Check TMDB recommendations.")

    with tab_similar:
        similar_cards = bundle.get("similar_recommendations", [])
        if similar_cards:
            poster_grid(similar_cards, cols=6, key_prefix="details_similar")
        else:
            st.info("No similar recommendations available.")

    with tab_genre:
        genre_cards = bundle.get("genre_recommendations", [])
        if genre_cards:
            poster_grid(genre_cards, cols=6, key_prefix="details_genre")
        else:
            st.info("No genre recommendations available.")
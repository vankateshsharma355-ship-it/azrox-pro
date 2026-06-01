import streamlit as st
import requests
import json
import re
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import google.generativeai as genai

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Azrox Pro – YT AI Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CUSTOM CSS – Dark Gaming aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500&display=swap');

:root {
    --bg: #0a0a0f;
    --card: #111118;
    --border: #1e1e2e;
    --accent: #7c3aed;
    --accent2: #06b6d4;
    --success: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
    --text: #e2e8f0;
    --muted: #64748b;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif;
    color: var(--text);
}

h1, h2, h3 { font-family: 'Rajdhani', sans-serif; letter-spacing: 0.05em; }

[data-testid="stSidebar"] { background: var(--card) !important; }

.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: border-color 0.3s;
}
.metric-card:hover { border-color: var(--accent); }
.metric-value {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent2);
}
.metric-label {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

.video-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.2s;
}
.video-card:hover { border-color: var(--accent); transform: translateY(-2px); }
.video-title {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.4;
    margin-bottom: 6px;
}
.video-meta {
    font-size: 0.72rem;
    color: var(--muted);
}

.analysis-box {
    background: linear-gradient(135deg, #111118 0%, #1a1a2e 100%);
    border: 1px solid var(--accent);
    border-radius: 12px;
    padding: 24px;
    margin-top: 16px;
}

.tag-chip {
    display: inline-block;
    background: #1e1e2e;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: var(--text);
    margin: 3px;
}

.section-header {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--accent2);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.health-bar-container { margin: 8px 0; }
.health-bar-label { font-size: 0.8rem; color: var(--muted); margin-bottom: 4px; }
.health-bar {
    height: 8px;
    background: var(--border);
    border-radius: 4px;
    overflow: hidden;
}
.health-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 1s ease;
}

.connect-btn {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    letter-spacing: 0.05em;
}

div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, var(--accent), #5b21b6);
    color: white;
    border: none;
    border-radius: 8px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 0.05em;
    transition: opacity 0.2s;
}
div[data-testid="stButton"] > button:hover { opacity: 0.85; }

.stTabs [data-baseweb="tab-list"] {
    background: var(--card);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 0.05em;
    color: var(--muted);
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
    border-radius: 8px;
}

div[data-testid="stCheckbox"] label { font-size: 0.85rem; color: var(--text); }

.stTextInput input, .stTextArea textarea {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

.badge-green { 
    background: #064e3b; color: var(--success);
    border-radius: 20px; padding: 2px 10px; font-size: 0.72rem;
}
.badge-yellow {
    background: #451a03; color: var(--warn);
    border-radius: 20px; padding: 2px 10px; font-size: 0.72rem;
}
.badge-red {
    background: #450a0a; color: var(--danger);
    border-radius: 20px; padding: 2px 10px; font-size: 0.72rem;
}

.logo-circle {
    width: 80px; height: 80px;
    border-radius: 50%;
    border: 3px solid var(--accent);
    object-fit: cover;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
REDIRECT_URI = "https://azrox-pro.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def format_number(n):
    if n is None: return "–"
    n = int(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)

def format_duration(iso_duration):
    """Convert ISO 8601 duration to seconds, also returns label."""
    match = re.match(
        r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso_duration or "PT0S"
    )
    if not match: return 0
    h = int(match.group(1) or 0)
    m = int(match.group(2) or 0)
    s = int(match.group(3) or 0)
    return h * 3600 + m * 60 + s

def is_short(video):
    """Shorts = duration ≤ 60 s OR vertical aspect OR #shorts in title/desc."""
    dur = format_duration(
        video.get("contentDetails", {}).get("duration", "PT0S")
    )
    title = video.get("snippet", {}).get("title", "").lower()
    desc  = video.get("snippet", {}).get("description", "").lower()
    if dur <= 60: return True
    if "#shorts" in title or "#shorts" in desc: return True
    return False

def get_client_secrets():
    return {
        "web": {
            "client_id":     st.secrets["client_secrets"]["client_id"],
            "client_secret": st.secrets["client_secrets"]["client_secret"],
            "project_id":    st.secrets["client_secrets"]["project_id"],
            "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
            "token_uri":     "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url":
                "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [REDIRECT_URI]
        }
    }

def build_flow():
    return Flow.from_client_config(
        get_client_secrets(), scopes=SCOPES, redirect_uri=REDIRECT_URI
    )

def get_youtube_service(creds_dict):
    creds = Credentials(
        token=creds_dict["token"],
        refresh_token=creds_dict.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=st.secrets["client_secrets"]["client_id"],
        client_secret=st.secrets["client_secrets"]["client_secret"],
    )
    return build("youtube", "v3", credentials=creds)

# ─────────────────────────────────────────────
# YOUTUBE DATA FETCHERS
# ─────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_channel_info(_youtube):
    resp = _youtube.channels().list(
        part="snippet,statistics,brandingSettings",
        mine=True
    ).execute()
    return resp["items"][0] if resp.get("items") else None

@st.cache_data(ttl=300)
def fetch_all_videos(_youtube, channel_id):
    videos = []
    next_page = None
    while True:
        resp = _youtube.search().list(
            part="id", channelId=channel_id,
            type="video", maxResults=50,
            pageToken=next_page, order="date"
        ).execute()
        ids = [i["id"]["videoId"] for i in resp.get("items", [])]
        if ids:
            detail_resp = _youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(ids)
            ).execute()
            videos.extend(detail_resp.get("items", []))
        next_page = resp.get("nextPageToken")
        if not next_page: break
    return videos

@st.cache_data(ttl=600)
def fetch_watch_time(_youtube):
    """Fetch last 28 days watch time via Analytics API (requires scope)."""
    try:
        analytics = build(
            "youtubeAnalytics", "v2",
            credentials=_youtube._http.credentials
        )
        today = datetime.today().strftime("%Y-%m-%d")
        resp = analytics.reports().query(
            ids="channel==MINE",
            startDate="2020-01-01",
            endDate=today,
            metrics="estimatedMinutesWatched,views",
            dimensions="channel"
        ).execute()
        rows = resp.get("rows", [[None, None, None]])
        return rows[0][1], rows[0][2]
    except Exception:
        return None, None

# ─────────────────────────────────────────────
# AI ANALYSIS (Gemini)
# ─────────────────────────────────────────────

def analyze_video_ai(video, channel_name):
    try:
        genai.configure(api_key=st.secrets["gemini"]["api_key"])
        model = genai.GenerativeModel("gemini-1.5-flash")

        title = video["snippet"]["title"]
        desc  = video["snippet"].get("description", "")[:500]
        tags  = video["snippet"].get("tags", [])
        views = video["statistics"].get("viewCount", 0)
        likes = video["statistics"].get("likeCount", 0)

        prompt = f"""
You are a YouTube SEO expert. Analyze this video and suggest improvements.

Channel: {channel_name}
Video Title: {title}
Current Tags: {', '.join(tags[:15]) if tags else 'None'}
Views: {views} | Likes: {likes}
Description snippet: {desc}

Respond ONLY in this exact JSON format (no markdown, no extra text):
{{
  "titles": ["Title 1", "Title 2", "Title 3", "Title 4", "Title 5"],
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10",
           "tag11","tag12","tag13","tag14","tag15","tag16","tag17","tag18","tag19","tag20"],
  "seo_score": 72,
  "analysis": "Brief 2-line analysis of why these suggestions will improve reach."
}}
"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}

def analyze_channel_health(channel, all_videos):
    try:
        genai.configure(api_key=st.secrets["gemini"]["api_key"])
        model = genai.GenerativeModel("gemini-1.5-flash")

        stats = channel.get("statistics", {})
        subs  = stats.get("subscriberCount", 0)
        views = stats.get("viewCount", 0)
        vcount= stats.get("videoCount", 0)
        name  = channel["snippet"]["title"]

        # Aggregate video data
        total_likes = sum(int(v["statistics"].get("likeCount",0)) for v in all_videos)
        avg_views   = int(views) // max(int(vcount), 1)

        prompt = f"""
You are a YouTube growth strategist. Analyze this channel and provide actionable insights.

Channel: {name}
Subscribers: {subs} | Total Views: {views}
Total Videos: {vcount} | Avg Views/Video: {avg_views}
Total Likes: {total_likes}

Respond ONLY in this exact JSON format:
{{
  "monetization_eligible": true,
  "monetization_reason": "1 line reason",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2", "weakness 3"],
  "growth_tips": ["tip 1", "tip 2", "tip 3", "tip 4"],
  "scores": {{
    "seo": 65,
    "consistency": 70,
    "engagement": 55,
    "growth_potential": 80
  }},
  "summary": "2-3 line overall channel health summary."
}}
"""
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}

# ─────────────────────────────────────────────
# UPDATE VIDEO ON YOUTUBE
# ─────────────────────────────────────────────

def update_video_metadata(youtube, video_id, new_title, new_tags,
                           current_snippet):
    try:
        current_snippet["title"] = new_title
        current_snippet["tags"]  = new_tags
        youtube.videos().update(
            part="snippet",
            body={"id": video_id, "snippet": current_snippet}
        ).execute()
        return True, "✅ Video YouTube Studio pe update ho gaya!"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# ─────────────────────────────────────────────
# OAUTH FLOW
# ─────────────────────────────────────────────

def handle_oauth():
    params = st.query_params
    if "code" in params and "credentials" not in st.session_state:
        code = params["code"]
        try:
            flow = build_flow()
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state["credentials"] = {
                "token":         creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri":     creds.token_uri,
                "client_id":     creds.client_id,
                "client_secret": creds.client_secret,
                "scopes":        list(creds.scopes or []),
            }
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Auth error: {e}")

# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────

def main():
    handle_oauth()

    # ── HEADER ──────────────────────────────
    st.markdown("""
    <div style="display:flex;align-items:center;gap:16px;padding:16px 0 24px;">
      <div style="background:linear-gradient(135deg,#7c3aed,#06b6d4);
                  width:48px;height:48px;border-radius:12px;
                  display:flex;align-items:center;justify-content:center;
                  font-size:1.5rem;">🎯</div>
      <div>
        <h1 style="margin:0;font-size:1.8rem;
                   background:linear-gradient(135deg,#7c3aed,#06b6d4);
                   -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
          AZROX PRO
        </h1>
        <p style="margin:0;font-size:0.75rem;color:#64748b;letter-spacing:0.15em;">
          AI-POWERED YOUTUBE GROWTH TOOL
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── NOT CONNECTED ────────────────────────
    if "credentials" not in st.session_state:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;">
          <div style="font-size:4rem;margin-bottom:16px;">📺</div>
          <h2 style="font-family:'Rajdhani',sans-serif;font-size:2rem;
                     color:#e2e8f0;margin-bottom:8px;">
            Apna YouTube Channel Connect Karo
          </h2>
          <p style="color:#64748b;max-width:400px;margin:0 auto 32px;">
            Channel ko connect karne ke baad AI automatically videos analyze karega,
            titles & tags suggest karega aur reach badhane mein help karega.
          </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("🔗 YouTube Connect Karo", use_container_width=True):
                flow = build_flow()
                auth_url, _ = flow.authorization_url(
                    prompt='consent', access_type='offline'
                )
                st.markdown(f"""
                <div style="text-align:center;margin-top:16px;">
                  <a href="{auth_url}" target="_self"
                     style="background:linear-gradient(135deg,#7c3aed,#06b6d4);
                            color:white;padding:14px 40px;border-radius:10px;
                            text-decoration:none;font-family:'Rajdhani',sans-serif;
                            font-size:1.1rem;font-weight:600;letter-spacing:0.05em;">
                    🚀 Google se Authorize Karo
                  </a>
                </div>
                """, unsafe_allow_html=True)
        return

    # ── CONNECTED – Build service ────────────
    try:
        youtube = get_youtube_service(st.session_state["credentials"])
    except Exception as e:
        st.error(f"YouTube service error: {e}")
        if st.button("Reconnect"):
            del st.session_state["credentials"]
            st.rerun()
        return

    channel = fetch_channel_info(youtube)
    if not channel:
        st.error("Channel data fetch nahi ho saki.")
        return

    ch_snippet = channel["snippet"]
    ch_stats   = channel["statistics"]
    ch_id      = channel["id"]

    # ── DASHBOARD HEADER ─────────────────────
    thumb_url = (
        ch_snippet.get("thumbnails", {})
        .get("high", {}).get("url")
        or ch_snippet.get("thumbnails", {})
        .get("default", {}).get("url", "")
    )

    col_logo, col_name = st.columns([1, 5])
    with col_logo:
        if thumb_url:
            st.markdown(
                f'<img src="{thumb_url}" class="logo-circle">',
                unsafe_allow_html=True
            )
    with col_name:
        st.markdown(f"""
        <h2 style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;
                   margin-bottom:2px;">{ch_snippet['title']}</h2>
        <p style="color:#64748b;font-size:0.8rem;margin:0;">
          {ch_snippet.get('customUrl','') or ch_id}
        </p>
        """, unsafe_allow_html=True)

        disc_btn, _ = st.columns([1, 4])
        with disc_btn:
            if st.button("🔓 Disconnect"):
                del st.session_state["credentials"]
                st.cache_data.clear()
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── METRIC CARDS ─────────────────────────
    subs   = ch_stats.get("subscriberCount", "0")
    views  = ch_stats.get("viewCount", "0")
    vcount = ch_stats.get("videoCount", "0")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value">{format_number(subs)}</div>
          <div class="metric-label">👥 Subscribers</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value">{format_number(views)}</div>
          <div class="metric-label">👁️ Total Views</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value">{vcount}</div>
          <div class="metric-label">🎬 Total Videos</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        # Monetization check (basic)
        mono_ok = int(subs or 0) >= 1000 and int(vcount or 0) >= 0
        badge_class = "badge-green" if mono_ok else "badge-red"
        badge_text  = "Eligible ✓" if mono_ok else "Not Yet"
        st.markdown(f"""
        <div class="metric-card">
          <div class="metric-value" style="font-size:1.3rem;">
            <span class="{badge_class}">{badge_text}</span>
          </div>
          <div class="metric-label">💰 Monetization</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ─────────────────────────────────
    tab1, tab2, tab3 = st.tabs(
        ["🎬  Videos", "📊  Channel Analysis", "⚙️  Settings"]
    )

    # ══════════════════════════════════════════
    # TAB 1 – VIDEOS
    # ══════════════════════════════════════════
    with tab1:
        with st.spinner("Videos fetch ho rahi hain..."):
            all_videos = fetch_all_videos(youtube, ch_id)

        long_videos  = [v for v in all_videos if not is_short(v)]
        short_videos = [v for v in all_videos if is_short(v)]

        vtab1, vtab2 = st.tabs(
            [f"📹 Long Videos ({len(long_videos)})",
             f"⚡ Shorts ({len(short_videos)})"]
        )

        for vtab, vlist, label in [
            (vtab1, long_videos,  "Long"),
            (vtab2, short_videos, "Short")
        ]:
            with vtab:
                if not vlist:
                    st.info(f"Koi {label} video nahi mili.")
                    continue

                st.markdown(
                    f'<div class="section-header">{label} Videos</div>',
                    unsafe_allow_html=True
                )

                # ── VIDEO GRID ───────────────
                cols_per_row = 3
                for i in range(0, len(vlist), cols_per_row):
                    row_vids = vlist[i:i+cols_per_row]
                    cols = st.columns(cols_per_row)

                    for j, vid in enumerate(row_vids):
                        snip  = vid["snippet"]
                        stats = vid.get("statistics", {})
                        thumb = (
                            snip.get("thumbnails", {})
                            .get("medium", {}).get("url", "")
                        )
                        views_v = format_number(stats.get("viewCount"))
                        likes_v = format_number(stats.get("likeCount"))

                        with cols[j]:
                            if thumb:
                                st.image(thumb, use_container_width=True)
                            st.markdown(
                                f'<div class="video-title">{snip["title"][:70]}</div>'
                                f'<div class="video-meta">👁️ {views_v} &nbsp;|&nbsp; '
                                f'👍 {likes_v}</div>',
                                unsafe_allow_html=True
                            )

                            if st.button(
                                "🤖 AI Analyze",
                                key=f"analyze_{vid['id']}",
                                use_container_width=True
                            ):
                                st.session_state["selected_video"] = vid

                # ── ANALYSIS PANEL ───────────
                if (
                    "selected_video" in st.session_state
                    and st.session_state["selected_video"] in vlist
                ):
                    sel = st.session_state["selected_video"]
                    st.markdown("---")
                    st.markdown(
                        '<div class="section-header">🤖 AI Analysis</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"**Analyzing:** {sel['snippet']['title'][:80]}"
                    )

                    if "ai_result" not in st.session_state or \
                       st.session_state.get("ai_video_id") != sel["id"]:
                        with st.spinner("Gemini AI analysis kar raha hai..."):
                            result = analyze_video_ai(sel, ch_snippet["title"])
                            st.session_state["ai_result"]   = result
                            st.session_state["ai_video_id"] = sel["id"]

                    result = st.session_state.get("ai_result", {})

                    if "error" in result:
                        st.error(f"AI Error: {result['error']}")
                    else:
                        st.markdown(
                            f'<div class="analysis-box">'
                            f'<p style="color:#94a3b8;font-size:0.85rem;">'
                            f'📝 {result.get("analysis","")}</p></div>',
                            unsafe_allow_html=True
                        )

                        col_t, col_tg = st.columns(2)

                        # ── TITLES ───────────
                        with col_t:
                            st.markdown(
                                "**🏷️ Suggested Titles (tick to select)**"
                            )
                            sel_title = None
                            for t in result.get("titles", []):
                                if st.checkbox(t, key=f"title_{t[:30]}"):
                                    sel_title = t

                        # ── TAGS ─────────────
                        with col_tg:
                            st.markdown(
                                "**🔖 Suggested Tags (tick to select)**"
                            )
                            sel_tags = []
                            tags_list = result.get("tags", [])
                            for tg in tags_list:
                                if st.checkbox(tg, key=f"tag_{tg[:20]}"):
                                    sel_tags.append(tg)

                        # ── UPDATE BUTTON ────
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(
                            "🚀 YouTube Studio pe Update Karo",
                            use_container_width=True
                        ):
                            if not sel_title:
                                st.warning(
                                    "Koi bhi ek title select karo pehle."
                                )
                            elif not sel_tags:
                                st.warning(
                                    "Kam se kam ek tag select karo."
                                )
                            else:
                                current_snip = dict(sel["snippet"])
                                # Remove read-only fields
                                for k in ["publishedAt","channelId","channelTitle",
                                          "liveBroadcastContent","localized",
                                          "thumbnails"]:
                                    current_snip.pop(k, None)

                                ok, msg = update_video_metadata(
                                    youtube,
                                    sel["id"],
                                    sel_title,
                                    sel_tags,
                                    current_snip
                                )
                                if ok:
                                    st.success(msg)
                                    st.cache_data.clear()
                                else:
                                    st.error(msg)

    # ══════════════════════════════════════════
    # TAB 2 – CHANNEL ANALYSIS
    # ══════════════════════════════════════════
    with tab2:
        st.markdown(
            '<div class="section-header">📊 Channel Health Report</div>',
            unsafe_allow_html=True
        )

        if st.button("🔍 Channel Analyze Karo", use_container_width=False):
            with st.spinner("AI channel ko analyze kar raha hai..."):
                all_videos = fetch_all_videos(youtube, ch_id)
                health     = analyze_channel_health(channel, all_videos)
                st.session_state["channel_health"] = health

        if "channel_health" in st.session_state:
            h = st.session_state["channel_health"]

            if "error" in h:
                st.error(f"Analysis error: {h['error']}")
            else:
                # Summary
                st.markdown(f"""
                <div class="analysis-box">
                  <p style="color:#e2e8f0;font-size:0.95rem;margin:0;">
                    {h.get('summary','')}
                  </p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Scores
                scores = h.get("scores", {})
                score_cols = st.columns(4)
                for idx, (k, v) in enumerate(scores.items()):
                    color = (
                        "#10b981" if v >= 70 else
                        "#f59e0b" if v >= 45 else "#ef4444"
                    )
                    with score_cols[idx % 4]:
                        st.markdown(f"""
                        <div class="metric-card">
                          <div class="metric-value" style="color:{color};">
                            {v}%
                          </div>
                          <div class="metric-label">
                            {k.replace('_',' ').title()}
                          </div>
                        </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                col_l, col_r = st.columns(2)

                with col_l:
                    st.markdown("**✅ Channel ki Strengths**")
                    for s in h.get("strengths", []):
                        st.markdown(f"- {s}")

                    st.markdown("<br>**💡 Growth Tips**")
                    for tip in h.get("growth_tips", []):
                        st.markdown(f"- {tip}")

                with col_r:
                    st.markdown("**⚠️ Weaknesses / Issues**")
                    for w in h.get("weaknesses", []):
                        st.markdown(f"- {w}")

                    st.markdown("<br>**💰 Monetization Status**")
                    mono = h.get("monetization_eligible", False)
                    badge = "badge-green" if mono else "badge-red"
                    label = "Eligible ✓" if mono else "Not Eligible ✗"
                    st.markdown(
                        f'<span class="{badge}">{label}</span> – '
                        f'{h.get("monetization_reason","")}',
                        unsafe_allow_html=True
                    )

    # ══════════════════════════════════════════
    # TAB 3 – SETTINGS
    # ══════════════════════════════════════════
    with tab3:
        st.markdown(
            '<div class="section-header">⚙️ Settings</div>',
            unsafe_allow_html=True
        )
        st.info("Cache clear karne ke liye niche button press karo.")
        if st.button("🗑️ Cache Clear Karo"):
            st.cache_data.clear()
            st.success("Cache clear ho gaya! Page refresh hoga.")
            st.rerun()

        st.markdown("---")
        st.markdown("**App Version:** `1.0.0` | **Model:** Gemini 1.5 Flash")

# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()

import streamlit as st
import requests
import json
import re
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google import generativeai as genai

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
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
:root { --bg: #0a0a0f; --card: #111118; --accent: #7c3aed; --accent2: #06b6d4; --text: #e2e8f0; }
html, body, [data-testid="stAppViewContainer"] { background: var(--bg) !important; color: var(--text); }
.metric-card { background: var(--card); border: 1px solid #1e1e2e; border-radius: 12px; padding: 20px; text-align: center; }
.metric-value { font-size: 2rem; font-weight: 700; color: var(--accent2); }
.metric-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; margin-top: 4px; }
.analysis-box { background: #111118; border: 1px solid var(--accent); border-radius: 12px; padding: 24px; margin-top: 16px; }
.section-header { font-size: 1.3rem; font-weight: 600; color: var(--accent2); border-bottom: 1px solid #1e1e2e; padding-bottom: 8px; margin-bottom: 16px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS & FLOW
# ─────────────────────────────────────────────
REDIRECT_URI = "https://azrox-pro.streamlit.app/"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def get_client_secrets():
    return {
        "web": {
            "client_id": st.secrets["client_secrets"]["client_id"],
            "client_secret": st.secrets["client_secrets"]["client_secret"],
            "project_id": st.secrets["client_secrets"]["project_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [REDIRECT_URI]
        }
    }

def build_flow():
    # Updated Flow configuration
    return Flow.from_client_config(
        get_client_secrets(), 
        scopes=SCOPES, 
        redirect_uri=REDIRECT_URI
    )

def get_youtube_service(creds_dict):
    creds = Credentials(
        token=creds_dict["token"],
        refresh_token=creds_dict.get("refresh_token"),
        token_uri=creds_dict["token_uri"],
        client_id=creds_dict["client_id"],
        client_secret=creds_dict["client_secret"],
    )
    return build("youtube", "v3", credentials=creds)

# ─────────────────────────────────────────────
# MAIN APP LOGIC
# ─────────────────────────────────────────────
def handle_oauth():
    params = st.query_params
    if "code" in params and "credentials" not in st.session_state:
        flow = build_flow()
        flow.fetch_token(code=params["code"])
        creds = flow.credentials
        st.session_state["credentials"] = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
        }
        st.query_params.clear()
        st.rerun()

def main():
    handle_oauth()
    
    if "credentials" not in st.session_state:
        st.title("🎯 Azrox Pro - Login")
        flow = build_flow()
        auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
        st.markdown(f'<a href="{auth_url}" target="_self" style="padding:10px; background:var(--accent); color:white; border-radius:5px;">🚀 Connect YouTube</a>', unsafe_allow_html=True)
        return

    # App logic continues here...
    st.write("Logged in successfully!")
    if st.button("Logout"):
        del st.session_state["credentials"]
        st.rerun()

if __name__ == "__main__":
    main()

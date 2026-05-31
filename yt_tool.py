import streamlit as st
import json
from google import genai
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

# --- SECURE CONFIG ---
# Jab aap deploy karenge, tab Streamlit Secrets mein GOOGLE_API_KEY daalna
# Filhal ke liye yahan apni key paste kar sakte hain, par baad mein remove kar dena
client = genai.Client(api_key=st.secrets.get("GOOGLE_API_KEY", "PASTE_YOUR_KEY_HERE"))

st.set_page_config(layout="wide", page_title="Azrox Pro Ultimate")

# --- AUTH ---
if 'creds' not in st.session_state:
    if st.button("Authorize YouTube"):
        scopes = ['https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/youtube.force-ssl']
        flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', scopes=scopes)
        st.session_state['creds'] = flow.run_local_server(port=8080)
        st.rerun()
    st.stop()

youtube = build("youtube", "v3", credentials=st.session_state['creds'])

# --- UI HEADER ---
ch_data = youtube.channels().list(part="snippet,statistics,contentDetails", mine=True).execute()['items'][0]
col1, col2 = st.columns([1, 4])
col1.image(ch_data['snippet']['thumbnails']['high']['url'], width=100)
col2.title(ch_data['snippet']['title'])
col2.write(f"Subs: {ch_data['statistics']['subscriberCount']} | Views: {ch_data['statistics']['viewCount']}")

# --- CHAT ANALYZER ---
with st.expander("🔍 Analyze External Video Link"):
    link = st.text_input("Paste Video Link:")
    if st.button("Analyze Link"):
        res = client.models.generate_content(model="gemini-2.5-flash", contents=f"Analyze this video for SEO: {link}. Give actionable tips in Hinglish.")
        st.write(res.text)

# --- VIDEO LIST ---
st.divider()
uploads_id = ch_data['contentDetails']['relatedPlaylists']['uploads']
videos = youtube.playlistItems().list(playlistId=uploads_id, part="snippet", maxResults=50).execute()

for item in videos['items']:
    v_id = item['snippet']['resourceId']['videoId']
    cols = st.columns([1, 4])
    cols[0].image(item['snippet']['thumbnails']['default']['url'])
    if cols[1].button(f"Analyze: {item['snippet']['title']}", key=v_id):
        prompt = f"Analyze '{item['snippet']['title']}'. Return JSON: {{\"titles\": [\"t1\", \"t2\"], \"tags\": [\"tag1\", \"tag2\"]}}"
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        st.session_state['data'] = json.loads(response.text.replace('```json', '').replace('```', ''))
        st.session_state['vid_id'] = v_id
        st.rerun()

# --- UPDATE LOGIC ---
if 'data' in st.session_state:
    selected_title = st.radio("Choose Title:", st.session_state['data']['titles'])
    selected_tags = st.multiselect("Tags:", st.session_state['data']['tags'], default=st.session_state['data']['tags'])
    
    if st.button("Apply Changes to YouTube"):
        try:
            # Dynamic Category Fetch to avoid 403 Forbidden
            vid_resp = youtube.videos().list(id=st.session_state['vid_id'], part="snippet").execute()
            cat_id = vid_resp['items'][0]['snippet']['categoryId']
            
            youtube.videos().update(
                part="snippet",
                body={
                    "id": st.session_state['vid_id'],
                    "snippet": {
                        "title": selected_title,
                        "tags": selected_tags,
                        "categoryId": cat_id
                    }
                }
            ).execute()
            st.success("Successfully updated Title and Tags!")
        except Exception as e:
            st.error(f"Error: {e}")
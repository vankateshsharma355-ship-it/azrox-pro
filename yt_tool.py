import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow

# 1. Secrets se config load karein
# Streamlit secrets already ek dict-like object hai, 
# isliye json.loads ki zaroorat nahi hai.
client_secrets_dict = {
    "web": {
        "client_id": st.secrets.client_secrets.client_id,
        "client_secret": st.secrets.client_secrets.client_secret,
        "project_id": st.secrets.client_secrets.project_id,
        "auth_uri": st.secrets.client_secrets.auth_uri,
        "token_uri": st.secrets.client_secrets.token_uri,
        "auth_provider_x509_cert_url": st.secrets.client_secrets.auth_provider_x509_cert_url,
        "redirect_uris": st.secrets.client_secrets.redirect_uris
    }
}

# 2. Scopes define karein
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

# 3. Auth Flow setup karein
flow = InstalledAppFlow.from_client_config(
    client_secrets_dict, 
    scopes=scopes
)

st.title("Azrox Gaming YT Tool")
st.write("Authentication configuration successfully loaded!")

# Yahan apna YouTube API ka logic continue karein...

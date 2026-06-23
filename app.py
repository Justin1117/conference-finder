import streamlit as st
import os
from google import genai
from google.genai import types

# 1. Setup the webpage layout
st.set_page_config(page_title="Rural Oncology Conferences", layout="wide")

st.title("🌾 Upcoming Rural Oncology & Health Conferences")
st.write("This list automatically checks the live internet for upcoming professional events and refreshes once a month to save data.")

# 2. Connect to the Google AI Client Safely
try:
    client = genai.Client()
except Exception as e:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")

# 3. AUTOMATED SEARCH FUNCTION WITH TIME-TO-LIVE (TTL) CACHING
# 2,592,000 seconds = exactly 30 days. Change to 1209600 for 14 days.
@st.cache_data(ttl=2592000)
def fetch_conferences_from_web():
    # Hardcoded search parameters so the user doesn't have to type anything
    automated_query = "upcoming rural oncology health conferences annual meetings 2026 2027"
    
    system_prompt = f"""
    Search the live internet for upcoming professional conferences, webinars, or annual meetings regarding: {automated_query}.
    Provide a clean markdown table with the following columns:
    - Conference Name
    - Date
    - Location (or Virtual)
    - Brief Description
    - Website Link (Provide the actual working URL link)
    Only include public, official professional events. Do not include past events.
    """

    # Call Google Gemini and turn on the Live Search tool
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=system_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    
    # Extract the table text and the source chunk data safely
    table_content = response.text
    source_links = []
    try:
        sources = response.candidates.grounding_metadata.grounding_chunks
        for chunk in sources:
            source_links.append({"title": chunk.web.title, "url": chunk.web.uri})
    except:
        pass
        
    return table_content, source_links

# 4. Execute the Cached Search Automatically on Load
with st.spinner("Loading conference schedule..."):
    try:
        conference_table, used_sources = fetch_conferences_from_web()
        
        # Display the neat markdown table on the screen
        st.subheader("📅 Live Schedule")
        st.markdown(conference_table)
        
        # Create a dropdown box showing the exact websites used
        if used_sources:
            with st.expander("🌐 View Search Sources"):
                for source in used_sources:
                    st.markdown(f"- [{source['title']}]({source['url']})")
                    
    except Exception as e:
        st.error(f"Failed to auto-fetch data. Please check your API configuration. Error: {e}")

# --- HELP GUIDE (HIDDEN BACKGROUND COMMENT) ---
# To read these instructions later, just open this file on GitHub.
#
# 1. Go to https://aistudio.google.com
# 2. Log in and click "Get API Key"
# 3. Create a free key
# 4. Paste it into Streamlit Cloud Secrets as GEMINI_API_KEY


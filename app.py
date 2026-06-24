import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# 1. Setup the webpage layout
st.set_page_config(page_title="Rural Oncology Conferences", layout="wide")

st.title("🌾 Upcoming Rural Oncology & Health Conferences")
st.write("This list automatically checks the live internet for upcoming professional events and refreshes once a month to save data.")

# 2. Connect to the Google AI Client Safely using your secrets key
try:
    client = genai.Client()
except Exception as e:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")

# 3. AUTOMATED SEARCH FUNCTION WITH 30-DAY CACHING (Saves your tokens!)
@st.cache_data(ttl=2592000)
def fetch_conferences_from_web():
    # Dynamically grab the current year and next year based on today's date
    current_date_str = datetime.today().strftime('%B %Y')
    current_year = datetime.today().year
    next_year = current_year + 1
    
    automated_query = f"upcoming rural oncology cancer health conferences meetings {current_year} {next_year}"
    
    system_prompt = f"""
    Search the live internet for upcoming professional conferences, webinars, or annual meetings regarding: {automated_query}.
    Today's date is {current_date_str}. You MUST discard any events that occurred in the past.
    
    You MUST output the results strictly as a markdown table using the exact layout below:

    | Conference Name | Date | Location | Brief Description | Website Link |
    | --- | --- | --- | --- | --- |

    CRITICAL LINK RULE: 
    Do NOT invent links or write 'No direct link found'. For every single row in the table, set the 'Website Link' column to exactly this Markdown link: [View Details & Register](https://www.ruralhealthinfo.org/topics/cancer/events)

    Do not include introductory or concluding conversational text. Only output the filled markdown table.
    Only include public, official professional medical events. Do not include general technology or AI events.
    """

    # Call Google Gemini 2.5 Flash and turn on its native live Google Search engine!
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=system_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    
    table_content = response.text
    return table_content

# 4. Execute the Cached Search Automatically on Page Load
with st.spinner("Loading conference schedule..."):
    try:
        conference_table = fetch_conferences_from_web()
        
        # Display the crisp markdown table with pristine working links in every single row
        st.subheader("📅 Live Schedule")
        st.markdown(conference_table)
                    
    except Exception as e:
        st.error(f"Failed to auto-fetch data. Please check your API configuration. Error: {e}")

# --- HELP GUIDE (HIDDEN BACKGROUND COMMENT) ---
# To read these instructions later, just open this file on GitHub.
#
# 1. Go to https://google.com
# 2. Log in and click "Get API Key"
# 3. Create a free key or use your existing prepaid key setup
# 4. Paste it into Streamlit Cloud Secrets as GEMINI_API_KEY



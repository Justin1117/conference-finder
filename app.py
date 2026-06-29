import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

#Setup the webpage layout
st.set_page_config(page_title="Rural Oncology Conferences", layout="wide")

st.title("🌾 Upcoming Rural Oncology & Health Conferences")
st.write("This list automatically checks the live internet for upcoming professional events and refreshes once a month.")

#Connect to the Google AI Client Safely using your secrets key
try:
    client = genai.Client()
except Exception as e:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your Streamlit Secrets.")

#AUTOMATED SEARCH FUNCTION WITH 30-DAY CACHING (Saves your tokens!)
@st.cache_data(ttl=2592000)
def fetch_conferences_from_web():
    #Dynamically grab the current year and next year based on today's date
    current_date_str = datetime.today().strftime('%B %Y')
    current_year = datetime.today().year
    next_year = current_year + 1
    
    automated_query = f"upcoming rural oncology cancer health conferences meetings {current_year} {next_year}"
    
    system_prompt = f"""
    Search the live internet thoroughly for upcoming professional conferences, webinars, workshops, or annual meetings regarding: {automated_query} that will occur in the United States only.
    Today's date is {current_date_str}. You MUST discard any events that occurred in the past.
    
    You MUST output the results strictly as a markdown table using the exact layout below:

    | Conference Name | Date | Location | Brief Description | Website Link |
    | --- | --- | --- | --- | --- |

    CRITICAL LINK RULE:
    - To prevent broken link errors, format the 'Website Link' column using the verified parent domain URL found in your search metadata (for example: [ruralhealthinfo.org](https://ruralhealthinfo.org) or [cancer.org](https://cancer.org)). 
    - If a specific event link is not fully verified, link directly to the homepage of the organization hosting it. Never write 'No direct link found'.

    Do not include introductory or concluding conversational text. Only output the filled markdown table.
    Only include public, official professional medical events. Do not include general technology or AI events.
    """

    #Call Google Gemini 2.5 Flash and turn on its native live Google Search engine!
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=system_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    
    table_content = response.text
    return table_content

#Execute the Cached Search Automatically on Page Load
with st.spinner("Loading conference schedule..."):
    try:
        conference_table = fetch_conferences_from_web()
        
        #Display the complete table with reliable domain links built directly into rows
        st.subheader("📅 Live Schedule")
        st.markdown(conference_table)
                    
    except Exception as e:
        st.error(f"Failed to auto-fetch data. Please check your API configuration. Error: {e}")


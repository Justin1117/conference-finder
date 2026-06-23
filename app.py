import streamlit as st
import os
from google import genai
from google.genai import types

# 1. Setup the webpage layout
st.set_page_config(page_title="Rural Oncology Conference Finder", layout="wide")

st.title("🔍 Rural Oncology & Health Conference Finder")
st.write("Scan the live internet for upcoming medical conferences and events.")

# 2. Connect to the Google AI Client Safely
# This line looks for your secret key in the system environment variables
try:
    client = genai.Client()
except Exception as e:
    st.error("Missing API Key! Please add GEMINI_API_KEY to your system or Streamlit Secrets.")

# 3. Build the User Input Interface
search_topic = st.text_input(
    "What kind of conferences are you looking for?", 
    placeholder="e.g., upcoming rural oncology conferences 2026 2027"
)

# 4. Run the Search when the button is clicked
if search_topic:
    if st.button("Search Live Internet"):
        with st.spinner("Scanning the live web and organizing results into a table..."):
            try:
                # This prompt forces the AI to look at the web and build a clean data table
                system_prompt = f"""
                Search the live internet for upcoming professional conferences, webinars, or annual meetings regarding: {search_topic}.
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
                
                # 5. Display the neat markdown table on the screen
                st.success("Search complete!")
                st.subheader("📅 Upcoming Events Found")
                st.markdown(response.text)
                
                # Create a dropdown box showing the exact websites the AI used
                with st.expander("🌐 View Search Sources"):
                    try:
                        sources = response.candidates.grounding_metadata.grounding_chunks
                        for chunk in sources:
                            title = chunk.web.title
                            url = chunk.web.uri
                            st.markdown(f"- [{title}]({url})")
                    except:
                        st.write("Sources used, but could not be formatted into links.")
                        
            except Exception as e:
                st.error(f"Search failed. Please check your API Key. Error: {e}")

# --- HELP GUIDE IN THE SIDEBAR ---
"""
with st.sidebar:
    st.header("⚙️ Director's Admin Panel")
    st.write("This tool uses a free account key to search Google.")
    st.subheader("How to fix if it stops working:")
    st.markdown("1. Go to [://google.com](https://://google.com)\n2. Log in and click **Get API Key**\n3. Create a free key\n4. Paste it into Streamlit Cloud Secrets as `GEMINI_API_KEY`")
"""

import streamlit as st
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS
from datetime import datetime

# 1. Setup the webpage layout
st.set_page_config(page_title="Rural Oncology Conferences", layout="wide")

st.title("🌾 Upcoming Rural Oncology & Health Conferences")
st.write("This list automatically checks the live internet for upcoming professional events and refreshes once a month to save data.")

# 2. Connect to the Free Hugging Face Client Safely
hf_token = st.secrets.get("HUGGINGFACE_TOKEN")

if not hf_token:
    st.error("Missing API Token! Please add HUGGINGFACE_TOKEN to your Streamlit Secrets.")
else:
    client = InferenceClient(token=hf_token)

# 3. CACHED INTERNET DATA RETRIEVAL (Only searches the web once a month)
@st.cache_data(ttl=2592000)
def fetch_raw_search_results():
    current_year = datetime.today().year
    next_year = current_year + 1
    automated_query = f"rural oncology cancer healthcare conferences meetings {current_year} {next_year}"
    
    raw_results = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(automated_query, max_results=8))
            for i, r in enumerate(results, 1):
                raw_results.append({
                    "index": i,
                    "title": r['title'],
                    "body": r['body'],
                    "url": r['href']
                })
    except Exception as e:
        pass
    return raw_results

# 4. Execute the App Layout Flow on Page Load
if hf_token:
    with st.spinner("Loading conference schedule..."):
        try:
            # Always grab raw data from the 30-day safe cache storage
            cached_search_data = fetch_raw_search_results()
            
            # Format the text payload for the AI processor
            search_results_text = ""
            for item in cached_search_data:
                search_results_text += f"RESULT #{item['index']}\nTitle: {item['title']}\nDetails: {item['body']}\n\n"
            
            current_date_str = datetime.today().strftime('%B %Y')
            current_year = datetime.today().year
            next_year = current_year + 1

            system_prompt = f"""
            You are a medical administrative assistant. Your job is to extract upcoming rural healthcare, medical, and oncology conferences from the search results below.
            
            CRITICAL CHRONOLOGICAL RULES:
            - Today's date is {current_date_str}.
            - Discard any conferences that occurred in the past. Only include future events for {current_year} or {next_year}.
            - Discard any entries about general tech or AI. Only include healthcare/oncology.

            Search Results to parse:
            {search_results_text}

            You MUST output your findings strictly as a markdown table using the exact layout below. 
            In the 'Source Reference' column, simply output the text 'Source #X' matching the RESULT #X from the search results.

            | Conference Name | Date | Location | Brief Description | Source Reference |
            | --- | --- | --- | --- | --- |

            Do not include introductory text, conversational text, or summary text. Only output the markdown table.
            """

            # Run the generation call
            response = client.chat.completions.create(
                model="Qwen/Qwen2.5-72B-Instruct",
                messages=[{"role": "user", "content": system_prompt}],
                max_tokens=1500,
                temperature=0.1
            )
            
            # Flexible string conversion checks
            if hasattr(response, 'choices') and len(response.choices) > 0:
                conference_table = response.choices.message.content
            elif isinstance(response, dict):
                conference_table = response.get("choices", [{}]).get("message", {}).get("content", "")
            else:
                conference_table = str(response)
            
            # Render the Data Table on screen
            st.subheader("📅 Live Schedule")
            st.markdown(conference_table)
            
            # Render the Link Module on screen
            if cached_search_data:
                st.write("---")
                st.subheader("🔗 Verified Official Website Links")
                st.write("Click the links below to open the official websites for the sources referenced in the table above:")
                
                col1, col2 = st.columns(2)
                for index, source in enumerate(cached_search_data):
                    display_text = f"**Source #{source['index']}**: [{source['title']}]({source['url']})"
                    if index % 2 == 0:
                        col1.markdown(display_text)
                    else:
                        col2.markdown(display_text)
                        
        except Exception as e:
            st.error(f"Failed to auto-fetch data. Please check your API configuration. Error: {e}")

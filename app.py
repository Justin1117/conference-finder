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

# 3. AUTOMATED SEARCH FUNCTION WITH 30-DAY CACHING
@st.cache_data(ttl=2592000)
def fetch_conferences_from_web():
    # Dynamically grab today's date so the system always knows the present timeline
    current_date_str = datetime.today().strftime('%B %Y')
    current_year = datetime.today().year
    next_year = current_year + 1
    
    # Force search results into future timelines
    automated_query = f"rural oncology cancer healthcare conferences meetings {current_year} {next_year}"
    
    search_results_text = ""
    source_links = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(automated_query, max_results=7))
            for r in results:
                search_results_text += f"CONFERENCE WEBSITE DATA:\nTitle: {r['title']}\nDetails: {r['body']}\nURL: {r['href']}\n\n"
                source_links.append({"title": r['title'], "url": r['href']})
    except Exception as e:
        search_results_text = "Could not pull live web text due to search engine rate limits."

    # Direct the AI with explicit dynamic constraints
    system_prompt = f"""
    You are a medical administrative assistant. Your job is to extract upcoming rural healthcare, medical, and oncology conferences from the search results below.
    
    CRITICAL CHRONOLOGICAL RULES:
    - Today's date is {current_date_str}.
    - You MUST evaluate the date of every conference.
    - If a conference has already taken place or occurred in the past relative to {current_date_str}, DISCARD IT. 
    - Only include future professional events scheduled for late {current_year} or {next_year}.
    - Do not include general AI, tech, or unrelated non-medical entries.

    Search Results to parse:
    {search_results_text}

    You MUST output your findings strictly as a markdown table using the exact layout below:

    | Conference Name | Date | Location | Brief Description | Website Link |
    | --- | --- | --- | --- | --- |

    Do not include introductory text, conversational text, or summary text. Only output the markdown table.
    """

    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-72B-Instruct",
        messages=[{"role": "user", "content": system_prompt}],
        max_tokens=1500,
        temperature=0.1
    )
    
    table_content = response.choices[0].message.content
    return table_content, source_links

# 4. Execute the Cached Search Automatically on Page Load
if hf_token:
    with st.spinner("Loading conference schedule..."):
        try:
            conference_table, used_sources = fetch_conferences_from_web()
            
            st.subheader("📅 Live Schedule")
            st.markdown(conference_table)
            
            if used_sources:
                with st.expander("🌐 View Search Sources"):
                    for source in used_sources:
                        st.markdown(f"- [{source['title']}]({source['url']})")
                        
        except Exception as e:
            st.error(f"Failed to auto-fetch data. Please check your API configuration. Error: {e}")

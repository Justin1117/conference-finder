import streamlit as st
from huggingface_hub import InferenceClient
from duckduckgo_search import DDGS

# 1. Setup the webpage layout
st.set_page_config(page_title="Rural Oncology Conferences", layout="wide")

st.title("🌾 Upcoming Rural Oncology & Health Conferences")
st.write("This list automatically checks the live internet for upcoming professional events and refreshes once a month to save data.")

# 2. Connect to the Free Hugging Face Client Safely
# Looks for HUGGINGFACE_TOKEN in your Streamlit Cloud Secrets
hf_token = st.secrets.get("HUGGINGFACE_TOKEN")

if not hf_token:
    st.error("Missing API Token! Please add HUGGINGFACE_TOKEN to your Streamlit Secrets.")
else:
    # Use Meta's powerful open-source Llama model for free
    client = InferenceClient("meta-llama/Meta-Llama-3-8B-Instruct", token=hf_token)

# 3. AUTOMATED SEARCH FUNCTION WITH 30-DAY CACHING
@st.cache_data(ttl=2592000)
def fetch_conferences_from_web():
    automated_query = "upcoming rural oncology health conferences annual meetings 2026 2027"
    
    # Run a free live search using DuckDuckGo
    search_results_text = ""
    source_links = []
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(automated_query, max_results=5))
            for r in results:
                search_results_text += f"Title: {r['title']}\nSnippet: {r['body']}\nURL: {r['href']}\n\n"
                source_links.append({"title": r['title'], "url": r['href']})
    except Exception as e:
        search_results_text = "Could not pull live web text due to search engine rate limits."

    # Craft the instructions for the free AI model using the search data
    system_prompt = f"""
    You are an expert scheduler. Organize the following live internet search results into a clean markdown table.
    
    Search Results:
    {search_results_text}

    You MUST output the results strictly as a markdown table using the exact layout below:

    | Conference Name | Date | Location | Brief Description | Website Link |
    | --- | --- | --- | --- | --- |

    Do not include introductory or concluding conversational text. Only output the filled table.
    Only include public, official professional events. Do not include past events.
    """

    # Call the free Hugging Face API
    response = client.text_generation(
        system_prompt,
        max_new_tokens=1500,
        temperature=0.1
    )
    
    return response, source_links

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




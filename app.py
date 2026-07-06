import streamlit as st
import requests

# Configure the page layout
st.set_page_config(page_title="Quick Summarizer AI", layout="wide")

st.title("Quick Summarizer AI ⚡")
st.caption("Powered by BART-Large-CNN via Hugging Face API | True Abstractive Summarization")

# Public API URL for the model (No auth key needed for basic usage)
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

def query_api(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()

# Main UI Division
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input Text")
    text_input = st.text_area("Paste your text or article here:", height=350)
    submit_button = st.button("Summarize", type="primary")

with col2:
    st.subheader("AI Insights")
    if submit_button:
        if not text_input.strip():
            st.warning("Please paste some text to analyze.")
        elif len(text_input.split()) < 20:
            st.warning("Please enter a longer text block for meaningful abstractive analysis.")
        else:
            with st.spinner("Generating abstractive summary via API..."):
                try:
                    # Call the cloud model
                    output = query_api({
                        "inputs": text_input,
                        "parameters": {"max_length": 130, "min_length": 30, "do_sample": False}
                    })
                    
                    # Extract text from API response structure
                    if isinstance(output, list) and "summary_text" in output[0]:
                        summary_text = output[0]["summary_text"]
                        st.markdown("### Key Summary")
                        st.write(summary_text)
                    else:
                        st.error("API is warming up or busy. Please try clicking the button again in a few seconds.")
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
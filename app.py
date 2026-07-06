import streamlit as st
from transformers import pipeline

# Configure the page layout
st.set_page_config(page_title="Quick Summarizer AI", layout="wide")

st.title("Quick Summarizer AI ⚡")
st.caption("Powered by Hugging Face Transformers | No API Key Required")

# Initialize the pipeline and cache it so it doesn't reload on every click
@st.cache_resource
def load_summarizer():
    # Uses a lightweight, fast model ideal for basic deployment slots
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

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
        elif len(text_input.split()) < 10:
            st.warning("Please enter a longer text block to summarize.")
        else:
            with st.spinner("Processing content..."):
                try:
                    # Run the pipeline
                    summary_result = summarizer(text_input, max_length=150, min_length=30, do_sample=False)
                    summary_text = summary_result[0]['summary_text']
                    
                    # Render output
                    st.markdown("### Key Summary")
                    st.write(summary_text)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
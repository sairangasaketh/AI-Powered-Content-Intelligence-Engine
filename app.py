import streamlit as st
import google.generativeai as genai
import os

# Configure the page layout
st.set_page_config(page_title="Quick Summarizer AI", layout="wide")

st.title("Quick Summarizer AI ⚡")
st.caption("Powered by Gemini API | Deployed instantly with Streamlit Community Cloud")

# Sidebar for secure API key configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    if api_key:
        genai.configure(api_key=api_key)

# Main UI Division
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input Text")
    text_input = st.text_area("Paste your text or article here:", height=350)
    submit_button = st.button("Summarize & Extract Keywords", type="primary")

with col2:
    st.subheader("AI Insights")
    if submit_button:
        if not api_key:
            st.error("Please provide a valid Gemini API key in the sidebar.")
        elif not text_input.strip():
            st.warning("Please paste some text to analyze.")
        else:
            with st.spinner("Processing content..."):
                try:
                    # Construct a clear prompt targeting both summary bullets and comma-separated tags
                    prompt = f"""
                    Analyze the following text. Provide two distinct outputs formatted clearly:
                    1. A 'Key Summary' section consisting of 3-4 bullet points highlighting the main ideas.
                    2. A 'Generated Keywords' section containing 5 relevant keywords or topics separated by commas.

                    Text to analyze:
                    {text_input}
                    """
                    
                    # Call the Gemini model
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(prompt)
                    
                    # Render the model output directly inside the column
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
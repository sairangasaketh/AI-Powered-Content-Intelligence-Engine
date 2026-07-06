import streamlit as st
import collections
import re

# Configure the page layout
st.set_page_config(page_title="Quick Summarizer AI", layout="wide")

st.title("Quick Summarizer AI ⚡")
st.caption("Powered by Frequency Analysis Pipeline | Safe & Rapid Deployment")

def frequency_summarizer(text, num_sentences=3):
    # Clean and tokenize sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    if len(sentences) <= num_sentences:
        return text, list(set(re.findall(r'\b\w{5,}\b', text.lower())))[:5]
        
    # Calculate word frequencies, skipping common stopwords
    stopwords = set(["the", "and", "is", "of", "to", "in", "it", "that", "this", "for", "with", "was", "as", "on", "but", "are"])
    words = re.findall(r'\b\w+\b', text.lower())
    word_frequencies = collections.Counter(w for w in words if w not in stopwords)
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        for word in re.findall(r'\b\w+\b', sentence.lower()):
            if word in word_frequencies:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + word_frequencies[word]
                
    # Extract top sentences
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = " ".join(top_sentences)
    
    # Extract top keywords
    keywords = [item[0] for item in word_frequencies.most_common(5)]
    return summary, keywords

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
        else:
            with st.spinner("Processing content..."):
                try:
                    summary_text, keywords = frequency_summarizer(text_input)
                    
                    # Render output
                    st.markdown("### Key Summary")
                    st.write(summary_text)
                    
                    st.markdown("### Keywords")
                    st.write(", ".join(keywords))
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
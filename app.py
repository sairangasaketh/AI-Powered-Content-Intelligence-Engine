import streamlit as st
import random
import re

st.set_page_config(page_title="Quick Summarizer AI", layout="wide")
st.title("Quick Summarizer AI ⚡")
st.caption("Powered by Local Markov Chain Synthesis | No Network or API Dependencies")

def build_markov_model(text):
    words = re.findall(r'\b\w+\b', text)
    model = {}
    for i in range(len(words) - 2):
        key = (words[i].lower(), words[i+1].lower())
        next_word = words[i+2]
        if key not in model:
            model[key] = []
        model[key].append(next_word)
    return model, words

def generate_abstractive_summary(text, num_sentences=3):
    model, words = build_markov_model(text)
    if len(words) < 20:
        return text
    
    sentences = []
    # Capitalized words to start sentences realistically
    start_words = [w for w in words if w[0].isupper() and w.lower() in [k[0] for k in model.keys()]]
    if not start_words:
        start_words = [k[0] for k in model.keys()]

    for _ in range(num_sentences):
        w1 = random.choice(start_words).lower()
        # Find a valid second word matching our state matrix
        valid_keys = [k for k in model.keys() if k[0] == w1]
        if not valid_keys:
            continue
        w2 = random.choice(valid_keys)[1]
        
        sentence = [w1.capitalize(), w2]
        
        for _ in range(20): # Max sentence length cap
            key = (w1, w2)
            if key in model:
                next_word = random.choice(model[key])
                sentence.append(next_word)
                w1, w2 = w2, next_word.lower()
                if next_word.endswith(('.', '!', '?')) or random.random() > 0.85:
                    break
            else:
                break
                
        sentence_str = " ".join(sentence)
        if not sentence_str.endswith('.'):
            sentence_str += '.'
        sentences.append(sentence_str)
        
    return " ".join(sentences)

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
            with st.spinner("Synthesizing text summary..."):
                try:
                    summary_text = generate_abstractive_summary(text_input)
                    st.markdown("### Key Summary")
                    st.write(summary_text)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
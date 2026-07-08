import streamlit as st
import pandas as pd
import sqlite3
from google import genai
import re

# Page Configuration
st.set_page_config(page_title="Universal AI SQL Agent", layout="wide")
st.title("Universal AI SQL Agent 🤖📊")
st.caption("Powered by Gemini 2.5 Flash API | Universal Compatibility Runtime")

# 1. API Key Setup via Sidebar (Zero Cloud Configuration Needed)
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("[Get a free Gemini API Key here](https://aistudio.google.com/)")

# 2. Local Database Setup
@st.cache_resource
def init_clean_db():
    conn = sqlite3.connect("crop_analytics.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crop_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop_name TEXT,
            region TEXT,
            rainfall_required INTEGER,
            fertilizer_used TEXT,
            yield_mt INTEGER
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM crop_data")
    if cursor.fetchone()[0] == 0:
        mock_records = [
            ('Wheat', 'North', 80, 'Yes', 4500),
            ('Rice', 'South', 200, 'Yes', 6200),
            ('Maize', 'West', 120, 'No', 3100),
            ('Barley', 'North', 90, 'No', 2800),
            ('Sugarcane', 'East', 250, 'Yes', 8900)
        ]
        cursor.executemany("INSERT INTO crop_data (crop_name, region, rainfall_required, fertilizer_used, yield_mt) VALUES (?, ?, ?, ?, ?)", mock_records)
        conn.commit()
    return conn

db_conn = init_clean_db()

# Display active database preview
st.subheader("📋 Underlying Database Records")
df_preview = pd.read_sql_query("SELECT * FROM crop_data", db_conn)
st.dataframe(df_preview, use_container_width=True, hide_index=True)
st.markdown("---")

# 3. Native API Query Compiler
def call_gemini_compiler(user_prompt, api_token):
    # Initialize the modern, lightweight client structure
    client = genai.Client(api_key=api_token)
    
    system_instruction = """
    You are an expert SQL Developer. Translate the user's natural language request into a valid, optimized SQLite query.
    
    Database Table Schema:
    Table Name: crop_data
    Columns:
    - crop_name (TEXT)
    - region (TEXT)
    - rainfall_required (INTEGER)
    - fertilizer_used (TEXT)
    - yield_mt (INTEGER)
    
    Return ONLY the raw SQL query string inside markdown blocks like this:
    ```sql
    SELECT * FROM crop_data;
    ```
    Do not add extra explanations or conversational text.
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config={'system_instruction': system_instruction}
    )
    return response.text

# 4. Core UI Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Natural Language Input")
    user_query = st.text_input("Ask a question about the dataset:", placeholder="Which crop has the highest yield?")
    execute_btn = st.button("Compile & Execute", type="primary")

with col2:
    st.subheader("Execution Output")
    if execute_btn:
        if not api_key:
            st.error("Please enter your Gemini API Key in the left sidebar to proceed.")
        elif not user_query.strip():
            st.warning("Please enter a valid query string.")
        else:
            with st.spinner("Streaming response from Gemini..."):
                try:
                    # Request SQL generation from LLM
                    raw_llm_output = call_gemini_compiler(user_query, api_key)
                    
                    # Extract clean SQL block using regex
                    sql_match = re.search(r"```sql\n(.*?)```", raw_llm_output, re.DOTALL)
                    compiled_sql = sql_match.group(1).strip() if sql_match else raw_llm_output.strip()
                    
                    st.markdown("### Generated SQL Query")
                    st.code(compiled_sql, language="sql")
                    
                    # Execute on local database matrix
                    result_df = pd.read_sql_query(compiled_sql, db_conn)
                    st.markdown("### Returned Results")
                    st.dataframe(result_df, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Pipeline Execution Error: {str(e)}")
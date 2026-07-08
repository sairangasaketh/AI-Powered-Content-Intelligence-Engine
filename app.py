import streamlit as st
import pandas as pd
import sqlite3
import re
from google import genai

# Page Configuration
st.set_page_config(page_title="Universal AI SQL Agent", layout="wide")
st.title("Universal AI SQL Agent 🤖📊")
st.caption("Powered by Gemini 2.5 Flash API | Dynamic CSV & Excel File Uploads")

# 1. API Key Setup via Sidebar
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("[Get a free Gemini API Key here](https://aistudio.google.com/)")

# Initialize persistent in-memory database connection
@st.cache_resource
def get_db_connection():
    return sqlite3.connect(":memory:", check_same_thread=False)

conn = get_db_connection()

# --- STEP 1: DYNAMIC FILE UPLOAD (CSV or XLSX) ---
st.subheader("📁 Step 1: Upload Your Dataset")
uploaded_file = st.file_uploader("Upload a CSV or Excel file to query", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Check extension and parse accordingly
    file_name = uploaded_file.name.lower()
    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
            
        # Clean column names for safe SQL execution
        df.columns = [re.sub(r'\W+', '_', col.strip().lower()) for col in df.columns]
        
        # Derive a clean table name from filename
        table_name = re.sub(r'\W+', '_', uploaded_file.name.split('.')[0].lower())
        
        # Write to in-memory database
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        
        st.success(f"Successfully loaded table **'{table_name}'** with {len(df)} records!")
        st.markdown("### Live Dataset Preview")
        st.dataframe(df.head(5), use_container_width=True, hide_index=True)
        st.markdown("---")
        
    except Exception as e:
        st.error(f"Error parsing file: {str(e)}")
        st.stop()

    # --- STEP 2: NATIVE API QUERY COMPILER ---
    def call_gemini_compiler(user_prompt, api_token, t_name, df_columns):
        client = genai.Client(api_key=api_token)
        
        system_instruction = f"""
        You are an expert SQL Developer. Translate the user's natural language request into a valid, optimized SQLite query.
        
        Database Table Target: {t_name}
        Available Columns: {', '.join(df_columns)}
        
        Return ONLY the raw SQL query string inside markdown blocks like this:
        ```sql
        SELECT * FROM {t_name};
        ```
        Do not add extra explanations or conversational text.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config={'system_instruction': system_instruction}
        )
        return response.text

    # --- STEP 3: USER QUERY INTERFACE ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Natural Language Input")
        st.markdown(f"**Detected Table Columns:** `{', '.join(df.columns)}`")
        user_query = st.text_input("Ask a question about your uploaded dataset:", placeholder="e.g., Show top 5 records")
        execute_btn = st.button("Compile & Execute", type="primary")

    with col2:
        st.subheader("Execution Output")
        if execute_btn:
            if not api_key:
                st.error("Please enter your Gemini API Key in the left sidebar to proceed.")
            elif not user_query.strip():
                st.warning("Please enter a valid query string.")
            else:
                with st.spinner("Streaming query from Gemini pipeline..."):
                    try:
                        raw_llm_output = call_gemini_compiler(user_query, api_key, table_name, df.columns)
                        
                        # Extract clean SQL block using regex
                        sql_match = re.search(r"```sql\n(.*?)```", raw_llm_output, re.DOTALL)
                        compiled_sql = sql_match.group(1).strip() if sql_match else raw_llm_output.strip()
                        
                        st.markdown("### Generated SQL Query")
                        st.code(compiled_sql, language="sql")
                        
                        # Execute query on the newly loaded database state
                        result_df = pd.read_sql_query(compiled_sql, conn)
                        st.markdown("### Returned Results")
                        st.dataframe(result_df, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Pipeline Execution Error: {str(e)}")
else:
    st.info("💡 Please upload a CSV or Excel (.xlsx) file above to launch the interactive agent pipeline.")
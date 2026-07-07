import streamlit as st
import pandas as pd
import sqlite3
import re

# Page Setup
st.set_page_config(page_title="Dynamic AI SQL Agent", layout="wide")
st.title("Dynamic AI SQL Agent 🤖📊")
st.caption("Upload Any Table -> Ask in English -> Generate SQL & Query Live Data")

# Initialize a persistent in-memory database connection
@st.cache_resource
def get_db_connection():
    return sqlite3.connect(":memory:", check_same_thread=False)

conn = get_db_connection()

# --- STEP 1: DYNAMIC FILE UPLOAD ---
st.subheader("📁 Step 1: Upload Your Dataset")
uploaded_file = st.file_uploader("Upload a CSV file to query", type=["csv"])

if uploaded_file is not None:
    # Read the dataset and clean column names for safe SQL execution
    df = pd.read_csv(uploaded_file)
    df.columns = [re.sub(r'\W+', '_', col.strip().lower()) for col in df.columns]
    
    # Deriving table name from filename
    table_name = re.sub(r'\W+', '_', uploaded_file.name.split('.')[0].lower())
    
    # Save the dataframe to our in-memory SQLite database
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    
    # Display the dynamic table data preview
    st.success(f"Successfully loaded table **'{table_name}'** with {len(df)} records!")
    st.markdown("### Live Table Preview")
    st.dataframe(df.head(5), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # --- STEP 2: DYNAMIC INTENT MAPPING ---
    # Fetch available numerical and text columns on the fly
    all_columns = list(df.columns)
    numeric_cols = list(df.select_dtypes(include=['number']).columns)
    text_cols = list(df.select_dtypes(include=['object']).columns)
    
    def dynamic_sql_compiler(user_query, table, cols, num_cols, txt_cols):
        raw = user_query.lower().strip()
        
        # Fallback default configuration
        projection = "*"
        where_conditions = []
        order_by = ""
        group_by = ""
        
        # Dynamically discover which column the user might be referring to
        target_num_col = num_cols[0] if num_cols else "*"
        target_txt_col = txt_cols[0] if txt_cols else "*"
        
        # Scrape columns mentioned explicitly in the query text
        for c in cols:
            if c in raw:
                if c in num_cols:
                    target_num_col = c
                if c in txt_cols:
                    target_txt_col = c

        # Dynamic Intent Analyzer
        if "highest" in raw or "max" in raw or "top" in raw:
            if target_num_col != "*":
                order_by = f"ORDER BY {target_num_col} DESC LIMIT 1"
        elif "lowest" in raw or "min" in raw:
            if target_num_col != "*":
                order_by = f"ORDER BY {target_num_col} ASC LIMIT 1"
        elif "average" in raw or "avg" in raw:
            if target_num_col != "*":
                projection = f"AVG({target_num_col}) AS average_{target_num_col}"
        elif "total" in raw or "sum" in raw:
            if target_num_col != "*":
                projection = f"SUM({target_num_col}) AS total_{target_num_col}"
        elif "count" in raw or "how many" in raw:
            projection = "COUNT(*) AS total_records"
            if "by" in raw or "group by" in raw:
                if target_txt_col != "*":
                    projection = f"{target_txt_col}, COUNT(*) AS count"
                    group_by = f"GROUP BY {target_txt_col}"

        # Extract values for conditional matching (e.g., matching text labels or numeric parameters)
        numbers = re.findall(r'\b\d+\b', raw)
        if numbers and target_num_col != "*":
            if ">" in raw or "greater" in raw or "more than" in raw:
                where_conditions.append(f"{target_num_col} > {numbers[0]}")
            elif "<" in raw or "less" in raw or "under" in raw:
                where_conditions.append(f"{target_num_col} < {numbers[0]}")

        # Construct final executable structure dynamically
        where_stmt = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        sql_blocks = [f"SELECT {projection}", f"FROM {table}", where_stmt, group_by, order_by]
        
        return " ".join([b for b in sql_blocks if b.strip()]) + ";"

    # --- STEP 3: USER QUERY INTERFACE ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Ask Questions in English")
        st.markdown(f"**Detected Columns:** {', '.join(all_columns)}")
        st.caption("💡 Your intent engine dynamically detects column data types and generates accurate SQL structures.")
        
        user_input = st.text_input("What would you like to analyze from this dataset?", placeholder="e.g., Show the record with the highest value")
        execute_btn = st.button("Compile & Execute", type="primary")

    with col2:
        st.subheader("Relational Compilation Output")
        if execute_btn:
            if not user_input.strip():
                st.warning("Please type an evaluation parameter or prompt.")
            else:
                with st.spinner("Analyzing upload schema parameters..."):
                    try:
                        # Compile query based on dynamically generated file constraints
                        generated_sql = dynamic_sql_compiler(user_input, table_name, all_columns, numeric_cols, text_cols)
                        
                        st.markdown("### Context-Generated SQL")
                        st.code(generated_sql, language="sql")
                        
                        # Fetch and serve database data matrix
                        result_df = pd.read_sql_query(generated_sql, conn)
                        st.markdown("### Query Results Table")
                        st.dataframe(result_df, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Execution Error: {str(e)}")
else:
    st.info("💡 Please upload a CSV file above to launch the interactive dynamic database agent pipeline.")
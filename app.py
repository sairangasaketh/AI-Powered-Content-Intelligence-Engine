import streamlit as st
import pandas as pd
import sqlite3
import re

# Page Config
st.set_page_config(page_title="AI SQL Analytics Agent", layout="wide")
st.title("AI SQL Analytics Agent 🤖📊")
st.caption("Context-Aware Natural Language to SQL Translation Engine | Zero API Key Dependencies")

# 1. In-Memory Database Setup for Live Execution Simulation
@st.cache_resource
def init_database():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    
    # Create an Employee Analytics Table
    cursor.execute("""
        CREATE TABLE employees (
            emp_id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary INTEGER,
            hire_date TEXT
        )
    """)
    
    # Insert Mock Enterprise Data
    mock_data = [
        (101, 'Saketh', 'AI/ML', 145000, '2026-01-15'),
        (102, 'Ananya', 'Data Science', 125000, '2025-06-20'),
        (103, 'Rahul', 'Full Stack', 98000, '2024-11-02'),
        (104, 'Priya', 'AI/ML', 160000, '2025-03-10'),
        (105, 'Vikram', 'Data Science', 110000, '2026-02-01')
    ]
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", mock_data)
    conn.commit()
    return conn

db_conn = init_database()

# 2. Rule-Based Semantic Translation Engine (Simulating LLM Token Processing)
def translate_text_to_sql(user_query):
    query = user_query.lower().strip()
    
    # Base schema definitions
    select_clause = "SELECT * FROM employees"
    where_clause = ""
    order_clause = ""
    
    # Department Extraction
    if "ai/ml" in query or "ai" in query:
        where_clause = "WHERE department = 'AI/ML'"
    elif "data science" in query or "data" in query:
        where_clause = "WHERE department = 'Data Science'"
    elif "full stack" in query:
        where_clause = "WHERE department = 'Full Stack'"
        
    # Aggregate Operations
    if "highest salary" in query or "highest paid" in query:
        order_clause = "ORDER BY salary DESC LIMIT 1"
    elif "total salary" in query or "budget" in query:
        select_clause = "SELECT SUM(salary) AS Total_Budget FROM employees"
    elif "average salary" in query or "avg salary" in query:
        select_clause = "SELECT AVG(salary) AS Average_Salary FROM employees"
    elif "count" in query or "how many" in query:
        if where_clause:
            select_clause = "SELECT COUNT(*) AS Employee_Count FROM employees"
        else:
            select_clause = "SELECT COUNT(*) AS Total_Employees FROM employees"
            
    # Combine clauses logically
    sql_parts = [select_clause]
    if where_clause:
        sql_parts.append(where_clause)
    if order_clause:
        sql_parts.append(order_clause)
        
    final_sql = " ".join(sql_parts) + ";"
    return final_sql

# 3. Interactive UI layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Database Schema Context")
    st.markdown("""
    ```sql
    CREATE TABLE employees (
        emp_id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary INTEGER,
        hire_date TEXT
    );
    ```
    """)
    st.caption("💡 Try asking: 'Show all employees in AI/ML', 'What is the average salary?', or 'Who has the highest paid job?'")
    
    user_input = st.text_input("Enter your natural language question:", placeholder="e.g., Show me employees in Data Science")
    generate_btn = st.button("Translate & Execute", type="primary")

with col2:
    st.subheader("AI Compilation & Execution Output")
    if generate_btn:
        if not user_input.strip():
            st.warning("Please input a natural language query.")
        else:
            with st.spinner("Compiling tokens to SQL tokens..."):
                try:
                    # Generate the translation
                    generated_sql = translate_text_to_sql(user_input)
                    
                    st.markdown("### Generated SQL Query")
                    st.code(generated_sql, language="sql")
                    
                    # Execute generated query directly on the in-memory database
                    df_results = pd.read_sql_query(generated_sql, db_conn)
                    
                    st.markdown("### Executed Dataset Results")
                    st.dataframe(df_results, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Execution Engine Error: {str(e)}")
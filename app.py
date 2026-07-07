import streamlit as st
import pandas as pd
import sqlite3
import re

st.set_page_config(page_title="AI SQL Analytics Agent", layout="wide")
st.title("AI SQL Analytics Agent 🤖📊")
st.caption("Advanced Semantic AST Compiler | Complex Operations & Multi-Table Joins")

# 1. Multi-Table Relational Database Setup
@st.cache_resource
def init_advanced_database():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    
    # Core Table 1: Employees
    cursor.execute("""
        CREATE TABLE employees (
            emp_id INTEGER PRIMARY KEY,
            name TEXT,
            dept_id INTEGER,
            salary INTEGER,
            hire_date TEXT
        )
    """)
    
    # Core Table 2: Departments
    cursor.execute("""
        CREATE TABLE departments (
            dept_id INTEGER PRIMARY KEY,
            dept_name TEXT,
            location TEXT,
            budget INTEGER
        )
    """)
    
    # Seed Relational Datasets
    cursor.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)", [
        (1, 'AI/ML', 'Tirupati', 500000),
        (2, 'Data Science', 'Hyderabad', 400000),
        (3, 'Full Stack', 'Bangalore', 300000)
    ])
    
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?)", [
        (101, 'Saketh', 1, 145000, '2026-01-15'),
        (102, 'Ananya', 2, 125000, '2025-06-20'),
        (103, 'Rahul', 3, 98000, '2024-11-02'),
        (104, 'Priya', 1, 160000, '2025-03-10'),
        (105, 'Vikram', 2, 110000, '2026-02-01')
    ])
    conn.commit()
    return conn

db_conn = init_advanced_database()

# 2. Advanced AST Lexical Parser Component
def compile_complex_query(user_prompt):
    raw = user_prompt.lower().strip()
    
    # Structural AST Components
    projection = "e.emp_id, e.name, d.dept_name, e.salary"
    base_relations = "FROM employees e JOIN departments d ON e.dept_id = d.dept_id"
    conditions = []
    group_by = ""
    order_by = ""
    
    # A. Semantic Value Scanners (Detect exact literals within user prompts)
    salary_extract = re.findall(r'\b\d{5,}\b', raw)
    
    # B. Conditionals Engine 
    if "salary greater than" in raw or "earning more than" in raw or "salary >" in raw:
        if salary_extract:
            conditions.append(f"e.salary > {salary_extract[0]}")
    elif "salary less than" in raw or "salary <" in raw:
        if salary_extract:
            conditions.append(f"e.salary < {salary_extract[0]}")
            
    # C. Relational Scope Adjuster (Locate context targets across tables)
    if "ai/ml" in raw or "ai" in raw:
        conditions.append("d.dept_name = 'AI/ML'")
    elif "data science" in raw or "data" in raw:
        conditions.append("d.dept_name = 'Data Science'")
    elif "full stack" in raw:
        conditions.append("d.dept_name = 'Full Stack'")
        
    if "hyd" in raw or "hyderabad" in raw:
        conditions.append("d.location = 'Hyderabad'")
    elif "tirupati" in raw:
        conditions.append("d.location = 'Tirupati'")

    # D. Aggregate & Matrix Functions
    if "average salary" in raw or "avg salary" in raw:
        if "by department" in raw or "per department" in raw or "department wise" in raw:
            projection = "d.dept_name, AVG(e.salary) AS Average_Salary"
            group_by = "GROUP BY d.dept_name"
        else:
            projection = "AVG(e.salary) AS Global_Average_Salary"
            
    elif "total budget" in raw or "sum of budget" in raw:
        projection = "SUM(d.budget) AS Total_Operational_Budget"
        base_relations = "FROM departments d"
        conditions = [c for c in conditions if "dept_name" in c or "location" in c] # Strip out employee dependencies
        
    elif "highest paid" in raw or "maximum salary" in raw or "most money" in raw:
        order_by = "ORDER BY e.salary DESC LIMIT 1"
        
    elif "lowest paid" in raw or "minimum salary" in raw:
        order_by = "ORDER BY e.salary ASC LIMIT 1"

    # E. Query Synthesizer Pipeline
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    sql_components = [f"SELECT {projection}", base_relations, where_clause, group_by, order_by]
    clean_sql = " ".join([parts for parts in sql_components if parts.strip()]) + ";"
    return clean_sql

# 3. Execution Interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Relational Database Infrastructure")
    st.markdown("""
    ```sql
    -- Relational Schema Context Configuration
    CREATE TABLE employees (emp_id INT, name TEXT, dept_id INT, salary INT);
    CREATE TABLE departments (dept_id INT, dept_name TEXT, location TEXT, budget INT);
    ```
    """)
    st.caption("🔥 Complex Commands: 'average salary per department', 'employees earning more than 100000 in Hyderabad', 'who is the highest paid worker in AI?'")
    
    user_input = st.text_input("Enter natural language task:", placeholder="Average salary per department")
    generate_btn = st.button("Compile & Execute", type="primary")

with col2:
    st.subheader("Engine Output")
    if generate_btn:
        if not user_input.strip():
            st.warning("Please specify a problem parameter.")
        else:
            with st.spinner("Executing AST tree transformation..."):
                try:
                    compiled_sql = compile_complex_query(user_input)
                    
                    st.markdown("### Generated Complex SQL")
                    st.code(compiled_sql, language="sql")
                    
                    df_results = pd.read_sql_query(compiled_sql, db_conn)
                    st.markdown("### Matrix Evaluation Results")
                    st.dataframe(df_results, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"AST Error: {str(e)}")
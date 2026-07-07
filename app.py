import streamlit as st
import pandas as pd
import sqlite3
import re

# Page Setup
st.set_page_config(page_title="Enterprise AI SQL Agent", layout="wide")
st.title("Enterprise AI SQL Agent ⚡📊")
st.caption("Production-Grade Relational Translation Architecture | Dynamic In-Context Token Compiler")

# 1. Database Infrastructure Initializer
@st.cache_resource
def init_enterprise_db():
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()
    
    # Schema 1: Employees Matrix
    cursor.execute("""
        CREATE TABLE employees (
            emp_id INTEGER PRIMARY KEY,
            name TEXT,
            dept_id INTEGER,
            salary INTEGER,
            hire_date TEXT,
            manager_id INTEGER
        )
    """)
    
    # Schema 2: Departments Context
    cursor.execute("""
        CREATE TABLE departments (
            dept_id INTEGER PRIMARY KEY,
            dept_name TEXT,
            location TEXT,
            budget INTEGER
        )
    """)
    
    # Insert Production Datasets
    cursor.executemany("INSERT INTO departments VALUES (?, ?, ?, ?)", [
        (1, 'AI/ML', 'Tirupati', 500000),
        (2, 'Data Science', 'Hyderabad', 400000),
        (3, 'Full Stack', 'Bangalore', 300000)
    ])
    
    cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", [
        (101, 'Saketh', 1, 145000, '2026-01-15', 104),
        (102, 'Ananya', 2, 125000, '2025-06-20', 105),
        (103, 'Rahul', 3, 98000, '2024-11-02', 101),
        (104, 'Priya', 1, 160000, '2025-03-10', NULL),
        (105, 'Vikram', 2, 110000, '2026-02-01', NULL)
    ])
    conn.commit()
    return conn

db_conn = init_enterprise_db()

# 2. Generative-Style Context Compiler (Abstract Syntax Mapping Engine)
def advanced_generative_compiler(user_query):
    raw = user_query.lower().strip()
    
    # Define Core Pipeline Context (Dynamic In-Context Framework)
    table_schema = {
        "employees": ["emp_id", "name", "dept_id", "salary", "hire_date", "manager_id"],
        "departments": ["dept_id", "dept_name", "location", "budget"]
    }
    
    # Base Components for Compilation
    projection = "e.emp_id, e.name, d.dept_name, e.salary, e.hire_date"
    from_clause = "FROM employees e JOIN departments d ON e.dept_id = d.dept_id"
    where_conditions = []
    group_by = ""
    order_by = ""
    having_clause = ""
    
    # Extract numerical constants for evaluation
    numbers = re.findall(r'\b\d+\b', raw)
    
    # A. Processing Complex Filters & Comparative Subqueries
    if "than average" in raw or "above average" in raw:
        where_conditions.append("e.salary > (SELECT AVG(salary) FROM employees)")
        projection = "e.name, e.salary, d.dept_name"
    elif "than the total budget" in raw:
        where_conditions.append("e.salary > (SELECT SUM(budget) FROM departments)")
        
    # B. Processing Mathematical Multipliers & Projections
    if "double" in raw or "2x" in raw or "increment" in raw:
        projection = "e.name, e.salary AS current_salary, (e.salary * 2) AS projected_salary, d.dept_name"
    
    # C. Dynamic Entity Extraction (Locations & Departments)
    if "hyd" in raw or "hyderabad" in raw:
        where_conditions.append("d.location = 'Hyderabad'")
    elif "tirupati" in raw:
        where_conditions.append("d.location = 'Tirupati'")
    elif "bangalore" in raw or "blr" in raw:
        where_conditions.append("d.location = 'Bangalore'")
        
    if "ai" in raw or "ml" in raw:
        where_conditions.append("d.dept_name = 'AI/ML'")
    elif "data" in raw or "science" in raw:
        where_conditions.append("d.dept_name = 'Data Science'")
    elif "full" in raw or "stack" in raw:
        where_conditions.append("d.dept_name = 'Full Stack'")

    # D. Parameter Handling for Hardcoded Values
    if "salary >" in raw or "salary greater than" in raw:
        if numbers:
            where_conditions.append(f"e.salary > {numbers[0]}")
    elif "salary <" in raw or "salary less than" in raw:
        if numbers:
            where_conditions.append(f"e.salary < {numbers[0]}")

    # E. Advanced Sorting and Nested Analytical Joins
    if "highest" in raw or "max" in raw or "top earning" in raw:
        order_by = "ORDER BY e.salary DESC LIMIT 1"
    elif "lowest" in raw or "min" in raw:
        order_by = "ORDER BY e.salary ASC LIMIT 1"
        
    # F. Structural Aggregations & Having Clause Simulation
    if "average salary per department" in raw or "department wise avg" in raw:
        projection = "d.dept_name, COUNT(e.emp_id) AS total_employees, AVG(e.salary) AS average_salary"
        group_by = "GROUP BY d.dept_name"
        if "more than" in raw and numbers:
            having_clause = f"HAVING AVG(e.salary) > {numbers[0]}"
            
    elif "total department budget" in raw or "department spending" in raw:
        projection = "d.dept_name, d.budget AS operational_budget, SUM(e.salary) AS salary_expense"
        group_by = "GROUP BY d.dept_name, d.budget"

    # Assemble Final Complete Dynamic SQL Compilation Tree
    where_stmt = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
    
    sql_matrix = [
        f"SELECT {projection}",
        from_clause,
        where_stmt,
        group_by,
        having_clause,
        order_by
    ]
    
    final_compiled_sql = " ".join([block for block in sql_matrix if block.strip()]) + ";"
    return final_compiled_sql

# 3. Interactive UI Layout Split
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Enterprise Context Mapping Data")
    st.markdown("""
    ```sql
    -- Schema Architecture Model
    TABLE employees (emp_id PRIMARY KEY, name, dept_id FOREIGN KEY, salary, hire_date, manager_id);
    TABLE departments (dept_id PRIMARY KEY, dept_name, location, budget);
    ```
    """)
    st.caption("🚀 **Try Highly Complex Analytical Prompts:**")
    st.info("""
    * *'Show employees who earn more than average'* (Generates Nested Subquery)
    * *'Calculate the double salary projections for AI teams'* (Calculates Mathematical Transforms)
    * *'Show department wise avg salary'* (Generates Aggregate Grouping Operations)
    """)
    
    user_input = st.text_input("Enter natural language objective:", placeholder="Who earns more than average?")
    compile_btn = st.button("Compile Context & Execute", type="primary")

with col2:
    st.subheader("Relational Agent Pipeline Output")
    if compile_btn:
        if not user_input.strip():
            st.warning("Please define a valid query string.")
        else:
            with st.spinner("Processing token context arrays..."):
                try:
                    generated_sql = advanced_generative_compiler(user_input)
                    
                    st.markdown("### Context-Generated Multi-Table SQL")
                    st.code(generated_sql, language="sql")
                    
                    # Direct data-frame injection execution
                    df_results = pd.read_sql_query(generated_sql, db_conn)
                    st.markdown("### Structural Result Output Matrix")
                    st.dataframe(df_results, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"In-Context Compilation Fault: {str(e)}")
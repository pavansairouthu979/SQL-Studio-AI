import os
import time
import sqlite3
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import pandas as pd

# Load environment variables
load_dotenv()

# Configure Google Generative AI
api_key = os.getenv("API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# ---------------------------------------------------------
# Page Configuration & Custom CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI SQL Studio Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Enterprise UI Theme
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }
    
    /* Header card styling */
    .header-card {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #311042 100%);
        border: 1px solid #3730A3;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
        color: white;
        box-shadow: 0 12px 30px -5px rgba(0, 0, 0, 0.4);
    }
    .header-badge {
        background: linear-gradient(90deg, #6366F1, #EC4899);
        color: white;
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 0.75rem;
    }
    .header-title {
        font-size: 2.3rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(90deg, #FFFFFF, #E0E7FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-subtitle {
        color: #C7D2FE;
        font-size: 1.05rem;
        margin: 0;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #38BDF8;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-top: 0.2rem;
        font-weight: 500;
    }
    
    /* Styled Explainer Container */
    .explainer-card {
        background-color: #1E1B4B;
        border-left: 4px solid #818CF8;
        border-radius: 8px;
        padding: 1.25rem;
        margin-top: 1rem;
        color: #E0E7FF;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 600;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Helper Functions & Database Management
# ---------------------------------------------------------
DB_FILE = "students.db"

def get_database_tables(db_path):
    """Retrieve list of all tables in the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def get_table_schema(db_path, table_name):
    """Retrieve column metadata for a specific table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    return columns

def clean_sql_query(sql_text):
    """Clean markdown formatting or commentary from LLM response."""
    sql = sql_text.strip()
    if sql.startswith("```"):
        lines = sql.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        sql = "\n".join(lines).strip()
    if sql.lower().startswith("sql"):
        sql = sql[3:].strip()
    return sql

def execute_sql_query(sql, db_path):
    """Execute SQL query and return columns and result rows."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description] if cursor.description else []
    conn.commit()
    conn.close()
    return column_names, rows

def get_gemini_sql(question, system_prompt):
    """Generate SQL query from text prompt using Gemini."""
    if not api_key:
        raise ValueError("API_KEY environment variable is not configured.")
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([system_prompt, question])
    return response.text

def get_gemini_explanation(question, sql):
    """Generate plain English breakdown of the SQL query."""
    if not api_key:
        return "API Key missing. Cannot generate explanation."
    prompt = f"""
    You are a database instructor. Explain the following SQL query in simple step-by-step terms for a non-technical user.
    
    User Question: "{question}"
    Generated SQL: "{sql}"
    
    Format output with bullet points:
    - What tables are queried
    - Filtering or conditions applied
    - What output is returned
    Keep explanation concise under 150 words.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# System Prompt definition for multi-table schema
SYSTEM_PROMPT = """
You are an expert in converting English questions into SQLite SQL queries.

The SQLite database contains two tables:

1. Table Name: students
   Columns:
   - id INTEGER PRIMARY KEY
   - name TEXT
   - age INTEGER
   - department TEXT
   - gpa REAL
   - city TEXT

2. Table Name: courses
   Columns:
   - course_id INTEGER PRIMARY KEY
   - course_name TEXT
   - department TEXT
   - credits INTEGER

Instructions:
- Convert the user's question into a valid SQLite SQL query.
- Return ONLY the executable SQL query.
- Do NOT include markdown blocks such as ```sql or explanations.
- Do NOT return any extra text before or after the query.
- You can join 'students' and 'courses' on department when requested.
- For text comparisons, use `COLLATE NOCASE` where appropriate.
  Example: SELECT * FROM students WHERE department = 'Computer Science' COLLATE NOCASE;
"""

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "user_question" not in st.session_state:
    st.session_state.user_question = ""
if "last_sql" not in st.session_state:
    st.session_state.last_sql = ""
if "last_df" not in st.session_state:
    st.session_state.last_df = None
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "explanation_cache" not in st.session_state:
    st.session_state.explanation_cache = ""

def set_question(q):
    st.session_state.user_question = q

# ---------------------------------------------------------
# Sidebar Component
# ---------------------------------------------------------
with st.sidebar:
    st.title("🗄️ Database Explorer")
    st.caption("SQLite Connection: `students.db`")
    
    tables = get_database_tables(DB_FILE)
    selected_table = st.selectbox("Select Table Inspector:", tables if tables else ["students"])
    
    # Table Schema Expander
    if selected_table:
        with st.expander(f"📋 Schema: `{selected_table}`", expanded=True):
            schema_data = get_table_schema(DB_FILE, selected_table)
            schema_df = pd.DataFrame(
                [{"Column": col[1], "Type": col[2], "PK": "Yes" if col[5] else "No"} for col in schema_data]
            )
            st.dataframe(schema_df, use_container_width=True, hide_index=True)
        
        # Live Data Preview
        with st.expander(f"👀 `{selected_table}` Top 5 Rows", expanded=False):
            try:
                cols, rows = execute_sql_query(f"SELECT * FROM {selected_table} LIMIT 5;", DB_FILE)
                st.dataframe(pd.DataFrame(rows, columns=cols), use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Preview error: {e}")
            
    st.markdown("---")
    st.subheader("💡 Advanced Preset Queries")
    st.caption("Click any query below to populate the search bar:")
    
    sample_queries = [
        "Show all students in Computer Science",
        "What is the average GPA by department?",
        "List all courses with 4 credits",
        "Show top 3 students with highest GPA",
        "Show students and courses offered in their department"
    ]
    
    for sq in sample_queries:
        st.button(f"🔍 {sq}", on_click=set_question, args=(sq,), use_container_width=True)
        
    st.markdown("---")
    
    # Query History Drawer
    st.subheader("📜 Session History")
    if st.session_state.query_history:
        for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.container():
                st.markdown(f"**Q:** *{item['question']}*")
                st.code(item['sql'], language="sql")
                st.caption(f"Rows: {item['rows']} | Status: {item['status']}")
                st.markdown("---")
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.session_state.last_df = None
            st.session_state.last_sql = ""
            st.rerun()
    else:
        st.caption("No queries executed yet.")

# ---------------------------------------------------------
# Main App Body & Header
# ---------------------------------------------------------

st.markdown("""
    <div class="header-card">
        <span class="header-badge">Enterprise SQL & Intelligence Suite</span>
        <h1 class="header-title">Natural Language to SQL Studio Pro</h1>
        <p class="header-subtitle">Translate English into SQLite queries, analyze datasets visually, and inspect AI-generated query logic in real time.</p>
    </div>
""", unsafe_allow_html=True)

if not api_key:
    st.error("⚠️ **API Key Missing!** Please ensure `API_KEY` is specified in your `.env` file.")

# Main Input Bar
col_input, col_btn = st.columns([5, 1])
with col_input:
    query_input = st.text_input(
        "Ask a question about students or courses:",
        value=st.session_state.user_question,
        placeholder="e.g. What is the average GPA by department?",
        key="input_field",
        label_visibility="collapsed"
    )
with col_btn:
    execute_clicked = st.button("🚀 Run Query", type="primary", use_container_width=True)

# Trigger Query Execution
if execute_clicked or (query_input and query_input != st.session_state.user_question):
    current_q = query_input if query_input else st.session_state.user_question
    if not current_q:
        st.warning("Please enter a question or choose a sample query from the sidebar.")
    else:
        st.session_state.user_question = current_q
        with st.spinner("🧠 Gemini is generating and executing SQL..."):
            start_time = time.time()
            try:
                raw_sql = get_gemini_sql(current_q, SYSTEM_PROMPT)
                clean_sql = clean_sql_query(raw_sql)
                cols, rows = execute_sql_query(clean_sql, DB_FILE)
                exec_time = round((time.time() - start_time) * 1000, 2)
                
                df_result = pd.DataFrame(rows, columns=cols) if rows else pd.DataFrame(columns=cols)
                st.session_state.last_sql = clean_sql
                st.session_state.last_df = df_result
                st.session_state.last_exec_time = exec_time
                st.session_state.explanation_cache = "" # reset explanation cache for new query
                
                st.session_state.query_history.append({
                    "question": current_q,
                    "sql": clean_sql,
                    "rows": len(rows),
                    "status": "Success"
                })
            except Exception as e:
                st.error(f"❌ **Query Execution Error:** {e}")
                st.session_state.query_history.append({
                    "question": current_q,
                    "sql": "N/A",
                    "rows": 0,
                    "status": "Failed"
                })

# ---------------------------------------------------------
# Multi-Tab Main Interface
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 AI Query Studio", 
    "📊 Visual Analytics", 
    "💡 AI SQL Explainer", 
    "🛠️ Direct SQL Console"
])

# ---------------- Tab 1: AI Query Studio ----------------
with tab1:
    if st.session_state.last_df is not None:
        st.subheader("🛠️ Generated SQL Query")
        st.code(st.session_state.last_sql, language="sql")
        
        # Metric Cards
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("""
                <div class="metric-card">
                    <div class="metric-value" style="color: #34D399;">SUCCESS</div>
                    <div class="metric-label">Execution Status</div>
                </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(st.session_state.last_df)}</div>
                    <div class="metric-label">Rows Returned</div>
                </div>
            """, unsafe_allow_html=True)
        with m3:
            exec_t = getattr(st.session_state, 'last_exec_time', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{exec_t} ms</div>
                    <div class="metric-label">Execution Speed</div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 Query Results")
        
        if not st.session_state.last_df.empty:
            st.dataframe(st.session_state.last_df, use_container_width=True)
            
            # Export to CSV
            csv_bytes = st.session_state.last_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Results to CSV",
                data=csv_bytes,
                file_name="query_results.csv",
                mime="text/csv"
            )
        else:
            st.info("Query executed successfully. 0 matching records found.")
    else:
        st.info("👆 Enter a prompt above or select a preset query from the sidebar to begin!")

# ---------------- Tab 2: Visual Analytics ----------------
with tab2:
    st.subheader("📈 Automatic Visual Data Charts")
    df = st.session_state.last_df
    if df is not None and not df.empty:
        # Filter numeric columns for graphing
        numeric_cols = df.select_dtypes(include=['number', 'float', 'int']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'string', 'category']).columns.tolist()
        
        if numeric_cols:
            c1, c2, c3 = st.columns(3)
            with c1:
                chart_type = st.selectbox("Select Chart Type:", ["Bar Chart", "Line Chart", "Area Chart"])
            with c2:
                x_axis = st.selectbox("X-Axis (Category/Label):", categorical_cols if categorical_cols else df.columns.tolist())
            with c3:
                y_axis = st.selectbox("Y-Axis (Numeric Metric):", numeric_cols)
                
            st.markdown("### Interactive Visualization")
            chart_data = df.set_index(x_axis)[y_axis] if x_axis in df.columns else df[y_axis]
            
            if chart_type == "Bar Chart":
                st.bar_chart(chart_data)
            elif chart_type == "Line Chart":
                st.line_chart(chart_data)
            elif chart_type == "Area Chart":
                st.area_chart(chart_data)
                
            with st.expander("🔢 View Summary Statistics", expanded=False):
                st.dataframe(df.describe(), use_container_width=True)
        else:
            st.warning("The current result dataset has no numeric columns to plot automatically.")
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Run a query in the Query Studio first to render analytical charts.")

# ---------------- Tab 3: AI SQL Explainer ----------------
with tab3:
    st.subheader("💡 Step-by-Step AI Logic Breakdown")
    if st.session_state.last_sql:
        st.code(st.session_state.last_sql, language="sql")
        
        if st.button("✨ Explain SQL Query Step-by-Step", type="secondary"):
            with st.spinner("Analyzing SQL logic..."):
                explanation = get_gemini_explanation(st.session_state.user_question, st.session_state.last_sql)
                st.session_state.explanation_cache = explanation
                
        if st.session_state.explanation_cache:
            st.markdown(f"""
                <div class="explainer-card">
                    <h4>📘 Plain English Explanation</h4>
                    {st.session_state.explanation_cache}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Execute a query to unlock AI step-by-step SQL explanations.")

# ---------------- Tab 4: Direct SQL Console ----------------
with tab4:
    st.subheader("🛠️ Raw SQLite Interactive Console")
    st.caption("Write and execute custom SQL statements directly against `students.db`.")
    
    manual_sql = st.text_area("Enter SQL Command:", value="SELECT department, COUNT(*) as total_students, ROUND(AVG(gpa),2) as avg_gpa FROM students GROUP BY department;", height=120)
    
    if st.button("▶️ Execute Raw SQL", type="primary"):
        with st.spinner("Executing SQL command..."):
            try:
                m_cols, m_rows = execute_sql_query(manual_sql, DB_FILE)
                st.success("SQL Command Executed Successfully!")
                if m_rows:
                    m_df = pd.DataFrame(m_rows, columns=m_cols)
                    st.dataframe(m_df, use_container_width=True)
                else:
                    st.info("Command executed. No rows returned.")
            except Exception as ex:
                st.error(f"❌ SQL Execution Error: {ex}")
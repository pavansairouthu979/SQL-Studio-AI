# ⚡ AI SQL Studio Pro - Natural Language to SQL & Enterprise Analytics

A high-performance Business Intelligence (BI) and SQL Learning platform built with **Streamlit**, **Google Gemini AI**, **Pandas**, and **SQLite**.

Convert plain English questions into executable SQLite queries, inspect live database schemas, visualize datasets automatically with interactive charts, generate AI step-by-step SQL breakdowns, and run raw commands in a direct SQL console.

---

## ✨ Enterprise Features

- 🧠 **Gemini AI Translation**: Powered by `gemini-2.5-flash` to convert complex English prompts into valid multi-table SQLite queries (JOINs, aggregations, filtering).
- 🏛️ **Multi-Table Relational Schema**: Built-in SQLite database featuring related tables (`students` and `courses`) with rich attributes (`gpa`, `department`, `city`, `credits`).
- 🗂️ **4-Tab Enterprise Workspace**:
  1. 🔍 **AI Query Studio**: Enter natural language questions, inspect generated SQL, view formatted result grids, and export to CSV.
  2. 📊 **Visual Analytics**: Interactive Bar, Line, and Area charts generated automatically from query results along with statistical summaries (`describe()`).
  3. 💡 **AI SQL Explainer**: Generates plain-English step-by-step explanations of how generated SQL queries function.
  4. 🛠️ **Direct SQL Console**: Interactive SQLite console for executing custom raw SQL queries directly.
- 🗄️ **Dynamic Multi-Table Schema Inspector**: Switch between tables in the sidebar to inspect column types, primary keys, and top-5 row previews.
- 💡 **Advanced Quick-Query Presets**: Pre-configured sample questions covering aggregations, multi-table JOINs, and filtering.
- 📜 **Session Query Drawer**: Tracks active query history, execution speed (ms), row count, and query status.
- 🎨 **Enterprise UI Theme**: Gradient header, glassmorphic metric badges, custom tab design, and dark theme styling.

---

## 🛠️ Technology Stack

- **Frontend / UI**: [Streamlit](https://streamlit.io/)
- **LLM Engine**: [Google Generative AI SDK](https://pypi.org/project/google-generativeai/) (`gemini-2.5-flash`)
- **Database**: SQLite3
- **Data Analytics & Charts**: [Pandas](https://pandas.pydata.org/)
- **Environment**: `python-dotenv`
- **Deployment Service**: [Render](https://render.com/) (via `render.yaml`)

---

## 📁 Project Structure

```
sqlproject/
├── app.py              # Main multi-tab Streamlit application
├── sql.py              # Multi-table database creation & seeding script
├── students.db         # Relational SQLite database file
├── requirements.txt    # Required Python dependencies
├── .env                # API Key configuration file
├── render.yaml         # Render deployment configuration blueprint
└── README.md           # Enterprise project documentation
```

---

## 🚀 Quick Start Guide (Local)

### 1. Prerequisites
- **Python 3.9+**
- A **Google Gemini API Key**

### 2. Setup Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
In `.env`:
```env
API_KEY="YOUR_GEMINI_API_KEY_HERE"
```

### 5. Populate Multi-Table Database
Run `sql.py` to create and seed `students` and `courses` tables:
```bash
python sql.py
```

### 6. Launch Application
```bash
streamlit run app.py
```

Access the live app at `http://localhost:8501`.

---

## 🌐 Server Deployment Guide

### Option 1: Deploy on Render (Recommended Service)

#### Method A: Automatic Deployment (using `render.yaml`)
1. Push your repository to **GitHub**.
2. Log into [Render](https://render.com/).
3. Click **New +** -> **Blueprint**.
4. Connect your GitHub repository. Render will automatically read `render.yaml` and configure your build command, start command, and port.
5. Set your `API_KEY` under Environment Variables and click **Apply**.

#### Method B: Manual Deployment
1. Push project to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
3. Connect your repository and set the configuration:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python sql.py`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
4. Add Environment Variable:
   - Key: `API_KEY` | Value: `YOUR_GEMINI_API_KEY`
5. Click **Deploy Web Service**.

---

### Option 2: Streamlit Community Cloud (Free Alternative)
1. Push your project to a **GitHub Repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New App"** and select your repository, branch (`main`), and main file path (`app.py`).
4. Under **Advanced Settings** -> **Secrets**, add your API key:
   ```toml
   API_KEY = "YOUR_GEMINI_API_KEY"
   ```
5. Click **Deploy!** Your app will be live on a public URL (`https://your-app.streamlit.app`).

---

## 📄 License
MIT License. Open for educational and commercial use.

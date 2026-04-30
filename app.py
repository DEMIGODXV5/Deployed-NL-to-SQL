import streamlit as st
import sqlite3
import json
import os
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NL → SQL | E-Commerce Intelligence",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #7c6afa, #4fc3f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.subtitle {
    font-size: 0.95rem;
    color: #7070a0;
    margin-bottom: 2rem;
}

.sql-box {
    background: #12121f;
    border: 1px solid #2a2a4a;
    border-left: 3px solid #7c6afa;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
    color: #a0d8ff;
    white-space: pre-wrap;
    word-break: break-word;
    margin-bottom: 1rem;
}

.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    font-family: 'Space Mono', monospace;
}

.badge-success { background: #1a3a2a; color: #4caf87; border: 1px solid #2a5a3a; }
.badge-clarify { background: #3a2a10; color: #f4a533; border: 1px solid #5a3a10; }
.badge-error   { background: #3a1a1a; color: #f45353; border: 1px solid #5a2a2a; }

.info-card {
    background: #12121f;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
}

.schema-header {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: #7c6afa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}

.schema-col {
    font-size: 0.8rem;
    color: #9090b8;
    line-height: 1.6;
}

/* Input styling */
.stTextInput > div > div > input {
    background: #12121f !important;
    border: 1px solid #2a2a4a !important;
    border-radius: 8px !important;
    color: #e8e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #7c6afa !important;
    box-shadow: 0 0 0 2px rgba(124,106,250,0.2) !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #7c6afa, #4fc3f7) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 2rem !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s !important;
}

.stButton > button:hover {
    opacity: 0.85 !important;
}

/* Dataframe */
.stDataFrame { border-radius: 8px; overflow: hidden; }

/* Divider */
hr { border-color: #1e1e3a !important; }

/* Spinner */
.stSpinner > div { border-top-color: #7c6afa !important; }

/* Metric */
[data-testid="stMetric"] {
    background: #12121f;
    border: 1px solid #1e1e3a;
    border-radius: 10px;
    padding: 0.8rem 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🗄️ NL → SQL Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask questions about the e-commerce database in plain English — get SQL & results instantly.</div>', unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DB_NAME = "ecommerce.db"

MOCKAROO_URLS = {
    "customers": "https://api.mockaroo.com/api/dde01370?count=1000&key=11149690",
    "products":  "https://api.mockaroo.com/api/8ba6f630?count=1000&key=11149690",
    "orders":    "https://api.mockaroo.com/api/6fa67fe0?count=3000&key=11149690",
}

CUSTOMERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50), last_name VARCHAR(50),
    email VARCHAR(50), phone_number VARCHAR(50),
    address VARCHAR(50), city VARCHAR(50),
    country VARCHAR(50), postal_code VARCHAR(50),
    loyalty_points INT
);"""

PRODUCTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    product_id INT PRIMARY KEY,
    product_name TEXT, description TEXT,
    price DECIMAL(10,2), discount_percentage DECIMAL(5,2),
    category VARCHAR(50), brand TEXT,
    stock_quantity INT, color VARCHAR(50),
    size VARCHAR(20), weight DECIMAL(5,2),
    dimensions TEXT, release_date DATE,
    rating DECIMAL(3,1), reviews_count INT,
    seller_name TEXT, seller_rating DECIMAL(3,1),
    seller_reviews_count INT, shipping_method VARCHAR(20),
    shipping_cost DECIMAL(6,2)
);"""

ORDERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY,
    customer_id INT, product_id INT,
    quantity INT, unit_price DECIMAL(10,2),
    total_price DECIMAL(10,2), order_date DATE,
    shipping_address VARCHAR(255), payment_method VARCHAR(20),
    status VARCHAR(20),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);"""

SYSTEM_PROMPT = """
### ROLE

You are an expert-level SQLite Database Engineer specializing in Natural Language to SQL (NL2SQL) translation.

Your job is to convert natural language English queries into accurate, optimized SQLite queries for an e-commerce business intelligence dashboard used by non-technical users.

You must carefully understand user intent and generate SQL queries strictly based on the provided schema.

------------------------------------------------------------

### DATABASE SCHEMA

The database contains the following tables:

------------------------------------------------------------

TABLE: customers

Columns:
- customer_id (INTEGER PRIMARY KEY)
- first_name (TEXT)
- last_name (TEXT)
- email (TEXT)
- phone_number (TEXT)
- address (TEXT)
- city (TEXT)
- country (TEXT)
- postal_code (TEXT)
- loyalty_points (INTEGER)

------------------------------------------------------------

TABLE: products

Columns:
- product_id (INTEGER PRIMARY KEY)
- product_name (TEXT)
- description (TEXT)
- price (REAL)
- discount_percentage (REAL)
- category (TEXT)
- brand (TEXT)
- stock_quantity (INTEGER)
- color (TEXT)
- size (TEXT)
- weight (REAL)
- dimensions (TEXT)
- release_date (DATE)
- rating (REAL)
- reviews_count (INTEGER)
- seller_name (TEXT)
- seller_rating (REAL)
- seller_reviews_count (INTEGER)
- shipping_method (TEXT)
- shipping_cost (REAL)

------------------------------------------------------------

TABLE: orders

Columns:
- order_id (INTEGER PRIMARY KEY)
- customer_id (INTEGER)
- product_id (INTEGER)
- quantity (INTEGER)
- unit_price (REAL)
- total_price (REAL)
- order_date (DATE)
- shipping_address (TEXT)
- payment_method (TEXT)
- status (TEXT)

------------------------------------------------------------

### TABLE RELATIONSHIPS

customers.customer_id → orders.customer_id
products.product_id → orders.product_id

------------------------------------------------------------

### PRIMARY TASK

Convert the user's natural language query into a valid SQLite query.
Understand what the user is asking.
Identify relevant tables.
Identify required joins.
Generate optimized SQL query.

------------------------------------------------------------

### QUERY RULES

Generate ONLY SELECT queries.

NEVER generate:
- INSERT
- UPDATE
- DELETE
- DROP
- ALTER
- TRUNCATE

Use only tables listed above.
Use only columns listed above.
Never invent tables, columns, or relationships.
Use proper JOIN statements when multiple tables are needed.

------------------------------------------------------------

### BUSINESS LOGIC RULES

Active orders = status = 'active'
Completed orders = status = 'completed'
Cancelled orders = status = 'cancelled'

For "top N" queries always include ORDER BY + LIMIT N.
For revenue queries use SUM(total_price).
For sales volume use SUM(quantity).
For customer ranking use GROUP BY customer_id.

If user asks "this month":
strftime('%Y-%m', order_date) = strftime('%Y-%m', 'now')

If user asks "this year":
strftime('%Y', order_date) = strftime('%Y', 'now')

------------------------------------------------------------

### AMBIGUITY HANDLING

If the user query is unclear, incomplete, or ambiguous:
Return clarification request.

Examples of ambiguous requests:
- Show best customers
- Show top products
- Show recent orders
- Show high-performing sellers

Ask follow-up question when needed.

------------------------------------------------------------

### ERROR HANDLING

Return an error response if:
- User asks for unavailable tables
- User asks for unavailable columns
- User asks for unsupported metrics
- Query cannot be generated

------------------------------------------------------------

### OUTPUT FORMAT

Your final response must be a single valid JSON object with the following keys:

1. "status" — one of: "success", "clarification_needed", "error"

2. "response"
   - If success: return complete SQLite query string
   - If clarification_needed: return follow-up question
   - If error: return reason query could not be generated

------------------------------------------------------------

### RESPONSE RULES

- Return valid JSON only
- Return only one JSON object
- No markdown
- No code blocks
- No explanations
- No comments
- No extra keys

------------------------------------------------------------

### EXAMPLES

Example 1
User: Show top 5 customers by total spending
Response:
{"status": "success", "response": "SELECT c.first_name, c.last_name, SUM(o.total_price) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id ORDER BY total_spent DESC LIMIT 5;"}

Example 2
User: Show best customers
Response:
{"status": "clarification_needed", "response": "Do you want best customers based on total spending, total orders, or loyalty points?"}

Example 3
User: Show employee salaries
Response:
{"status": "error", "response": "The requested data does not exist in the current database schema."}

------------------------------------------------------------

IMPORTANT FINAL INSTRUCTION

Generate accurate SQLite queries strictly based on the provided schema.
Never hallucinate columns/tables.
Always return valid JSON output.
"""

# ── DB Setup ──────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def setup_database():
    """Download data from Mockaroo and create SQLite DB. Cached so it only runs once."""
    if os.path.exists(DB_NAME):
        return True, "Database loaded from disk."

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(CUSTOMERS_SCHEMA)
        cursor.execute(PRODUCTS_SCHEMA)
        cursor.execute(ORDERS_SCHEMA)

        for table, url in MOCKAROO_URLS.items():
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            df = pd.read_csv(StringIO(resp.text))
            df.to_sql(table, conn, if_exists="append", index=False)

        conn.commit()
        conn.close()
        return True, "Database created successfully."
    except Exception as e:
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        return False, str(e)


# ── Gemini client ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_genai_client(api_key):
    from google import genai
    return genai.Client(api_key=api_key)


# ── Core functions ────────────────────────────────────────────────────────────
def get_sql_query(client, user_query):
    contents = f"{SYSTEM_PROMPT}\n\nHere is the user query you need to convert:\n{user_query}"
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=contents
    )
    raw = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def execute_query(query):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_db_stats():
    conn = sqlite3.connect(DB_NAME)
    stats = {}
    for table in ["customers", "products", "orders"]:
        count = pd.read_sql_query(f"SELECT COUNT(*) as n FROM {table}", conn).iloc[0]["n"]
        stats[table] = count
    conn.close()
    return stats


# ── Sidebar: Schema reference ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 Schema Reference")
    st.markdown('<div class="info-card"><div class="schema-header">customers</div><div class="schema-col">customer_id · first_name · last_name<br>email · phone_number · address<br>city · country · postal_code · loyalty_points</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><div class="schema-header">products</div><div class="schema-col">product_id · product_name · description<br>price · discount_percentage · category<br>brand · stock_quantity · color · size<br>weight · dimensions · release_date<br>rating · reviews_count · seller_name<br>seller_rating · shipping_method · shipping_cost</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="info-card"><div class="schema-header">orders</div><div class="schema-col">order_id · customer_id · product_id<br>quantity · unit_price · total_price<br>order_date · shipping_address<br>payment_method · status</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💡 Sample Questions")
    samples = [
        "Top 5 customers by total spending",
        "Average price of products per category",
        "Order count by country",
        "Most popular products by sales quantity",
        "Which country has the least sales?",
        "Monthly revenue this year",
        "Products with highest ratings",
    ]
    for s in samples:
        st.markdown(f"<span style='font-size:0.82rem; color:#7070a0;'>→ {s}</span>", unsafe_allow_html=True)


# ── API Key input ─────────────────────────────────────────────────────────────
api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.markdown("#### 🔑 Enter your Gemini API Key")
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get your key from https://aistudio.google.com/app/apikey"
    )
    if not api_key:
        st.info("Enter your Gemini API key above to get started.")
        st.stop()


# ── Init DB ───────────────────────────────────────────────────────────────────
with st.spinner("⚙️ Setting up database (first run may take ~30s)..."):
    ok, msg = setup_database()

if not ok:
    st.error(f"❌ Database setup failed: {msg}")
    st.stop()

# DB stats row
try:
    stats = get_db_stats()
    c1, c2, c3 = st.columns(3)
    c1.metric("👥 Customers", f"{stats['customers']:,}")
    c2.metric("📦 Products",  f"{stats['products']:,}")
    c3.metric("🛒 Orders",    f"{stats['orders']:,}")
except:
    pass

st.markdown("---")

# ── Gemini client init ────────────────────────────────────────────────────────
try:
    client = get_genai_client(api_key)
except Exception as e:
    st.error(f"❌ Could not initialise Gemini client: {e}")
    st.stop()


# ── Query input ───────────────────────────────────────────────────────────────
st.markdown("#### 💬 Ask a question about your data")

col_input, col_btn = st.columns([5, 1])
with col_input:
    user_query = st.text_input(
        "Query",
        label_visibility="collapsed",
        placeholder='e.g. "Show top 5 customers by total spending"'
    )
with col_btn:
    run = st.button("▶ Run", type="primary", use_container_width=True)

# ── Query execution ───────────────────────────────────────────────────────────
if run and user_query.strip():
    with st.spinner("🤖 Generating SQL..."):
        try:
            result = get_sql_query(client, user_query)
        except Exception as e:
            st.error(f"❌ Gemini API error: {e}")
            st.stop()

    status = result.get("status", "error")
    response = result.get("response", "")

    if status == "success":
        st.markdown('<span class="status-badge badge-success">✓ SQL Generated</span>', unsafe_allow_html=True)
        st.markdown(f'<div class="sql-box">{response}</div>', unsafe_allow_html=True)

        with st.spinner("🔍 Running query..."):
            try:
                df = execute_query(response)
            except Exception as e:
                st.error(f"❌ SQL execution error: {e}")
                st.stop()

        if df.empty:
            st.warning("⚠️ Query ran successfully but returned no rows.")
        else:
            st.markdown(f"**{len(df):,} rows returned**")
            st.dataframe(df, use_container_width=True, height=300)

            numeric_cols = df.select_dtypes(include="number").columns.tolist()
            text_cols    = df.select_dtypes(exclude="number").columns.tolist()

            # ── 📈 Descriptive Statistics ──────────────────────────────────
            if numeric_cols:
                st.markdown("---")
                st.markdown("#### 📈 Descriptive Statistics")
                stats_df = df[numeric_cols].agg(["mean", "median", "min", "max", "std"]).T
                stats_df.columns = ["Mean", "Median", "Min", "Max", "Std Dev"]
                stats_df = stats_df.map(lambda x: f"{x:,.2f}")

                # Show as styled metric cards
                for col_name, row in stats_df.iterrows():
                    st.markdown(f"<div style='font-family:Space Mono,monospace;font-size:0.78rem;color:#7c6afa;margin-bottom:0.3rem;'>▸ {col_name}</div>", unsafe_allow_html=True)
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("Mean",    row["Mean"])
                    m2.metric("Median",  row["Median"])
                    m3.metric("Min",     row["Min"])
                    m4.metric("Max",     row["Max"])
                    m5.metric("Std Dev", row["Std Dev"])

            # ── 📊 Visualizations ──────────────────────────────────────────
            if numeric_cols:
                st.markdown("---")
                st.markdown("#### 📊 Visualizations")

                CHART_THEME = dict(
                    plot_bgcolor="#0a0a0f",
                    paper_bgcolor="#0a0a0f",
                    font_color="#e8e8f0",
                    margin=dict(t=50, b=40, l=40, r=20),
                )

                if text_cols and numeric_cols:
                    x_col = text_cols[0]
                    y_col = numeric_cols[0]
                    agg = df.groupby(x_col)[y_col].sum().reset_index()
                    agg = agg.sort_values(by=y_col, ascending=False).head(15)

                    tab1, tab2, tab3 = st.tabs(["📊 Bar Chart", "🥧 Pie Chart", "📉 Line Chart"])

                    with tab1:
                        fig = px.bar(
                            agg, x=x_col, y=y_col,
                            title=f"Bar: {user_query}",
                            color=y_col,
                            color_continuous_scale="Purples",
                            template="plotly_dark"
                        )
                        fig.update_layout(**CHART_THEME, coloraxis_showscale=False)
                        fig.update_traces(marker_line_width=0)
                        st.plotly_chart(fig, use_container_width=True)

                    with tab2:
                        fig2 = px.pie(
                            agg, names=x_col, values=y_col,
                            title=f"Distribution: {user_query}",
                            template="plotly_dark",
                            color_discrete_sequence=px.colors.sequential.Purples_r
                        )
                        fig2.update_layout(**CHART_THEME)
                        st.plotly_chart(fig2, use_container_width=True)

                    with tab3:
                        fig3 = px.line(
                            agg, x=x_col, y=y_col,
                            title=f"Trend: {user_query}",
                            template="plotly_dark",
                            markers=True
                        )
                        fig3.update_layout(**CHART_THEME)
                        fig3.update_traces(line_color="#7c6afa", marker_color="#4fc3f7")
                        st.plotly_chart(fig3, use_container_width=True)

                elif len(numeric_cols) >= 2:
                    tab1, tab2 = st.tabs(["🔵 Scatter Plot", "📊 Bar Chart"])
                    with tab1:
                        fig = px.scatter(
                            df, x=numeric_cols[0], y=numeric_cols[1],
                            title=f"Scatter: {numeric_cols[0]} vs {numeric_cols[1]}",
                            template="plotly_dark"
                        )
                        fig.update_layout(**CHART_THEME)
                        fig.update_traces(marker_color="#7c6afa")
                        st.plotly_chart(fig, use_container_width=True)
                    with tab2:
                        fig2 = px.bar(
                            df.head(15), x=numeric_cols[0], y=numeric_cols[1],
                            title=f"Bar: {numeric_cols[0]} vs {numeric_cols[1]}",
                            template="plotly_dark",
                            color=numeric_cols[1],
                            color_continuous_scale="Purples"
                        )
                        fig2.update_layout(**CHART_THEME, coloraxis_showscale=False)
                        st.plotly_chart(fig2, use_container_width=True)

            # ── 🔍 Outlier Detection (IQR method) ─────────────────────────
            if numeric_cols:
                st.markdown("---")
                st.markdown("#### 🔍 Outlier Detection")
                st.caption("Using IQR method (values below Q1−1.5×IQR or above Q3+1.5×IQR)")

                outlier_found = False
                for col in numeric_cols:
                    Q1  = df[col].quantile(0.25)
                    Q3  = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                    outliers = df[(df[col] < lower) | (df[col] > upper)]

                    if not outliers.empty:
                        outlier_found = True
                        st.markdown(f"<div style='font-family:Space Mono,monospace;font-size:0.78rem;color:#f4a533;'>⚠ Column: <b>{col}</b> — {len(outliers)} outlier(s) found</div>", unsafe_allow_html=True)
                        oc1, oc2, oc3 = st.columns(3)
                        oc1.metric("Lower Bound", f"{lower:,.2f}")
                        oc2.metric("Upper Bound", f"{upper:,.2f}")
                        oc3.metric("Outlier Rows", len(outliers))

                        # Box plot for this column
                        fig_box = px.box(
                            df, y=col,
                            title=f"Box Plot: {col}",
                            template="plotly_dark",
                            points="outliers",
                            color_discrete_sequence=["#7c6afa"]
                        )
                        fig_box.update_layout(
                            plot_bgcolor="#0a0a0f",
                            paper_bgcolor="#0a0a0f",
                            font_color="#e8e8f0",
                            margin=dict(t=40, b=30, l=30, r=20),
                            height=300
                        )
                        st.plotly_chart(fig_box, use_container_width=True)

                        with st.expander(f"View {len(outliers)} outlier row(s) for '{col}'"):
                            st.dataframe(outliers, use_container_width=True)

                if not outlier_found:
                    st.success("✅ No outliers detected in numeric columns.")

    elif status == "clarification_needed":
        st.markdown('<span class="status-badge badge-clarify">⚠ Clarification Needed</span>', unsafe_allow_html=True)
        st.warning(f"🤔 {response}")

    else:
        st.markdown('<span class="status-badge badge-error">✗ Error</span>', unsafe_allow_html=True)
        st.error(f"❌ {response}")

elif run and not user_query.strip():
    st.warning("Please enter a question first.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#3a3a6a; font-size:0.78rem; font-family: Space Mono, monospace;'>"
    "NL→SQL · Powered by Gemini 2.5 Flash Lite · SQLite Backend"
    "</div>",
    unsafe_allow_html=True
)

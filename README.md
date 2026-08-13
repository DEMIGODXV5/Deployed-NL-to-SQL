# 🗄️QueryMin -  Natural Language to SQL — E-Commerce Intelligence Dashboard
TRY - https://querymind-nl-to-sql.streamlit.app/

A Streamlit web app that lets you query an e-commerce database using plain English. Powered by **Google Gemini 2.5 Flash Lite**, it converts your question into a SQL query, runs it, and shows you results with descriptive statistics, charts, and outlier detection — no SQL knowledge needed.

---

## 🚀 Features

- 💬 **Natural Language Input** — Ask questions like *"Top 5 customers by total spending"*
- 🤖 **AI-Powered SQL Generation** — Gemini converts your English to SQLite automatically
- 📊 **Auto Visualizations** — Bar, Pie, and Line charts generated from query results
- 📈 **Descriptive Statistics** — Mean, Median, Min, Max, Std Dev for every numeric column
- 🔍 **Outlier Detection** — IQR-based outlier detection with box plots
- 🗃️ **SQLite Backend** — 3-table e-commerce schema (customers, products, orders)
- 🎨 **Dark UI** — Clean, modern dark-themed interface

---

## 🗂️ Database Schema

The app uses a SQLite database with 3 tables auto-populated from Mockaroo:

**customers** — customer_id, first_name, last_name, email, phone_number, address, city, country, postal_code, loyalty_points

**products** — product_id, product_name, description, price, discount_percentage, category, brand, stock_quantity, color, size, weight, dimensions, release_date, rating, reviews_count, seller_name, seller_rating, shipping_method, shipping_cost

**orders** — order_id, customer_id, product_id, quantity, unit_price, total_price, order_date, shipping_address, payment_method, status

---

## 💡 Sample Questions to Try

- Show top 5 customers by total spending
- Average price of products per category
- Order count by country descending
- Most popular products by sales quantity
- Which country has the least sales?
- Monthly revenue this year
- Products with highest ratings
- Average number of orders per day per country

---

## 🛠️ Run Locally

### Prerequisites
- Python 3.9 or above
- A Gemini API key → get one free at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Steps

**1. Clone or download this repository**
```bash
git clone https://github.com/your-username/nl2sql-app.git
cd nl2sql-app
```

**2. Create a virtual environment**
```bash
python -m venv venv
```

**3. Activate the virtual environment**

Windows:
```bash
venv\Scripts\activate
```

Mac/Linux:
```bash
source venv/bin/activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Run the app**
```bash
streamlit run app.py
```

**6. Open your browser**

The app opens automatically at `http://localhost:8501`

Enter your Gemini API key in the input box on the page and you're good to go!

> **Note:** The first run downloads data from Mockaroo and builds the database (~30 seconds). Every run after that is instant.

---

## ☁️ Deploy on Streamlit Cloud (Free Hosting)

**1.** Push your code to a public GitHub repository (upload `app.py` and `requirements.txt`)

**2.** Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub

**3.** Click **"New app"** → select your repository → set main file as `app.py`

**4.** Click **"Advanced settings"** → **"Secrets"** → add:
```
GEMINI_API_KEY = "your_gemini_api_key_here"
```

**5.** Click **"Deploy"** — your app will be live at a public URL in ~2 minutes!

---

## 📦 Requirements

```
streamlit
pandas
google-genai
plotly
requests
```

---

## 🔑 API Key

This app uses the **Google Gemini API** (free tier available).

1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click **"Create API Key"**
3. Copy and paste it into the app

---

## ⚠️ Important Notes

- The app only generates **SELECT** queries — no data is ever modified
- Never commit your API key to GitHub — use Streamlit Secrets for deployment
- The `ecommerce.db` file is auto-generated on first run and does not need to be uploaded

---

## 🧑‍💻 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI Model | Google Gemini 2.5 Flash Lite |
| Database | SQLite |
| Data Source | Mockaroo (mock e-commerce data) |
| Charts | Plotly Express |
| Data Processing | Pandas |

---

## 📄 License

This project is for educational purposes.

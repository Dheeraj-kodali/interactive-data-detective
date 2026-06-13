---
title: Data Detective
emoji: 🕵️‍♂️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.30.0
app_file: app.py
pinned: false
---

# 🕵️‍♂️ Data Detective: Interactive Data Science & Investigation Engine

Data Detective is a feature-rich, premium Streamlit application designed for rapid exploratory data analysis (EDA), anomaly auditing, segment discovery, and conversational querying of tabular datasets. 

Designed with a sleek, dark slate design system, the application converts raw CSV and Excel data files into high-impact visual findings and insights.

---

## 🚀 Key Modules & Features

### 1. 🧬 Dataset DNA Profile
- Evaluates dataset structural quality, complexity, clusterability, and stability.
- Generates an overall quality rating and detailed analysis metrics.

### 2. 📈 Executive Dashboard
- Summarizes findings, metrics, and case milestones in a premium layout.
- Provides one-click PDF Report Downloads compiled on-the-fly.

### 3. 🗺️ Semantic Data Map
- Projects high-dimensional datasets into an interactive 2D coordinate space using UMAP (Uniform Manifold Approximation and Projection).
- Supports lasso/box selections for isolated row-level audits.

### 4. ⏳ Timeline Intelligence
- Automatically detects date columns and performs decomposed time-series analysis.
- Extracts underlying trends, seasonal periodicities, structural change points, temporal anomalies, and multi-period forecasts.

### 5. 🔍 Segment Discovery
- Groups records into natural cohorts using K-Means or DBSCAN clustering.
- Displays segment population sizes and z-score based distinguishing traits.

### 6. ⚠️ Anomaly Detection
- Leverages Isolation Forest models to flag and score multi-dimensional outliers.
- Features an Anomaly Inspector tool to explain individual row deviances.

### 7. 🔗 Correlation Discovery
- Analyzes relationships between variables using linear Pearson coefficients, rank-based Spearman scores, and binned Mutual Information values.

### 8. 🕵️ Investigation Console
- A conversational natural language querying interface.
- Translates descriptive requests (e.g. average calculation, trend, anomalies, or segments) into interactive charts, statistics, and tables.
- Includes dynamic suggestions matched directly to active dataset columns that execute instantly.

---

## 💻 Local Installation

Ensure you have **Python 3.8+** installed.

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/data-detective.git
   cd data-detective
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Application:**
   ```bash
   streamlit run app.py
   ```

---

## ☁️ Hugging Face Spaces Deployment

This repository is pre-configured for deployment on **Hugging Face Spaces** as a Streamlit app. 

### Steps to Deploy:
1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/spaces).
2. Select **Streamlit** as the SDK.
3. Push this repository's contents to the Space's Git remote or drag-and-drop the files directly.
4. The space will automatically install dependencies from `requirements.txt` and start the app from `app.py`.

---

## 📷 Screenshots (Placeholders)

*Below are placeholders for visual documentation:*

#### 🕵️ Investigation Console NLP Interface
`[Insert Screenshot of NLP chat results with suggestion buttons]`

#### 🗺️ UMAP Projection & Data Mapping
`[Insert Screenshot of 2D scatter plot projection]`

#### ⏳ Time-series Forecast & Seasonality Analysis
`[Insert Screenshot of decomposed timeline metrics]`

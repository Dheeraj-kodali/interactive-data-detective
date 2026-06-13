import pandas as pd
import numpy as np
import streamlit as st
import io
import logging
from utils.timeline_tracker import record_timeline_event, reset_timeline

# Set up logging for ingestion
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def deduplicate_columns(df: pd.DataFrame, source: str = "Unknown") -> pd.DataFrame:
    """
    Checks for duplicate columns. If found, logs a warning and renames them with suffixes (e.g., age, age_2).
    """
    if df.columns.is_unique:
        return df
        
    cols = pd.Series(df.columns)
    duplicates = cols[cols.duplicated()].unique()
    
    logger.warning(f"DUPLICATE COLUMNS DETECTED [{source}]: Expected unique column names, got duplicates: {list(duplicates)}")
    
    for dup in duplicates:
        # Find all indices of the duplicate
        dup_indices = cols[cols == dup].index.values.tolist()
        # Keep the first one as is, suffix the rest
        for count, idx in enumerate(dup_indices):
            if count != 0:
                cols[idx] = f"{dup}_{count + 1}"
                
    df.columns = cols
    logger.info(f"Resolved duplicate columns to: {df.columns.tolist()}")
    return df


@st.cache_data(show_spinner="Analyzing file content...")
def load_data_file(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    Load a dataset from file bytes. Caches the resulting DataFrame based on file content and name.
    Supports CSV and Excel files.
    """
    file_lower = file_name.lower()
    
    # Wrap bytes in BytesIO so pandas can read it
    file_io = io.BytesIO(file_bytes)
    
    if file_lower.endswith('.csv'):
        # Try reading with common encodings if default fails
        encodings = ['utf-8', 'latin1', 'cp1252', 'utf-16']
        for encoding in encodings:
            try:
                # Seek to start
                file_io.seek(0)
                df = pd.read_csv(file_io, encoding=encoding)
                
                # Sanitize duplicate columns immediately upon ingest
                df = deduplicate_columns(df, source="CSV Upload")
                
                reset_timeline()
                record_timeline_event("Dataset Loaded", f"({len(df):,} rows)")
                record_timeline_event("Data Quality Checked", f"({df.isna().sum().sum():,} nulls)")
                return df
            except Exception:
                continue
        # Fallback to raising exception
        raise ValueError("Failed to decode CSV file. Please verify encoding.")
        
    elif file_lower.endswith(('.xlsx', '.xls')):
        try:
            # Load the Excel workbook
            # If there are multiple sheets, we load the first sheet by default.
            df = pd.read_excel(file_io)
            
            # Sanitize duplicate columns immediately upon ingest
            df = deduplicate_columns(df, source="Excel Upload")
            
            reset_timeline()
            record_timeline_event("Dataset Loaded", f"({len(df):,} rows)")
            record_timeline_event("Data Quality Checked", f"({df.isna().sum().sum():,} nulls)")
            return df
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
            
    else:
        raise ValueError("Unsupported file format. Please upload a CSV or Excel (.xlsx/.xls) file.")

@st.cache_data
def get_sample_dataset() -> pd.DataFrame:
    """
    Generates a realistic, professional synthetic dataset of E-commerce Sales & Analytics
    to demonstrate Data Detective's features without requiring user files.
    Contains datetime, numeric, categorical data, and simulated missing values.
    """
    np.random.seed(42)
    n_rows = 1200
    
    # Generate dates over a year
    dates = pd.date_range(start="2025-01-01", periods=n_rows, freq="h")
    
    # Categories and products
    categories = ["Electronics", "Office Supplies", "Furniture", "Apparel"]
    category_choices = np.random.choice(categories, size=n_rows, p=[0.3, 0.4, 0.15, 0.15])
    
    products_map = {
        "Electronics": ["Smartphone", "Wireless Earbuds", "Smart Watch", "Laptop Stand"],
        "Office Supplies": ["Gel Pens (Pack)", "Ergonomic Stapler", "Sticky Notes", "File Organizer"],
        "Furniture": ["Ergonomic Chair", "Standing Desk", "Desk Lamp", "Monitor Mount"],
        "Apparel": ["Hoodie", "Athletic Socks", "Running Shoes", "Baseball Cap"]
    }
    
    products = [np.random.choice(products_map[cat]) for cat in category_choices]
    
    # Numeric variables
    base_prices = {
        "Electronics": 150.0,
        "Office Supplies": 15.0,
        "Furniture": 250.0,
        "Apparel": 45.0
    }
    
    prices = []
    quantities = []
    for cat in category_choices:
        base = base_prices[cat]
        price = np.round(base * np.random.uniform(0.8, 1.5), 2)
        qty = np.random.randint(1, 6)
        prices.append(price)
        quantities.append(qty)
        
    prices = np.array(prices)
    quantities = np.array(quantities)
    sales = np.round(prices * quantities, 2)
    
    # Profit (simulated with some variance, sometimes negative)
    profit_margin = np.random.normal(loc=0.25, scale=0.15, size=n_rows)
    profit = np.round(sales * profit_margin, 2)
    
    # Demographics / logistics
    regions = ["North America", "Europe", "Asia-Pacific", "Latin America"]
    region_choices = np.random.choice(regions, size=n_rows, p=[0.4, 0.3, 0.2, 0.1])
    
    customer_types = ["Corporate", "Consumer", "Home Office"]
    customer_choices = np.random.choice(customer_types, size=n_rows, p=[0.5, 0.3, 0.2])
    
    payment_methods = ["Credit Card", "PayPal", "Bank Transfer", "Crypto"]
    payment_choices = np.random.choice(payment_methods, size=n_rows, p=[0.6, 0.2, 0.15, 0.05])
    
    # Satisfaction Score (1 to 5)
    satisfaction = np.random.choice([1, 2, 3, 4, 5], size=n_rows, p=[0.05, 0.08, 0.17, 0.35, 0.35])
    
    df = pd.DataFrame({
        "Order_Date": dates[:n_rows],
        "Category": category_choices,
        "Product": products,
        "Price_USD": prices,
        "Quantity": quantities,
        "Total_Sales_USD": sales,
        "Profit_USD": profit,
        "Region": region_choices,
        "Customer_Segment": customer_choices,
        "Payment_Method": payment_choices,
        "Satisfaction_Score": satisfaction
    })
    
    # Inject missing values for exploration testing (around 3% of fields)
    cols_to_nan = ["Price_USD", "Region", "Satisfaction_Score", "Profit_USD"]
    for col in cols_to_nan:
        nan_indices = np.random.choice(df.index, size=int(n_rows * 0.035), replace=False)
        df.loc[nan_indices, col] = np.nan
        
    df = deduplicate_columns(df, source="Sample Dataset Generation")
        
    reset_timeline()
    record_timeline_event("Dataset Loaded", f"({len(df):,} rows)")
    record_timeline_event("Data Quality Checked", f"({df.isna().sum().sum():,} nulls)")
        
    return df

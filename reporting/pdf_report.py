import os
import tempfile
import pandas as pd
from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # Use Helvetica as fallback standard font
        self.set_font("Helvetica", size=12)
        
    def header(self):
        # Header banner
        self.set_fill_color(15, 23, 42) # Dark Slate
        self.rect(0, 0, 210, 25, 'F')
        
        # Title
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(248, 250, 252) # White
        self.cell(0, 10, "Data Detective - Investigation Report", 0, 1, "C")
        
        # Date
        self.set_font("Helvetica", "", 10)
        self.set_text_color(148, 163, 184) # Light Slate
        self.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, "C")
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_section_title(self, title):
        self.ln(5)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 41, 59)
        self.set_fill_color(226, 232, 240)
        self.cell(0, 10, f"  {title}", 0, 1, "L", fill=True)
        self.ln(5)
        
    def add_bullet_point(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(51, 65, 85)
        # Handle unicode issues with basic ascii replacement if needed
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 6, f"\x95 {safe_text}")
        
    def add_chart(self, fig, width=170):
        """Exports Plotly fig to temp png and embeds it."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmpfile:
                # Use kaleido to write image
                fig.write_image(tmpfile.name, engine="kaleido", scale=2)
                
                # Calculate center position
                x_pos = (210 - width) / 2
                self.image(tmpfile.name, x=x_pos, w=width)
                self.ln(5)
            
            # Clean up
            os.remove(tmpfile.name)
        except Exception as e:
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(239, 68, 68)
            self.cell(0, 10, f"[Chart Render Failed: {str(e)}]", 0, 1)

def generate_pdf_report(df: pd.DataFrame, session_state: dict) -> bytes:
    """
    Compiles all available analytical findings into a PDF byte string.
    """
    pdf = PDFReport()
    pdf.add_page()
    
    # 1. Dataset Summary
    pdf.add_section_title("Dataset Summary")
    pdf.add_bullet_point(f"Total Records: {len(df):,}")
    pdf.add_bullet_point(f"Total Features: {len(df.columns)}")
    
    missing_pct = (df.isna().sum().sum() / df.size) * 100
    pdf.add_bullet_point(f"Missing Data Rate: {missing_pct:.2f}%")
    
    duplicates = df.duplicated().sum()
    pdf.add_bullet_point(f"Duplicate Rows: {duplicates:,}")
    
    # 2. Dataset DNA
    from analytics.dataset_dna import generate_dataset_dna
    dna = generate_dataset_dna(df)
    pdf.add_section_title("Dataset DNA Profile")
    pdf.add_bullet_point(f"Overall Quality Score: {dna['Quality']}/100")
    pdf.add_bullet_point(f"Feature Complexity: {dna['Complexity']}/100")
    pdf.add_bullet_point(f"Clusterability Potential: {dna['Clusterability']}/100")
    pdf.add_bullet_point(f"Structural Stability (Anomaly Risk): {dna['Stability']}/100")
    
    # 3. Anomaly Results
    if 'Is_Anomaly' in df.columns:
        pdf.add_section_title("Anomaly Detection")
        total_anomalies = (df['Is_Anomaly'] == 'Anomaly').sum()
        anomaly_rate = (total_anomalies / len(df)) * 100
        pdf.add_bullet_point(f"Total Structural Anomalies Found: {total_anomalies:,} ({anomaly_rate:.1f}% of data)")
        
        if 'Anomaly_Score' in df.columns:
            max_score = df['Anomaly_Score'].max()
            pdf.add_bullet_point(f"Highest Anomaly Score: {max_score:.3f}")
            
    # 4. Clustering Results
    if 'Cluster_Label' in df.columns:
        pdf.add_section_title("Segment Discovery")
        valid_clusters = df[df['Cluster_Label'] != "Outliers/Noise"]['Cluster_Label']
        unique_count = valid_clusters.nunique()
        pdf.add_bullet_point(f"Total Natural Segments Identified: {unique_count}")
        if not valid_clusters.empty:
            largest_cluster = valid_clusters.value_counts().index[0]
            largest_pct = (valid_clusters.value_counts().iloc[0] / len(df)) * 100
            pdf.add_bullet_point(f"Dominant Segment: {largest_cluster} ({largest_pct:.1f}% of data)")
            
    # 5. Correlation Findings
    from analytics.correlation_engine import mine_correlations
    import numpy as np
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) >= 2:
        try:
            # Quick silent run
            ranked_rels, _, _ = mine_correlations(df, numeric_cols[:15])
            if ranked_rels:
                pdf.add_section_title("Correlation Findings")
                for i, rel in enumerate(ranked_rels[:5]):
                    val = rel['pearson']
                    direction = "Positive" if val > 0 else "Negative"
                    strength = "Strong" if abs(val) > 0.7 else "Moderate" if abs(val) > 0.4 else "Weak"
                    pdf.add_bullet_point(f"{rel['var1']} & {rel['var2']}: {strength} {direction} ({val:.2f})")
        except Exception:
            pass
            
    # Return as raw bytes
    return pdf.output(dest='S').encode('latin-1')

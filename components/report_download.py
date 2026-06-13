import streamlit as st
import pandas as pd
from reporting.pdf_report import generate_pdf_report

def render_report_download(df: pd.DataFrame):
    """
    Renders the PDF Report export button.
    """
    st.markdown('<div class="section-title" style="margin-top: 20px;">📥 Export Investigation</div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <p style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5; margin-bottom: 15px;">
            Compile all current findings, correlations, and dataset metrics into a professional PDF document.
        </p>
        """, 
        unsafe_allow_html=True
    )
    
    # Use a button to generate the PDF only when requested, as generation can take a few seconds
    if st.button("Generate PDF Report", icon="📄", type="primary", use_container_width=True):
        with st.spinner("Compiling PDF Investigation Report..."):
            try:
                pdf_bytes = generate_pdf_report(df, st.session_state)
                
                # Render the actual download button after generation
                st.download_button(
                    label="Download Report",
                    data=pdf_bytes,
                    file_name="Data_Detective_Report.pdf",
                    mime="application/pdf",
                    type="primary",
                    icon="⬇️",
                    use_container_width=True
                )
                st.success("Report compiled successfully! Click the button above to download.")
            except Exception as e:
                st.error(f"Failed to generate report: {str(e)}")

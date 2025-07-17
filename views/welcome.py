import streamlit as st

def render_welcome_page():
    """
    Renders the welcome page of the application.
    """
    
    st.markdown("""
        <div class="main-header">
            <h1>Thickness Uniformity Analysis</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## Get Started in 3 Simple Steps")
    
    cols = st.columns(3, gap="large")
    with cols[0]:
        st.markdown("""
        <div class="feature-box">
            <div class="icon">📤</div>
            <h3>1. Upload Data</h3>
            <p>Start by uploading your CSV file. Ensure it has the correct columns: `sensor_id`, `position_mm`, `thickness_mm`, `condition`, and `measurement_mm` for Pre-OL data.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class="feature-box">
            <div class="icon">📊</div>
            <h3>2. Analyse</h3>
            <p>Explore interactive dashboards for Pre-OL and Post-OL data. View summary statistics, score distributions, and individual sensor profiles.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class="feature-box">
            <div class="icon">📄</div>
            <h3>3. Export</h3>
            <p>Download comprehensive HTML reports for each analysis stage, or export the calculated uniformity scores to a CSV file for further use.</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    st.subheader("About the Analysis")
    with st.container(border=True):
        st.markdown("""
        This application is designed to provide a comprehensive analysis of thickness uniformity for materials, typically in a manufacturing or quality control context. It separates the analysis into two key stages:
        - **Pre-OL:** Analysis of the material thickness at the print stage.
        - **Post-OL:** Analysis after the OL dip, allowing for comparison and assessment of the process's impact on uniformity.
        
        The application calculates two key metrics:
        - **TUS (Targeted Uniformity Score):** Measures how close the thickness profile is to a desired target mean thickness and how uniform it is.
        - **RUS (Relative Uniformity Score):** Measures the intrinsic uniformity of the profile, regardless of its proximity to the target.
        
        Navigate using the sidebar to upload your data and explore the results.
        """) 
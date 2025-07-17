import streamlit as st

def render_help_page():
    """
    Renders the help and documentation page.
    """
    
    st.header("Help and Documentation")
    
    with st.container(border=True):
        st.subheader("Data Requirements")
        st.markdown("""
        - **File Format:** Must be a CSV file.
        - **Required Columns:** 
            - `sensor_id`: Unique identifier for each sensor or measurement run.
            - `position_mm`: The position along the measurement axis, in millimeters.
            - `thickness_mm`: The measured thickness, used for 'Post' condition analysis.
            - `condition`: The state of the measurement, either 'Pre' or 'Post'.
        - **'Pre' Condition Column:** If your data includes a 'Pre' condition, you must also include a `measurement_mm` column, which will be used for its thickness analysis.
        - **Data Integrity:** Ensure position and thickness/measurement columns contain only numeric values and no missing data.
        """)

    with st.container(border=True):
        st.subheader("Analysis Methods")
        st.markdown("""
        **TUS (Targeted Uniformity Score):** This score evaluates a sensor's thickness profile based on two main criteria: its closeness to a specified target mean thickness and its overall flatness or uniformity. A high TUS indicates that the profile is both accurately on-target and highly uniform. This is useful when you have a specific thickness goal.

        **RUS (Relative Uniformity Score):** This score evaluates a sensor's profile based solely on its flatness and uniformity, without considering its average thickness. A high RUS signifies a very consistent and even profile, even if its average thickness is far from the target. This is useful for assessing the intrinsic quality of a process.
        """)

    with st.container(border=True):
        st.subheader("Troubleshooting")
        st.markdown("""
        - **File Upload Error:** If you see an error after uploading, double-check that your file is a valid CSV and that all the required column names are present and spelled correctly.
        - **No Data Displayed on Analysis Pages:** This usually means the 'condition' column in your CSV does not contain 'Pre' or 'Post' values for the respective analysis pages. Check for typos or different naming conventions.
        - **Slow Performance:** For very large files (e.g., >100,000 rows), the initial data processing might take a few moments. Once the initial analysis is complete, navigating the app should be fast.
        - **Incorrect Plots or Calculations:** Ensure that the numeric columns (`position_mm`, `thickness_mm`, `measurement_mm`) do not contain any text, special characters (except the decimal point), or missing values.
        - **Report Download Issues:** If the downloaded report doesn't look right, try trying to clear your browser cache or using a different web browser.
        """) 
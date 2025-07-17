import streamlit as st
from processing.data_processing import load_and_validate_data, process_and_cache_results

def render_upload_page():
    """
    Renders the file upload page and handles the data processing.
    """
    st.header("Upload and Process Your Data")

    # --- Upload Area ---
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("##### 📤 Upload Your Data")
            uploaded_file = st.file_uploader(
                "Choose a CSV file",
                type="csv",
                help="Upload your data in CSV format."
            )
        with col2:
            st.markdown("##### ⚙️ Set Target Means")
            st.session_state.target_mean_pre = st.number_input("Target Mean Pre-OL (um)", value=st.session_state.get('target_mean_pre', 120.0), step=0.1, format="%.1f")
            st.session_state.target_mean_post = st.number_input("Target Mean Post-OL (um)", value=st.session_state.get('target_mean_post', 17.5), step=0.1, format="%.1f")

    # --- Processing and Validation ---
    if st.session_state.get('data_uploaded', False):
        # Show processing summary when data is already processed
        st.success("✅ Data processed successfully! Navigate to the analysis dashboards from the sidebar.")
        
        with st.container(border=True):
            st.markdown("##### 📊 Processing Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**Filename:** {st.session_state.get('input_filename', 'N/A')}")
                if not st.session_state.pre_scores.empty:
                    st.metric("Pre-OL Sensors", len(st.session_state.pre_scores))
                else:
                    st.metric("Pre-OL Sensors", "0")
            with col2:
                conditions = []
                if not st.session_state.pre_scores.empty:
                    conditions.append("Pre")
                if not st.session_state.post_scores.empty:
                    conditions.append("Post")
                st.info(f"**Conditions:** {', '.join(conditions) if conditions else 'None'}")
                if not st.session_state.post_scores.empty:
                    st.metric("Post-OL Sensors", len(st.session_state.post_scores))
                else:
                    st.metric("Post-OL Sensors", "0")
        
        if st.button("🗑️ Clear Processed Data", type="secondary"):
            # Reset session state related to data
            for key in ['data_uploaded', 'pre_scores', 'post_scores', 'pre_plots', 'post_plots', 'pre_report_html', 'post_report_html', 'input_filename', 'background_processing_started']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    elif uploaded_file:
        # Show file validation and processing only when no data is processed yet
        try:
            with st.spinner("Validating file..."):
                df = load_and_validate_data(uploaded_file)
            
            with st.container(border=True):
                st.success("✅ File validation successful!")
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Filename:** {uploaded_file.name}")
                    st.info(f"**Rows:** {len(df):,}")
                with col2:
                    conditions = df['condition'].unique()
                    st.info(f"**Conditions:** {', '.join(conditions)}")
                    st.info(f"**Sensors:** {df['sensor_id'].nunique():,}")
                
                if st.button("🚀 Process Data", use_container_width=True, type="primary"):
                    with st.spinner("Processing data... This may take a moment."):
                        process_and_cache_results(df, st.session_state.target_mean_pre, st.session_state.target_mean_post, uploaded_file.name)
                    st.rerun()

        except ValueError as e:
            st.error(f"**Validation Error:** {str(e)}")
        except Exception as e:
            st.error(f"**Unexpected Error:** Could not process the file. Please ensure it's a valid CSV. Error: {e}") 
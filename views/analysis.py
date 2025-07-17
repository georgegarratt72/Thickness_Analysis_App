import streamlit as st
import pandas as pd

def render_analysis_dashboard(analysis_type):
    """
    Renders the main analysis dashboard.
    """
    
    if 'data_uploaded' not in st.session_state or not st.session_state.data_uploaded:
        st.warning("Please upload and process data first on the 'Data Upload' page.")
        return

    if analysis_type == 'Pre-OL':
        scores = st.session_state.get('pre_scores', pd.DataFrame())
        title = "Pre-OL Analysis"
        plots = st.session_state.get('pre_plots', {})
        report_html = st.session_state.get('pre_report_html', "")
    else: # Post-OL
        scores = st.session_state.get('post_scores', pd.DataFrame())
        title = "Post-OL Analysis"
        plots = st.session_state.get('post_plots', {})
        report_html = st.session_state.get('post_report_html', "")

    st.header(title)

    if scores.empty:
        st.info(f"No {analysis_type} data was found in the uploaded file.")
        return

    # Create tabs with improved performance
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📋 Results", "📈 Plots"])

    with tab1:
        render_dashboard_tab(scores, plots, report_html, analysis_type)

    with tab2:
        render_results_tab(scores, analysis_type)

    with tab3:
        render_plots_tab(plots, analysis_type)

def render_dashboard_tab(scores, plots, report_html, analysis_type):
    """Renders the content of the 'Dashboard' tab."""
    
    st.subheader("📊 Summary Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Sensors", len(scores))
    with col2:
        mean_thickness = scores['mean_thickness'].mean()
        st.metric("Mean Thickness", f"{mean_thickness:.1f} μm")
    with col3:
        mean_sd = scores['thickness_sd'].mean()
        st.metric("Mean Std Dev", f"{mean_sd:.2f} μm")
    with col4:
        mean_range = scores['thickness_range'].mean()
        st.metric("Mean Range", f"{mean_range:.2f} μm")
    with col5:
        mean_tus = scores['TUS'].mean()
        st.metric("Mean TUS Score", f"{mean_tus:.3f}")
    with col6:
        mean_rus = scores['RUS'].mean()
        st.metric("Mean RUS Score", f"{mean_rus:.3f}")

    st.divider()

    # Report download section
    with st.container():
        st.subheader("📄 Download Report")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"✅ Complete HTML report with interactive charts is ready!")
            st.info(f"Full HTML report for {analysis_type} analysis with all visualizations and data tables.")
        with col2:
            st.download_button(
                label="📥 Download HTML Report",
                data=report_html,
                file_name=f"{analysis_type.replace('-', '_')}_report.html",
                mime="text/html",
                use_container_width=True,
                type="primary"
            )
    
    st.divider()

    # Statistical distributions with improved layout
    st.subheader("📈 Statistical Distributions")
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plots.get('TUS_dist'), use_container_width=True, key=f"tus_dist_{analysis_type}")
        
        with st.expander("📊 TUS Statistics"):
            tus_stats = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Min', 'Max', 'Median'],
                'Value': [
                    f"{scores['TUS'].mean():.3f}",
                    f"{scores['TUS'].std():.3f}",
                    f"{scores['TUS'].min():.3f}",
                    f"{scores['TUS'].max():.3f}",
                    f"{scores['TUS'].median():.3f}"
                ]
            })
            st.dataframe(tus_stats, use_container_width=True, hide_index=True)
    
    with col2:
        st.plotly_chart(plots.get('RUS_dist'), use_container_width=True, key=f"rus_dist_{analysis_type}")
        
        with st.expander("📊 RUS Statistics"):
            rus_stats = pd.DataFrame({
                'Metric': ['Mean', 'Std Dev', 'Min', 'Max', 'Median'],
                'Value': [
                    f"{scores['RUS'].mean():.3f}",
                    f"{scores['RUS'].std():.3f}",
                    f"{scores['RUS'].min():.3f}",
                    f"{scores['RUS'].max():.3f}",
                    f"{scores['RUS'].median():.3f}"
                ]
            })
            st.dataframe(rus_stats, use_container_width=True, hide_index=True)

def render_results_tab(scores, analysis_type):
    """Renders the content of the 'Results' tab."""
    st.subheader(f"📋 {analysis_type} Uniformity Scores")
    
    # Thickness statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Sensors", len(scores))
    with col2:
        thickness_mean = scores['mean_thickness'].mean()
        st.metric("Mean Thickness", f"{thickness_mean:.1f} μm")
    with col3:
        thickness_std = scores['thickness_sd'].mean()
        st.metric("Mean Std Dev", f"{thickness_std:.2f} μm")
    with col4:
        thickness_range = scores['thickness_range'].mean()
        st.metric("Mean Range", f"{thickness_range:.2f} μm")
    
    st.divider()
    
    # Comprehensive thickness statistics
    st.subheader("📊 Thickness Statistics Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Thickness Distribution**")
        thickness_stats = pd.DataFrame({
            'Metric': ['Mean', 'Std Dev', 'Min', 'Max', 'Median', 'Q1', 'Q3'],
            'Value (μm)': [
                f"{scores['mean_thickness'].mean():.2f}",
                f"{scores['mean_thickness'].std():.2f}",
                f"{scores['mean_thickness'].min():.2f}",
                f"{scores['mean_thickness'].max():.2f}",
                f"{scores['mean_thickness'].median():.2f}",
                f"{scores['mean_thickness'].quantile(0.25):.2f}",
                f"{scores['mean_thickness'].quantile(0.75):.2f}"
            ]
        })
        st.dataframe(thickness_stats, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("**Variability Metrics**")
        variability_stats = pd.DataFrame({
            'Metric': ['Mean Std Dev', 'Mean Range', 'Mean R²', 'Mean TUS', 'Mean RUS'],
            'Value': [
                f"{scores['thickness_sd'].mean():.3f}",
                f"{scores['thickness_range'].mean():.3f}",
                f"{scores['r2_straightness'].mean():.3f}",
                f"{scores['TUS'].mean():.3f}",
                f"{scores['RUS'].mean():.3f}"
            ]
        })
        st.dataframe(variability_stats, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Filtering section
    with st.expander("🔍 Filter & Search Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_sensor = st.text_input("🔍 Search Sensor ID", key=f"search_{analysis_type}")
        with col2:
            tus_range = st.slider("TUS Score Range", 0.0, 1.0, (0.0, 1.0), 0.01, key=f"tus_{analysis_type}")
        with col3:
            rus_range = st.slider("RUS Score Range", 0.0, 1.0, (0.0, 1.0), 0.01, key=f"rus_{analysis_type}")
    
    # Apply filters
    filtered_scores = scores.copy()
    if search_sensor:
        filtered_scores = filtered_scores[filtered_scores['sensor_id'].str.contains(search_sensor, case=False, na=False)]
    filtered_scores = filtered_scores[
        (filtered_scores['TUS'] >= tus_range[0]) & (filtered_scores['TUS'] <= tus_range[1]) &
        (filtered_scores['RUS'] >= rus_range[0]) & (filtered_scores['RUS'] <= rus_range[1])
    ]
    
    # Display results
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info(f"Showing {len(filtered_scores):,} of {len(scores):,} sensors")
    with col2:
        # Download button
        csv_data = filtered_scores.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{analysis_type.replace('-', '_')}_scores.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    if len(filtered_scores) > 0:
        # Display data with improved formatting
        display_df = filtered_scores.copy()
        
        # Format numerical columns
        numerical_cols = ['mean_thickness', 'thickness_sd', 'thickness_range', 'r2_straightness', 'TUS', 'RUS']
        for col in numerical_cols:
            if col in display_df.columns:
                if col in ['TUS', 'RUS', 'r2_straightness']:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.3f}")
                else:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")
        
        # Simple styling function for better readability
        def highlight_scores(val):
            return ''  # No color coding - just neutral display
        
        # Apply styling
        styled_df = display_df.style.applymap(highlight_scores, subset=['TUS', 'RUS'])
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Top performers section
        if len(filtered_scores) >= 3:
            st.subheader("🏆 Top Performers")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🥇 Best TUS Scores**")
                top_tus = filtered_scores.nlargest(3, 'TUS')[['sensor_id', 'TUS', 'RUS']]
                st.dataframe(top_tus.round(3), use_container_width=True, hide_index=True)
            
            with col2:
                st.markdown("**🥇 Best RUS Scores**")
                top_rus = filtered_scores.nlargest(3, 'RUS')[['sensor_id', 'TUS', 'RUS']]
                st.dataframe(top_rus.round(3), use_container_width=True, hide_index=True)
    else:
        st.warning("No sensors match the current filter criteria.")

def render_plots_tab(plots, analysis_type):
    """Renders the content of the 'Plots' tab."""
    st.subheader(f"📈 {analysis_type} Thickness Profiles")
    st.info("Thickness profiles are grouped by their uniformity scores. Higher scoring sensors are displayed first.")
    
    # TUS Profiles
    with st.container():
        st.markdown("### 🎯 TUS Profiles")
        st.plotly_chart(plots.get('TUS_profile'), use_container_width=True, key=f"tus_profile_{analysis_type}")

    st.divider()
    
    # RUS Profiles  
    with st.container():
        st.markdown("### 📏 RUS Profiles")
        st.plotly_chart(plots.get('RUS_profile'), use_container_width=True, key=f"rus_profile_{analysis_type}") 
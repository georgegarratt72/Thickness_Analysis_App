import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
import io
import base64

warnings.filterwarnings('ignore')

# --- Page Configuration ---
st.set_page_config(
    page_title="Sava Lot Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
def load_custom_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Initialize Session State ---
def init_session_state():
    """Initialize session state variables."""
    state_defaults = {
        'data_uploaded': False,
        'processed_data': None,
        'pre_scores': None,
        'post_scores': None,
        'pre_plots': {},
        'post_plots': {},
        'pre_report_html': "",
        'post_report_html': "",
        'processed_filename': None,
        'target_mean_pre': 120.0,
        'target_mean_post': 17.5,
        'current_page': 'Welcome'
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Data Processing Functions ---
@st.cache_data
def process_thickness_data(df, target_mean_pre=120.0, target_mean_post=17.5):
    """Process thickness data and calculate uniformity scores."""
    
    # Identify Pre-OL and Post-OL data
    thickness_cols = [col for col in df.columns if 'thickness' in col.lower() or 'thick' in col.lower()]
    
    if not thickness_cols:
        st.error("No thickness columns found in the data.")
        return None, None, None, None
    
    # Separate data based on thickness values
    pre_ol_data = []
    post_ol_data = []
    
    for _, row in df.iterrows():
        thickness_values = []
        positions = []
        
        for col in thickness_cols:
            if pd.notna(row[col]) and row[col] > 0:
                thickness_values.append(row[col])
                # Extract position from column name (assuming format like 'thickness_10mm')
                pos = col.split('_')[-1].replace('mm', '') if '_' in col else len(positions)
                try:
                    positions.append(float(pos))
                except:
                    positions.append(len(positions))
        
        if thickness_values:
            mean_thickness = np.mean(thickness_values)
            
            # Classify as Pre-OL or Post-OL based on mean thickness
            if mean_thickness > 50:  # Threshold for Pre-OL vs Post-OL
                pre_ol_data.append({
                    'sensor_id': row.get('sensor_id', f'sensor_{len(pre_ol_data)}'),
                    'positions': positions,
                    'thickness_values': thickness_values,
                    'mean_thickness': mean_thickness
                })
            else:
                post_ol_data.append({
                    'sensor_id': row.get('sensor_id', f'sensor_{len(post_ol_data)}'),
                    'positions': positions,
                    'thickness_values': thickness_values,
                    'mean_thickness': mean_thickness
                })
    
    # Calculate uniformity scores
    pre_scores = calculate_uniformity_scores(pre_ol_data, target_mean_pre) if pre_ol_data else pd.DataFrame()
    post_scores = calculate_uniformity_scores(post_ol_data, target_mean_post) if post_ol_data else pd.DataFrame()
    
    return pre_ol_data, post_ol_data, pre_scores, post_scores

def calculate_uniformity_scores(sensor_data, target_mean):
    """Calculate TUS and RUS scores for sensor data."""
    scores = []
    
    for sensor in sensor_data:
        thickness_values = np.array(sensor['thickness_values'])
        
        # Basic statistics
        mean_thickness = np.mean(thickness_values)
        thickness_sd = np.std(thickness_values)
        thickness_range = np.max(thickness_values) - np.min(thickness_values)
        
        # Calculate TUS (Thickness Uniformity Score)
        target_deviation = abs(mean_thickness - target_mean) / target_mean
        tus = max(0, 1 - target_deviation)
        
        # Calculate RUS (Range Uniformity Score) 
        range_coefficient = thickness_range / mean_thickness if mean_thickness > 0 else 1
        rus = max(0, 1 - range_coefficient)
        
        # R² for straightness (simplified)
        if len(thickness_values) > 2:
            positions = np.array(sensor['positions'])
            z = np.polyfit(positions, thickness_values, 1)
            p = np.poly1d(z)
            y_pred = p(positions)
            ss_res = np.sum((thickness_values - y_pred) ** 2)
            ss_tot = np.sum((thickness_values - np.mean(thickness_values)) ** 2)
            r2_straightness = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        else:
            r2_straightness = 0
        
        scores.append({
            'sensor_id': sensor['sensor_id'],
            'mean_thickness': mean_thickness,
            'thickness_sd': thickness_sd,
            'thickness_range': thickness_range,
            'r2_straightness': max(0, r2_straightness),
            'TUS': tus,
            'RUS': rus
        })
    
    return pd.DataFrame(scores)

# --- Plotting Functions ---
def create_distribution_plot(scores, score_type='TUS'):
    """Create distribution plot for TUS or RUS scores."""
    if scores.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=scores[score_type],
        nbinsx=20,
        name=f'{score_type} Distribution',
        marker_color='lightblue',
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f'{score_type} Score Distribution',
        xaxis_title=f'{score_type} Score',
        yaxis_title='Frequency',
        showlegend=False,
        height=400
    )
    
    return fig

def create_profile_plots(sensor_data, scores, score_type='TUS'):
    """Create thickness profile plots grouped by score ranges."""
    if not sensor_data or scores.empty:
        return go.Figure()
    
    # Sort by score
    sorted_scores = scores.sort_values(score_type, ascending=False)
    
    # Create subplots - but ensure we have at least 1 row
    num_sensors = min(len(sorted_scores), 10)  # Limit to top 10
    if num_sensors == 0:
        return go.Figure()
    
    fig = make_subplots(
        rows=max(1, (num_sensors + 1) // 2),  # Ensure at least 1 row
        cols=2,
        subplot_titles=[f"{sensor_id} ({score_type}: {score:.3f})" 
                       for sensor_id, score in zip(sorted_scores['sensor_id'].head(num_sensors), 
                                                 sorted_scores[score_type].head(num_sensors))]
    )
    
    for i, (_, row) in enumerate(sorted_scores.head(num_sensors).iterrows()):
        sensor_id = row['sensor_id']
        
        # Find sensor data
        sensor_info = next((s for s in sensor_data if s['sensor_id'] == sensor_id), None)
        if sensor_info:
            row_num = (i // 2) + 1
            col_num = (i % 2) + 1
            
            fig.add_trace(
                go.Scatter(
                    x=sensor_info['positions'],
                    y=sensor_info['thickness_values'],
                    mode='lines+markers',
                    name=sensor_id,
                    showlegend=False
                ),
                row=row_num, col=col_num
            )
    
    fig.update_layout(
        title=f'Top {num_sensors} Sensors by {score_type} Score',
        height=300 * max(1, (num_sensors + 1) // 2)
    )
    
    return fig

# --- Page Functions ---
def render_welcome_page():
    """Render the welcome page."""
    st.markdown("<h1 class='main-header'>🔬 Sava Lot Analysis</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### Welcome to the Thickness Uniformity Analysis App
        
        This application analyzes optical coating thickness data and calculates uniformity scores:
        
        - **TUS (Thickness Uniformity Score)**: Measures how close the mean thickness is to target
        - **RUS (Range Uniformity Score)**: Measures thickness variation across the sensor
        
        #### Getting Started:
        1. Upload your thickness data CSV file
        2. Review the automated Pre-OL and Post-OL analysis
        3. Download detailed reports and visualizations
        
        #### Data Format:
        Your CSV should contain thickness measurements with position information.
        """)

def render_upload_page():
    """Render the upload page."""
    st.header("☁️ Data Upload")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file containing thickness measurement data"
    )
    
    if uploaded_file is not None:
        try:
            # Read the file
            df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File uploaded successfully!")
            st.info(f"📊 Data shape: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Show data preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Process data button
            if st.button("🔄 Process Data", type="primary", use_container_width=True):
                with st.spinner("Processing data..."):
                    pre_data, post_data, pre_scores, post_scores = process_thickness_data(df)
                    
                    if pre_data is not None or post_data is not None:
                        # Store in session state
                        st.session_state.data_uploaded = True
                        st.session_state.processed_data = df
                        st.session_state.pre_scores = pre_scores
                        st.session_state.post_scores = post_scores
                        st.session_state.processed_filename = uploaded_file.name
                        
                        # Create plots
                        if pre_scores is not None and not pre_scores.empty:
                            st.session_state.pre_plots = {
                                'TUS_dist': create_distribution_plot(pre_scores, 'TUS'),
                                'RUS_dist': create_distribution_plot(pre_scores, 'RUS'),
                                'TUS_profile': create_profile_plots(pre_data, pre_scores, 'TUS'),
                                'RUS_profile': create_profile_plots(pre_data, pre_scores, 'RUS')
                            }
                        
                        if post_scores is not None and not post_scores.empty:
                            st.session_state.post_plots = {
                                'TUS_dist': create_distribution_plot(post_scores, 'TUS'),
                                'RUS_dist': create_distribution_plot(post_scores, 'RUS'),
                                'TUS_profile': create_profile_plots(post_data, post_scores, 'TUS'),
                                'RUS_profile': create_profile_plots(post_data, post_scores, 'RUS')
                            }
                        
                        st.success("✅ Data processed successfully!")
                        st.balloons()
                    else:
                        st.error("❌ No valid thickness data found in the file.")
                        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

def render_analysis_dashboard(analysis_type):
    """Render the analysis dashboard for Pre-OL or Post-OL."""
    if 'data_uploaded' not in st.session_state or not st.session_state.data_uploaded:
        st.warning("Please upload and process data first on the 'Data Upload' page.")
        return

    if analysis_type == 'Pre-OL':
        scores = st.session_state.get('pre_scores', pd.DataFrame())
        title = "Pre-OL Analysis"
        plots = st.session_state.get('pre_plots', {})
    else: # Post-OL
        scores = st.session_state.get('post_scores', pd.DataFrame())
        title = "Post-OL Analysis"
        plots = st.session_state.get('post_plots', {})

    st.header(title)

    if scores.empty:
        st.info(f"No {analysis_type} data was found in the uploaded file.")
        return

    # Summary metrics
    st.subheader("📊 Summary Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Sensors", len(scores))
    with col2:
        mean_thickness = scores['mean_thickness'].mean()
        st.metric("Mean Thickness", f"{mean_thickness:.1f} μm")
    with col3:
        mean_sd = scores['thickness_sd'].mean()
        st.metric("Mean Thickness Std Dev", f"{mean_sd:.2f} μm")
    with col4:
        mean_range = scores['thickness_range'].mean()
        st.metric("Mean Thickness Range", f"{mean_range:.2f} μm")
    with col5:
        mean_tus = scores['TUS'].mean()
        st.metric("Mean TUS Score", f"{mean_tus:.3f}")
    with col6:
        mean_rus = scores['RUS'].mean()
        st.metric("Mean RUS Score", f"{mean_rus:.3f}")

    st.divider()

    # Tabs for different views
    tab1, tab2 = st.tabs(["📊 Distributions", "📈 Profiles"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            if 'TUS_dist' in plots:
                st.plotly_chart(plots['TUS_dist'], use_container_width=True)
        with col2:
            if 'RUS_dist' in plots:
                st.plotly_chart(plots['RUS_dist'], use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### TUS Profiles")
            if 'TUS_profile' in plots:
                st.plotly_chart(plots['TUS_profile'], use_container_width=True)
        with col2:
            st.markdown("#### RUS Profiles")
            if 'RUS_profile' in plots:
                st.plotly_chart(plots['RUS_profile'], use_container_width=True)

    # Results table
    st.subheader("📋 Results")
    st.dataframe(scores, use_container_width=True)
    
    # Download button
    csv_data = scores.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download {analysis_type} Results",
        data=csv_data,
        file_name=f"{analysis_type.replace('-', '_')}_results.csv",
        mime="text/csv"
    )

def render_help_page():
    """Render the help page."""
    st.header("❓ Help & Documentation")
    
    st.markdown("""
    ## How to Use This Application
    
    ### 1. Data Upload
    - Upload a CSV file containing thickness measurements
    - The app automatically detects Pre-OL and Post-OL data based on thickness values
    - Data should include position and thickness information
    
    ### 2. Analysis
    - **TUS (Thickness Uniformity Score)**: Measures deviation from target thickness
    - **RUS (Range Uniformity Score)**: Measures thickness variation across sensor
    - Higher scores indicate better uniformity
    
    ### 3. Visualizations
    - Distribution plots show score distributions
    - Profile plots show thickness vs position for top performers
    
    ### 4. Export Results
    - Download analysis results as CSV files
    - Generate comprehensive HTML reports with all visualizations
    
    ## Troubleshooting
    - Ensure your CSV has thickness measurement columns
    - Check that data contains numeric values
    - Contact support if you encounter persistent issues
    """)

# --- Main Application ---
def main():
    """Main function to run the Streamlit application."""
    init_session_state()
    load_custom_css()
    
    with st.sidebar:
        st.markdown("<h1 style='color: white; text-align: center; font-size: 1.6em;'>SAVA</h1>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Navigation
        nav_options = [
            ("🏠 Welcome", "Welcome"),
            ("☁️ Data Upload", "Data Upload"),
            ("📏 Pre-OL Analysis", "Pre-OL Analysis"),
            ("📐 Post-OL Analysis", "Post-OL Analysis"),
            ("❓ Help", "Help")
        ]
        
        current_page = st.session_state.get('current_page', 'Welcome')
        
        for display_name, page_key in nav_options:
            if st.button(display_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        page = st.session_state.current_page

    # Render the selected page
    if page == "Welcome":
        render_welcome_page()
    elif page == "Data Upload":
        render_upload_page()
    elif page == "Pre-OL Analysis":
        render_analysis_dashboard("Pre-OL")
    elif page == "Post-OL Analysis":
        render_analysis_dashboard("Post-OL")
    elif page == "Help":
        render_help_page()

if __name__ == "__main__":
    main() 
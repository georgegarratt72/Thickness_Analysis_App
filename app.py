import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO
import tempfile
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
from streamlit_option_menu import option_menu
import os
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Thickness Uniformity Analysis",
    page_icon="📏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* --- Base Styles --- */
    body {
        font-family: 'Inter', sans-serif;
        background-color: #F8F9FA;
        color: #333333;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #091E42;
        font-weight: 700;
    }

    /* --- Keyboard Shortcuts --- */
    .keyboard-shortcuts {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: rgba(9, 30, 66, 0.9);
        color: white;
        padding: 10px;
        border-radius: 8px;
        font-size: 12px;
        max-width: 200px;
        display: none;
    }
    
    .keyboard-shortcuts.show {
        display: block;
    }
    
    .shortcut-item {
        margin: 4px 0;
    }
    
    .shortcut-key {
        background: #0062FF;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: bold;
        margin-right: 8px;
    }

    /* --- Loading States --- */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #0062FF;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* --- Error and Warning Styles --- */
    .error-container {
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #721c24;
    }
    
    .warning-container {
        background: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
    
    .info-container {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
    }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: #091E42;
        border-right: 1px solid #E0E0E0;
        border-left: none !important;
        border-top: none !important;
        border-bottom: none !important;
    }
    
    /* Remove any default borders on sidebar container */
    [data-testid="stSidebar"] > div {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Remove borders from sidebar content */
    [data-testid="stSidebar"] .block-container {
        border: none !important;
        box-shadow: none !important;
    }
    
    /* This targets the text inside the sidebar options */
    [data-testid="stSidebar"] .nav-link {
        color: #FFFFFF !important; 
        margin: 4px 0; /* Add some vertical margin */
    }
    
    /* This targets the selected option text in the sidebar */
    [data-testid="stSidebar"] .nav-link.active {
        color: #0062FF !important;
        background-color: #FFFFFF !important;
    }

    /* --- Main UI Components --- */
    .main-header {
        background: linear-gradient(90deg, #0062FF, #0A2540);
        color: #FFFFFF;
        padding: 3rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 98, 255, 0.3);
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 2.5em;
        font-weight: 700;
    }

    .feature-box {
        background: #FFFFFF;
        padding: 2.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #E0E0E0;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .feature-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    }
    .feature-box .icon {
        font-size: 3rem;
        color: #0062FF;
        margin-bottom: 1.5rem;
    }
    
    .content-box {
        background: #FFFFFF;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #E0E0E0;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        text-align: center;
        border: 1px solid #EAECEF;
        height: 100%;
    }
    .metric-card h4 {
        color: #5A6474;
        font-weight: 600;
        font-size: 1em;
        margin-bottom: 0.5rem;
    }
    .metric-card h2 {
        color: #091E42;
        font-size: 2.2em;
        font-weight: 700;
    }

    .upload-area {
        background: #FFFFFF;
        border: 2px dashed #D0D7E0;
        border-radius: 15px;
        padding: 2.5rem;
        text-align: center;
        margin: 2rem 0;
        transition: border-color 0.3s ease, background-color 0.3s ease;
    }
    .upload-area:hover {
        border-color: #0062FF;
        background-color: #f8f9fa;
    }
    
    .stTabs [data-baseweb="tab-list"] {
		gap: 24px;
        border-bottom: 2px solid #EAECEF;
	}
	.stTabs [data-baseweb="tab"] {
		height: 50px;
        background-color: transparent;
		padding: 0 16px;
        border-radius: 8px 8px 0 0;
        color: #5A6474;
        font-weight: 600;
	}
	.stTabs [data-baseweb="tab"]:hover {
		background-color: #F0F2F5;
        color: #0062FF;
	}
	.stTabs [aria-selected="true"] {
		background-color: transparent;
        border-bottom: 2px solid #0062FF;
        color: #0062FF;
	}

    .stButton>button {
        border: 2px solid #0062FF;
        border-radius: 8px;
        background-color: #0062FF;
        color: white;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #0052D6;
        color: white;
        border-color: #0052D6;
    }

    /* --- Accessibility Improvements --- */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }
    
    /* Focus indicators */
    .stButton>button:focus {
        outline: 2px solid #0062FF;
        outline-offset: 2px;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .feature-box {
            border: 2px solid #000000;
        }
        
        .metric-card {
            border: 2px solid #000000;
        }
    }

</style>

<!-- Keyboard Shortcuts Help -->
<div class="keyboard-shortcuts" id="keyboard-shortcuts">
    <div style="font-weight: bold; margin-bottom: 8px;">Keyboard Shortcuts</div>
    <div class="shortcut-item"><span class="shortcut-key">?</span>Toggle help</div>
    <div class="shortcut-item"><span class="shortcut-key">1</span>Welcome</div>
    <div class="shortcut-item"><span class="shortcut-key">2</span>Upload</div>
    <div class="shortcut-item"><span class="shortcut-key">3</span>Pre-OL</div>
    <div class="shortcut-item"><span class="shortcut-key">4</span>Post-OL</div>
    <div class="shortcut-item"><span class="shortcut-key">5</span>Help</div>
    <div class="shortcut-item"><span class="shortcut-key">Esc</span>Clear filters</div>
</div>

<script>
    // Keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Don't trigger when typing in input fields
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }
        
        const shortcuts = document.getElementById('keyboard-shortcuts');
        
        switch(event.key) {
            case '?':
                shortcuts.classList.toggle('show');
                break;
            case '1':
                // Navigate to Welcome (would need to integrate with Streamlit state)
                break;
            case '2':
                // Navigate to Upload
                break;
            case '3':
                // Navigate to Pre-OL
                break;
            case '4':
                // Navigate to Post-OL
                break;
            case '5':
                // Navigate to Help
                break;
            case 'Escape':
                shortcuts.classList.remove('show');
                break;
        }
    });
</script>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'pre_scores' not in st.session_state:
    st.session_state.pre_scores = None
if 'post_scores' not in st.session_state:
    st.session_state.post_scores = None
if 'page' not in st.session_state:
    st.session_state.page = 'Welcome'
if 'pre_y_max' not in st.session_state:
    st.session_state.pre_y_max = None
if 'post_y_max' not in st.session_state:
    st.session_state.post_y_max = None
# Add session state for pre-computed plots and reports
if 'pre_plots' not in st.session_state:
    st.session_state.pre_plots = {}
if 'post_plots' not in st.session_state:
    st.session_state.post_plots = {}
if 'pre_report_html' not in st.session_state:
    st.session_state.pre_report_html = ""
if 'post_report_html' not in st.session_state:
    st.session_state.post_report_html = ""
if 'processed_filename' not in st.session_state:
    st.session_state.processed_filename = None
if 'target_mean_pre' not in st.session_state:
    st.session_state.target_mean_pre = 120.0
if 'target_mean_post' not in st.session_state:
    st.session_state.target_mean_post = 17.5


@st.cache_data
def calculate_uniformity_scores(df, target_mean=17.5):
    """
    Calculate uniformity scores for thickness data
    """
    if df.empty:
        return pd.DataFrame()
    
    # Filter data to position_mm between 0.2 and 0.8 and thickness > 0
    df_filtered = df[
        (df['position_mm'] >= 0.2) & 
        (df['position_mm'] <= 0.8) & 
        (df['thickness_um'] > 0) & 
        (df['thickness_um'].notna())
    ].copy()
    
    if df_filtered.empty:
        return pd.DataFrame()
    
    # Calculate global max range
    global_max_range = df_filtered.groupby('sensor_id')['thickness_um'].apply(
        lambda x: x.max() - x.min()
    ).max()
    
    if not np.isfinite(global_max_range):
        global_max_range = 1
    
    results = []
    
    for sensor_id in df_filtered['sensor_id'].unique():
        sensor_data = df_filtered[df_filtered['sensor_id'] == sensor_id]
        
        # Basic statistics
        mean_thickness = sensor_data['thickness_um'].mean()
        thickness_sd = sensor_data['thickness_um'].std()
        thickness_range = sensor_data['thickness_um'].max() - sensor_data['thickness_um'].min()
        
        # R² straightness calculation
        if len(sensor_data) > 2 and sensor_data['position_mm'].var() > 0:
            X = sensor_data['position_mm'].values.reshape(-1, 1)
            y = sensor_data['thickness_um'].values
            model = LinearRegression()
            model.fit(X, y)
            y_pred = model.predict(X)
            r2_straightness = r2_score(y, y_pred)
        else:
            r2_straightness = 0
        
        # Symmetry score calculation
        median_pos = sensor_data['position_mm'].median()
        left_data = sensor_data[sensor_data['position_mm'] <= median_pos]
        right_data = sensor_data[sensor_data['position_mm'] > median_pos]
        
        if len(left_data) > 0 and len(right_data) > 0:
            left_mean = left_data['thickness_um'].mean()
            right_mean = right_data['thickness_um'].mean()
            overall_mean = (left_mean + right_mean) / 2
            
            if overall_mean > 0:
                symmetry_score = 1 - abs(left_mean - right_mean) / overall_mean
            else:
                symmetry_score = 0
        else:
            symmetry_score = 0
        
        symmetry_bonus = max(symmetry_score, 0)
        
        # Penalty calculations
        mean_penalty = np.exp(-((mean_thickness - target_mean)**2) / (2 * 2**2))
        smoothness_penalty = 1 / (1 + thickness_sd) if thickness_sd > 0 else 1
        range_penalty = 1 - thickness_range / global_max_range
        
        # Calculate TUS and RUS
        TUS = (0.3 * mean_penalty + 
               0.2 * smoothness_penalty + 
               0.2 * range_penalty + 
               0.2 * r2_straightness + 
               0.1 * symmetry_bonus)
        
        RUS = (0.25 * smoothness_penalty + 
               0.35 * range_penalty + 
               0.20 * r2_straightness + 
               0.20 * symmetry_bonus)
        
        # Categorize scores
        def categorize_score(score):
            if score >= 0.9:
                return "0.9 - 1.0"
            elif score >= 0.8:
                return "0.8 - 0.9"
            elif score >= 0.7:
                return "0.7 - 0.8"
            elif score >= 0.6:
                return "0.6 - 0.7"
            elif score >= 0.5:
                return "0.5 - 0.6"
            elif score >= 0.4:
                return "0.4 - 0.5"
            elif score >= 0.3:
                return "0.3 - 0.4"
            elif score >= 0.2:
                return "0.2 - 0.3"
            elif score >= 0.1:
                return "0.1 - 0.2"
            else:
                return "0.0 - 0.1"
        
        results.append({
            'sensor_id': sensor_id,
            'mean_thickness': mean_thickness,
            'thickness_sd': thickness_sd,
            'thickness_range': thickness_range,
            'r2_straightness': r2_straightness,
            'TUS': TUS,
            'RUS': RUS,
            'TUS_category': categorize_score(TUS),
            'RUS_category': categorize_score(RUS)
        })
    
    return pd.DataFrame(results)

@st.cache_data
def create_distribution_plot(scores_df, score_type='TUS'):
    """Create distribution plot for TUS or RUS scores"""
    if scores_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    category_col = f'{score_type}_category'
    # Categories sorted from low to high to have high scores at the top of the horizontal bar chart
    all_categories = [
        "0.0 - 0.1", "0.1 - 0.2", "0.2 - 0.3", "0.3 - 0.4", "0.4 - 0.5", 
        "0.5 - 0.6", "0.6 - 0.7", "0.7 - 0.8", "0.8 - 0.9", "0.9 - 1.0"
    ]
    
    # Define colors for categories (poor to excellent) using a sequential color scale
    colors = ['#d73027', '#f46d43', '#fdae61', '#fee08b', '#d9ef8b', '#a6d96a', '#66bd63', '#1a9850', '#006837', '#00441b']
    color_map = {cat: color for cat, color in zip(all_categories, colors)}

    scores_df[category_col] = pd.Categorical(scores_df[category_col], categories=all_categories, ordered=True)
    categories = scores_df[category_col].value_counts().sort_index()
    
    bar_colors = [color_map.get(cat, 'lightgrey') for cat in categories.index]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories.values,
            y=categories.index,
            orientation='h',
            marker_color=bar_colors,
            text=[f'{v}' for v in categories.values],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f'{score_type} Score Distribution',
        xaxis_title='Count',
        yaxis_title=f'{score_type} Category',
        height=400,
        showlegend=False,
        margin=dict(l=100, r=40, t=50, b=40)
    )
    
    return fig

@st.cache_data
def create_thickness_profiles_plot(df, scores_df, score_type='TUS', target_mean=17.5, y_range=None):
    """Create thickness profiles plot grouped by score category"""
    if df.empty or scores_df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Filter data
    df_filtered = df[
        (df['position_mm'] >= 0.2) & 
        (df['position_mm'] <= 0.8) & 
        (df['thickness_um'] > 0)
    ].copy()
    
    # Merge with scores
    category_col = f'{score_type}_category'
    df_plot = df_filtered.merge(
        scores_df[['sensor_id', category_col]], 
        on='sensor_id', 
        how='left'
    )
    
    # Get unique categories and sort them in descending order to show best scores first
    categories = sorted(df_plot[category_col].dropna().unique(), reverse=True)
    
    # Create subplots
    fig = make_subplots(
        rows=len(categories), 
        cols=1,
        subplot_titles=[f'{score_type}: {cat}' for cat in categories],
        vertical_spacing=0.15,
        shared_xaxes=True,
        shared_yaxes=True,
        x_title="Position (mm)",
        y_title="Thickness (μm)"
    )
    
    colors = px.colors.qualitative.Set3
    
    for i, category in enumerate(categories):
        category_data = df_plot[df_plot[category_col] == category]
        
        for j, sensor_id in enumerate(category_data['sensor_id'].unique()):
            sensor_data = category_data[category_data['sensor_id'] == sensor_id]
            sensor_data = sensor_data.sort_values('position_mm')
            
            fig.add_trace(
                go.Scatter(
                    x=sensor_data['position_mm'],
                    y=sensor_data['thickness_um'],
                    mode='lines+markers',
                    name=f'{sensor_id}',
                    line=dict(color=colors[j % len(colors)]),
                    showlegend=False
                ),
                row=i+1, col=1
            )
        
        # Add target line
        fig.add_hline(y=target_mean, line_dash="dash", line_color="red", annotation_text=f"Target: {target_mean} um", row="all", col="all")
    
    fig.update_layout(
        height=max(800, 400 * len(categories)), 
        showlegend=False,
        margin=dict(l=80, r=40, t=80, b=80)
    )
    
    # Update axes to avoid repetition
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    if y_range:
        fig.update_yaxes(range=y_range)
    
    return fig


def fig_to_base64(fig, width=1000, height=None):
    """Converts a Plotly figure to a base64 encoded string."""
    if fig is None:
        return ""
    try:
        buf = BytesIO()
        # Set explicit dimensions for better quality in HTML reports
        # Use the figure's layout height if no height is specified
        if height is None:
            height = fig.layout.height if fig.layout.height else 600
        fig.write_image(buf, format="png", width=width, height=height)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        st.warning(f"Could not convert plot to base64: {e}")
        return ""

def generate_lot_analysis_report_html(title, scores_data, pie_data, plot_objects, target_mean, input_filename):
    """
    Generates a standalone HTML report for lot analysis.
    """
    if not isinstance(scores_data, pd.DataFrame) or scores_data.empty:
        return "<html><body><h1>Report Generation Failed</h1><p>No valid scores data provided.</p></body></html>"

    # Encode logo
    logo_base64 = ""
    try:
        with open("logo.png", "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        logo_base64 = "" # Handle case where logo is not found

    total_sensors = len(scores_data)
    avg_tus = round(scores_data['TUS'].mean(), 3)
    avg_rus = round(scores_data['RUS'].mean(), 3)

    # Generate distribution plots
    tus_dist_plot = create_distribution_plot(scores_data, 'TUS')
    rus_dist_plot = create_distribution_plot(scores_data, 'RUS')
    
    # Generate profile plots
    tus_profile_plot = plot_objects.get('TUS_plot')
    rus_profile_plot = plot_objects.get('RUS_plot')

    # Convert plots to base64 with appropriate dimensions
    tus_dist_base64 = fig_to_base64(tus_dist_plot, width=1000, height=500)
    rus_dist_base64 = fig_to_base64(rus_dist_plot, width=1000, height=500)
    tus_profile_base64 = fig_to_base64(tus_profile_plot, width=1200) if tus_profile_plot else ""
    rus_profile_base64 = fig_to_base64(rus_profile_plot, width=1200) if rus_profile_plot else ""
    
    # Create scores table HTML, add a more modern class
    scores_table_html = scores_data.round(3).to_html(classes='styled-table', index=False)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #F8F9FA;
                color: #333333;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: #FFFFFF;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.05);
                padding: 40px;
            }}
            .header {{
                position: relative; /* For logo positioning */
                background: linear-gradient(90deg, #0062FF, #0A2540);
                color: #FFFFFF;
                padding: 30px;
                border-radius: 12px 12px 0 0;
                text-align: center;
                margin: -40px -40px 40px -40px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
            }}
            .header p {{
                margin: 5px 0 0;
                font-size: 1.1em;
                opacity: 0.9;
            }}
            .header .logo {{
                position: absolute;
                left: 40px;
                top: 50%;
                transform: translateY(-50%);
                height: 50px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .metric-card {{
                background-color: #F8F9FA;
                border: 1px solid #EAECEF;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
            }}
            .metric-card h3 {{
                margin: 0 0 10px 0;
                font-size: 1em;
                color: #5A6474;
                font-weight: 600;
            }}
            .metric-card h2 {{
                margin: 0;
                font-size: 2.2em;
                color: #091E42;
                font-weight: 700;
            }}
            .section-title {{
                font-size: 1.8em;
                color: #091E42;
                border-bottom: 2px solid #EAECEF;
                padding-bottom: 10px;
                margin-top: 40px;
                margin-bottom: 30px;
            }}
            .plot-container {{
                background-color: #F8F9FA;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 40px;
                border: 1px solid #EAECEF;
            }}
            .plot-container img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 0 auto;
                min-height: 400px;
            }}
            .plot-container.profile-plot {{
                min-height: 700px;
            }}
            .plot-container.profile-plot img {{
                min-height: 700px;
            }}
            .plot-container h3 {{
                margin-top: 0;
                text-align: center;
                font-size: 1.2em;
                color: #091E42;
            }}
            .styled-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 0.9em;
            }}
            .styled-table thead th {{
                background-color: #091E42;
                color: #FFFFFF;
                padding: 12px 15px;
                text-align: left;
                font-weight: 600;
            }}
            .styled-table tbody tr {{
                border-bottom: 1px solid #EAECEF;
            }}
            .styled-table tbody tr:nth-of-type(even) {{
                background-color: #F8F9FA;
            }}
            .styled-table tbody tr:hover {{
                background-color: #F0F2F5;
            }}
            .styled-table td, .styled-table th {{
                padding: 12px 15px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                {f'<img src="data:image/png;base64,{logo_base64}" alt="Logo" class="logo">' if logo_base64 else ''}
                <h1>{title}</h1>
                <p>Generated from: {input_filename}</p>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Sensors</h3>
                    <h2>{total_sensors}</h2>
                </div>
                <div class="metric-card">
                    <h3>Average TUS</h3>
                    <h2>{avg_tus}</h2>
                </div>
                <div class="metric-card">
                    <h3>Average RUS</h3>
                    <h2>{avg_rus}</h2>
                </div>
            </div>

            <h2 class="section-title">Score Distributions</h2>
            <div class="plot-container">
                <h3>TUS Score Distribution</h3>
                <img src="data:image/png;base64,{tus_dist_base64}" alt="TUS Distribution">
            </div>
            <div class="plot-container">
                <h3>RUS Score Distribution</h3>
                <img src="data:image/png;base64,{rus_dist_base64}" alt="RUS Distribution">
            </div>

            <h2 class="section-title">Thickness Profiles by Category</h2>
            <div class="plot-container profile-plot">
                <h3>TUS Profiles</h3>
                <img src="data:image/png;base64,{tus_profile_base64}" alt="TUS Profiles">
            </div>
            <div class="plot-container profile-plot">
                <h3>RUS Profiles</h3>
                <img src="data:image/png;base64,{rus_profile_base64}" alt="RUS Profiles">
            </div>

            <h2 class="section-title">Detailed Uniformity Scores</h2>
            {scores_table_html}
        </div>
    </body>
    </html>
    """
    return html_content

def create_download_link_html(html_content, filename):
    """Generates a link to download the HTML report."""
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}">Download Report</a>'

def process_uploaded_data(uploaded_file, target_mean_pre=120.0, target_mean_post=17.5):
    """
    Processes the uploaded CSV file, calculates scores, and stores them in session state.
    This function will now also pre-compute all plots and reports.
    """
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Load and validate data
        status_text.text("Loading and validating data...")
        progress_bar.progress(10)
        
        df = pd.read_csv(uploaded_file)
        
        # --- Data Validation ---
        required_cols = ['sensor_id', 'position_mm', 'thickness_mm', 'condition']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
            return

        df['condition'] = df['condition'].str.strip().str.title()
        
        if 'Pre' in df['condition'].values and 'measurement_mm' not in df.columns:
            st.error("Column 'measurement_mm' is required when 'Pre' condition data is present.")
            return

        st.session_state.original_data = df
        progress_bar.progress(25)
        
        # --- Pre-OL Processing ---
        status_text.text("Processing Pre-OL data...")
        pre_df = df[df['condition'] == 'Pre'].copy()
        if not pre_df.empty:
            pre_df = pre_df.rename(columns={'measurement_mm': 'thickness_um'})  # type: ignore
            st.session_state.pre_scores = calculate_uniformity_scores(pre_df, target_mean_pre)
            pre_filtered = pre_df[(pre_df['position_mm'] >= 0.2) & (pre_df['position_mm'] <= 0.8) & (pre_df['thickness_um'] > 0)]
            st.session_state.pre_y_max = pre_filtered['thickness_um'].max() * 1.05 if not pre_filtered.empty else None
            progress_bar.progress(45)
            
            # Pre-compute plots
            status_text.text("Generating Pre-OL visualizations...")
            y_range_pre = [0, st.session_state.pre_y_max] if st.session_state.pre_y_max else None
            st.session_state.pre_plots['TUS_dist'] = create_distribution_plot(st.session_state.pre_scores, 'TUS')
            st.session_state.pre_plots['RUS_dist'] = create_distribution_plot(st.session_state.pre_scores, 'RUS')
            progress_bar.progress(55)
            
            st.session_state.pre_plots['TUS_profile'] = create_thickness_profiles_plot(pre_filtered, st.session_state.pre_scores, 'TUS', target_mean_pre, y_range=y_range_pre)
            st.session_state.pre_plots['RUS_profile'] = create_thickness_profiles_plot(pre_filtered, st.session_state.pre_scores, 'RUS', target_mean_pre, y_range=y_range_pre)
            progress_bar.progress(65)
            
            # Pre-generate report
            status_text.text("Generating Pre-OL report...")
            report_plots = {'TUS_plot': st.session_state.pre_plots['TUS_profile'], 'RUS_plot': st.session_state.pre_plots['RUS_profile']}
            st.session_state.pre_report_html = generate_lot_analysis_report_html(
                "Pre-OL Thickness Uniformity Report", st.session_state.pre_scores, None, report_plots, target_mean_pre, uploaded_file.name
            )
            progress_bar.progress(70)
        else:
            st.session_state.pre_scores = pd.DataFrame()
            st.session_state.pre_y_max = None
            st.session_state.pre_plots = {}
            st.session_state.pre_report_html = ""

        # --- Post-OL Processing ---
        status_text.text("Processing Post-OL data...")
        post_df = df[df['condition'] == 'Post'].copy()
        if not post_df.empty:
            post_df = post_df.rename(columns={'thickness_mm': 'thickness_um'})  # type: ignore
            st.session_state.post_scores = calculate_uniformity_scores(post_df, target_mean_post)
            post_filtered = post_df[(post_df['position_mm'] >= 0.2) & (post_df['position_mm'] <= 0.8) & (post_df['thickness_um'] > 0)]
            st.session_state.post_y_max = post_filtered['thickness_um'].max() * 1.05 if not post_filtered.empty else None
            progress_bar.progress(85)
            
            # Pre-compute plots
            status_text.text("Generating Post-OL visualizations...")
            y_range_post = [0, st.session_state.post_y_max] if st.session_state.post_y_max else None
            st.session_state.post_plots['TUS_dist'] = create_distribution_plot(st.session_state.post_scores, 'TUS')
            st.session_state.post_plots['RUS_dist'] = create_distribution_plot(st.session_state.post_scores, 'RUS')
            st.session_state.post_plots['TUS_profile'] = create_thickness_profiles_plot(post_filtered, st.session_state.post_scores, 'TUS', target_mean_post, y_range=y_range_post)
            st.session_state.post_plots['RUS_profile'] = create_thickness_profiles_plot(post_filtered, st.session_state.post_scores, 'RUS', target_mean_post, y_range=y_range_post)
            progress_bar.progress(95)

            # Pre-generate report
            status_text.text("Generating Post-OL report...")
            report_plots = {'TUS_plot': st.session_state.post_plots['TUS_profile'], 'RUS_plot': st.session_state.post_plots['RUS_profile']}
            st.session_state.post_report_html = generate_lot_analysis_report_html(
                "Post-OL Thickness Uniformity Report", st.session_state.post_scores, None, report_plots, target_mean_post, uploaded_file.name
            )
        else:
            st.session_state.post_scores = pd.DataFrame()
            st.session_state.post_y_max = None
            st.session_state.post_plots = {}
            st.session_state.post_report_html = ""

        progress_bar.progress(100)
        status_text.text("Processing complete!")
        st.session_state.data_uploaded = True
        
        # Clear progress indicators after a brief delay
        import time
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        st.success("Data processed successfully!")

    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"An error occurred during file processing: {e}")
        st.session_state.data_uploaded = False

def validate_uploaded_file(uploaded_file):
    """
    Validate uploaded file and return validation results
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'info': {},
        'preview_df': None
    }
    
    try:
        # Read first few rows for preview
        df_preview = pd.read_csv(uploaded_file, nrows=100)
        validation_results['preview_df'] = df_preview
        
        # Reset file pointer
        uploaded_file.seek(0)
        
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        validation_results['info']['file_size_mb'] = round(file_size_mb, 2)
        
        if file_size_mb > 100:
            validation_results['warnings'].append(f"Large file detected ({file_size_mb:.1f} MB). Processing may take longer.")
        
        # Check required columns
        required_cols = ['sensor_id', 'position_mm', 'thickness_mm', 'condition']
        missing_cols = set(required_cols) - set(df_preview.columns)
        
        if missing_cols:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Missing required columns: {', '.join(missing_cols)}")
        
        # Check for Pre condition and measurement_mm column
        if 'condition' in df_preview.columns:
            conditions = df_preview['condition'].str.strip().str.title().unique()
            validation_results['info']['conditions_found'] = conditions.tolist()
            
            if 'Pre' in conditions and 'measurement_mm' not in df_preview.columns:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Column 'measurement_mm' is required when 'Pre' condition data is present.")
        
        # Check data types
        numeric_cols = ['position_mm', 'thickness_mm']
        if 'measurement_mm' in df_preview.columns:
            numeric_cols.append('measurement_mm')
            
        for col in numeric_cols:
            if col in df_preview.columns:
                try:
                    pd.to_numeric(df_preview[col], errors='coerce')
                    null_count = df_preview[col].isnull().sum()
                    if null_count > 0:
                        validation_results['warnings'].append(f"Column '{col}' contains {null_count} null values.")
                except:
                    validation_results['errors'].append(f"Column '{col}' contains non-numeric values.")
        
        # Check for duplicate sensor_id + position_mm combinations
        if 'sensor_id' in df_preview.columns and 'position_mm' in df_preview.columns:
            duplicates = df_preview.duplicated(subset=['sensor_id', 'position_mm', 'condition']).sum()
            if duplicates > 0:
                validation_results['warnings'].append(f"Found {duplicates} duplicate sensor_id + position_mm + condition combinations.")
        
        # Calculate estimated processing time
        row_count = len(df_preview)
        estimated_time = max(1, row_count / 1000)  # Rough estimate
        validation_results['info']['estimated_processing_time'] = f"{estimated_time:.1f} seconds"
        validation_results['info']['row_count'] = row_count
        
    except Exception as e:
        validation_results['is_valid'] = False
        validation_results['errors'].append(f"Error reading file: {str(e)}")
    
    return validation_results


def render_welcome_page():
    st.markdown("""
        <div class='main-header'>
            <h1>Thickness Uniformity Analysis</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("## Get Started in 3 Simple Steps")
    
    cols = st.columns(3, gap="large")
    with cols[0]:
        st.markdown("""
        <div class='feature-box'>
            <div class='icon'>📤</div>
            <h3>1. Upload Data</h3>
            <p>Start by uploading your CSV file. Ensure it has the correct columns: `sensor_id`, `position_mm`, `thickness_mm`, `condition`, and `measurement_mm` for Pre-OL data.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[1]:
        st.markdown("""
        <div class='feature-box'>
            <div class='icon'>📊</div>
            <h3>2. Analyse</h3>
            <p>Explore interactive dashboards for Pre-OL and Post-OL data. View summary statistics, score distributions, and individual sensor profiles.</p>
        </div>
        """, unsafe_allow_html=True)
    with cols[2]:
        st.markdown("""
        <div class='feature-box'>
            <div class='icon'>📄</div>
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

def render_upload_page():
    st.header("Data Upload & Configuration")
    
    with st.container(border=True):
        st.subheader("Upload Your Data File")
        
        uploaded_file = st.file_uploader(
            "Upload your CSV data file",
            type="csv",
            help="Required columns: `sensor_id`, `position_mm`, `thickness_mm`, `condition`. `measurement_mm` is also needed for 'Pre' condition data."
        )
        
        # File validation and preview
        if uploaded_file is not None:
            validation_results = validate_uploaded_file(uploaded_file)
            
            # Display validation results
            if validation_results['errors']:
                st.error("❌ File validation failed:")
                for error in validation_results['errors']:
                    st.write(f"• {error}")
            else:
                st.success("✅ File validation passed!")
            
            if validation_results['warnings']:
                st.warning("⚠️ Warnings:")
                for warning in validation_results['warnings']:
                    st.write(f"• {warning}")
            
            # Display file info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Size", f"{validation_results['info'].get('file_size_mb', 0)} MB")
            with col2:
                st.metric("Rows (preview)", validation_results['info'].get('row_count', 0))
            with col3:
                st.metric("Est. Processing Time", validation_results['info'].get('estimated_processing_time', 'Unknown'))
            
            # Show conditions found
            if 'conditions_found' in validation_results['info']:
                st.info(f"📊 Conditions found: {', '.join(validation_results['info']['conditions_found'])}")
            
            # File preview
            if validation_results['preview_df'] is not None:
                with st.expander("📋 File Preview (first 100 rows)", expanded=False):
                    st.dataframe(validation_results['preview_df'], use_container_width=True)
            
            # Only show processing section if validation passes
            if validation_results['is_valid']:
                st.markdown("---")
                st.subheader("✅ Ready to Process")
                st.info("Your file has been validated and is ready for processing. Configure the analysis parameters below and the data will be processed automatically.")

    with st.container(border=True):
        st.subheader("Analysis Parameters")
        st.markdown("Set the target mean thickness for your analysis. The data will be reprocessed automatically if you change these values.")
        
        col1, col2 = st.columns(2)
        with col1:
            target_mean_pre = st.number_input("Target Mean for Pre-OL (μm)", value=st.session_state.get('target_mean_pre', 120.0), step=0.1, help="Set the target mean thickness for the Pre-OL analysis.")
        with col2:
            target_mean_post = st.number_input("Target Mean for Post-OL (μm)", value=st.session_state.get('target_mean_post', 17.5), step=0.1, help="Set the target mean thickness for the Post-OL analysis.")

    # --- Automatic Processing Logic ---
    if uploaded_file is not None:
        validation_results = validate_uploaded_file(uploaded_file)
        
        if validation_results['is_valid']:
            is_new_file = uploaded_file.name != st.session_state.get('processed_filename')
            
            params_changed = (
                not is_new_file and
                (target_mean_pre != st.session_state.get('target_mean_pre') or target_mean_post != st.session_state.get('target_mean_post'))
            )

            if is_new_file or params_changed:
                process_uploaded_data(uploaded_file, target_mean_pre, target_mean_post)
                st.session_state.processed_filename = uploaded_file.name
                st.session_state.target_mean_pre = target_mean_pre
                st.session_state.target_mean_post = target_mean_post
                st.rerun()
    
    # Show processed data info
    if st.session_state.get('data_uploaded', False):
        st.markdown("---")
        st.success("🎉 Data Successfully Processed!")
        
        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            if hasattr(st.session_state, 'pre_scores') and not st.session_state.pre_scores.empty:
                st.metric("Pre-OL Sensors", len(st.session_state.pre_scores))
            else:
                st.metric("Pre-OL Sensors", 0)
        with col2:
            if hasattr(st.session_state, 'post_scores') and not st.session_state.post_scores.empty:
                st.metric("Post-OL Sensors", len(st.session_state.post_scores))
            else:
                st.metric("Post-OL Sensors", 0)
        with col3:
            total_sensors = 0
            if hasattr(st.session_state, 'pre_scores') and not st.session_state.pre_scores.empty:
                total_sensors += len(st.session_state.pre_scores)
            if hasattr(st.session_state, 'post_scores') and not st.session_state.post_scores.empty:
                total_sensors += len(st.session_state.post_scores)
            st.metric("Total Sensors", total_sensors)
        
        # Navigation hint
        st.info("💡 Navigate to the Pre-OL Analysis or Post-OL Analysis pages to explore your results!")
        
        # Option to reset/clear data
        if st.button("🔄 Clear Data and Start Over", type="secondary"):
            # Clear all session state data
            for key in ['data_uploaded', 'processed_data', 'pre_scores', 'post_scores', 'pre_y_max', 'post_y_max', 'pre_plots', 'post_plots', 'pre_report_html', 'post_report_html', 'processed_filename', 'original_data']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        with st.expander("Preview Processed Data", expanded=False):
            if hasattr(st.session_state, 'original_data'):
                st.dataframe(st.session_state.original_data, use_container_width=True)


def render_analysis_dashboard(analysis_type):
    if analysis_type == 'Pre-OL':
        scores = st.session_state.pre_scores
        title = "Pre-OL Analysis"
        plots = st.session_state.pre_plots
        report_html = st.session_state.pre_report_html
    else:
        scores = st.session_state.post_scores
        title = "Post-OL Analysis"
        plots = st.session_state.post_plots
        report_html = st.session_state.post_report_html

    st.header(title)

    if not plots:
        st.info(f"No {analysis_type} data to display. Please upload data on the 'Data Upload' page.", icon="📤")
        return

    # --- Dashboard Tab ---
    dash_tab, res_tab, plots_tab = st.tabs(["Dashboard", "Results", "Plots"])

    with dash_tab:
        
        # --- Metrics Section ---
        st.subheader("Summary Metrics")
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            st.markdown(f"<div class='metric-card'><h4>Total Sensors</h4><h2>{len(scores)}</h2></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><h4>Average TUS</h4><h2>{scores['TUS'].mean():.3f}</h2></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><h4>Average RUS</h4><h2>{scores['RUS'].mean():.3f}</h2></div>", unsafe_allow_html=True)

        st.markdown("<hr style='margin: 2rem 0; border-color: #EAECEF;'>", unsafe_allow_html=True)

        # --- Reporting Section ---
        with st.container(border=True):
            st.subheader("Download Full Report")
            st.download_button(
                label=f"Download {analysis_type} Report (HTML)",
                data=report_html,
                file_name=f"{analysis_type}_report.html",
                mime="text/html",
                use_container_width=True
            )
        
        st.markdown("<hr style='margin: 2rem 0; border-color: #EAECEF;'>", unsafe_allow_html=True)

        # --- Distributions Section ---
        st.subheader("Score Distributions")
        c1, c2 = st.columns(2, gap="large")
        with c1:
            with st.container(border=True):
                st.plotly_chart(plots.get('TUS_dist'), use_container_width=True)
                
                # Export TUS distribution plot
                if plots.get('TUS_dist'):
                    tus_dist_img = plots.get('TUS_dist').to_image(format="png", width=800, height=600)
                    st.download_button(
                        label="📥 Download TUS Distribution Plot",
                        data=tus_dist_img,
                        file_name=f"{analysis_type}_TUS_distribution.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                with st.expander("View TUS Data"):
                    tus_summary = scores['TUS_category'].value_counts().reset_index()
                    tus_summary.columns = ['TUS Category', 'Count']
                    st.dataframe(tus_summary, use_container_width=True)
        with c2:
            with st.container(border=True):
                st.plotly_chart(plots.get('RUS_dist'), use_container_width=True)
                
                # Export RUS distribution plot
                if plots.get('RUS_dist'):
                    rus_dist_img = plots.get('RUS_dist').to_image(format="png", width=800, height=600)
                    st.download_button(
                        label="📥 Download RUS Distribution Plot",
                        data=rus_dist_img,
                        file_name=f"{analysis_type}_RUS_distribution.png",
                        mime="image/png",
                        use_container_width=True
                    )
                
                with st.expander("View RUS Data"):
                    rus_summary = scores['RUS_category'].value_counts().reset_index()
                    rus_summary.columns = ['RUS Category', 'Count']
                    st.dataframe(rus_summary, use_container_width=True)
    
    with res_tab:
        st.subheader(f"{analysis_type} Uniformity Scores Data Table")
        
        # Search and filter controls
        with st.expander("🔍 Search & Filter Options", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_sensor = st.text_input("Search Sensor ID", placeholder="Enter sensor ID...")
                tus_range = st.slider("TUS Score Range", 0.0, 1.0, (0.0, 1.0), step=0.01)
            
            with col2:
                rus_range = st.slider("RUS Score Range", 0.0, 1.0, (0.0, 1.0), step=0.01)
                thickness_range = st.slider("Mean Thickness Range", 
                                          float(scores['mean_thickness'].min()), 
                                          float(scores['mean_thickness'].max()), 
                                          (float(scores['mean_thickness'].min()), float(scores['mean_thickness'].max())),
                                          step=0.1)
            
            with col3:
                tus_categories = st.multiselect("TUS Categories", 
                                              options=sorted(scores['TUS_category'].unique()),
                                              default=sorted(scores['TUS_category'].unique()))
                rus_categories = st.multiselect("RUS Categories", 
                                              options=sorted(scores['RUS_category'].unique()),
                                              default=sorted(scores['RUS_category'].unique()))
        
        # Apply filters
        filtered_scores = scores.copy()
        
        if search_sensor:
            filtered_scores = filtered_scores[filtered_scores['sensor_id'].str.contains(search_sensor, case=False, na=False)]
        
        filtered_scores = filtered_scores[
            (filtered_scores['TUS'] >= tus_range[0]) & 
            (filtered_scores['TUS'] <= tus_range[1]) &
            (filtered_scores['RUS'] >= rus_range[0]) & 
            (filtered_scores['RUS'] <= rus_range[1]) &
            (filtered_scores['mean_thickness'] >= thickness_range[0]) & 
            (filtered_scores['mean_thickness'] <= thickness_range[1]) &
            (filtered_scores['TUS_category'].isin(tus_categories)) &
            (filtered_scores['RUS_category'].isin(rus_categories))
        ]
        
        # Display filter results
        st.info(f"Showing {len(filtered_scores)} of {len(scores)} sensors")
        
        # Sorting options
        col1, col2 = st.columns(2)
        with col1:
            sort_column = st.selectbox("Sort by", 
                                     options=['sensor_id', 'TUS', 'RUS', 'mean_thickness', 'thickness_sd', 'thickness_range'])
        with col2:
            sort_order = st.radio("Sort order", ['Ascending', 'Descending'], horizontal=True)
        
        # Apply sorting
        ascending = sort_order == 'Ascending'
        filtered_scores = filtered_scores.sort_values(sort_column, ascending=ascending)
        
        # Download filtered scores as CSV
        csv_export = filtered_scores.to_csv(index=False).encode('utf-8')
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label=f"📥 Download Filtered {analysis_type} Scores (CSV)",
                    data=csv_export,
                    file_name=f"{analysis_type}_scores_filtered.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label=f"📥 Download All {analysis_type} Scores (CSV)",
                    data=scores.to_csv(index=False).encode('utf-8'),
                    file_name=f"{analysis_type}_scores_all.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        # Display filtered data with formatting
        if not filtered_scores.empty:
            # Color coding for better visualization
            def color_score(val):
                if val >= 0.9:
                    return 'background-color: #d4edda; color: #155724'  # Green
                elif val >= 0.7:
                    return 'background-color: #d1ecf1; color: #0c5460'  # Blue
                elif val >= 0.5:
                    return 'background-color: #fff3cd; color: #856404'  # Yellow
                else:
                    return 'background-color: #f8d7da; color: #721c24'  # Red
            
            styled_df = filtered_scores.style.format({
                'mean_thickness': '{:.2f}',
                'thickness_sd': '{:.3f}',
                'thickness_range': '{:.2f}',
                'r2_straightness': '{:.3f}',
                'TUS': '{:.3f}',
                'RUS': '{:.3f}'
            }).applymap(color_score, subset=['TUS', 'RUS'])
            
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("No data matches the current filters. Try adjusting your search criteria.")
            
        # Quick statistics for filtered data
        if not filtered_scores.empty:
            st.subheader("📊 Filtered Data Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Average TUS", f"{filtered_scores['TUS'].mean():.3f}")
            with col2:
                st.metric("Average RUS", f"{filtered_scores['RUS'].mean():.3f}")
            with col3:
                st.metric("Best TUS", f"{filtered_scores['TUS'].max():.3f}")
            with col4:
                st.metric("Best RUS", f"{filtered_scores['RUS'].max():.3f}")
            
            # Show best and worst performers
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🏆 Top 3 TUS Performers")
                top_tus = filtered_scores.nlargest(3, 'TUS')[['sensor_id', 'TUS', 'RUS']]
                st.dataframe(top_tus.round(3), use_container_width=True)
            
            with col2:
                st.subheader("🔧 Bottom 3 TUS Performers")
                bottom_tus = filtered_scores.nsmallest(3, 'TUS')[['sensor_id', 'TUS', 'RUS']]
                st.dataframe(bottom_tus.round(3), use_container_width=True)

    with plots_tab:
        st.subheader(f"{analysis_type} Thickness Profiles by Score")
        st.info("These plots show the thickness profiles of individual sensors, grouped by their calculated uniformity score. Higher scores are displayed first.")
        
        with st.container(border=True):
            st.subheader("TUS Profiles")
            st.plotly_chart(plots.get('TUS_profile'), use_container_width=True)
            
            # Export TUS profile plot
            if plots.get('TUS_profile'):
                col1, col2 = st.columns(2)
                with col1:
                    tus_profile_img = plots.get('TUS_profile').to_image(format="png", width=1200, height=800)
                    st.download_button(
                        label="📥 Download TUS Profile Plot",
                        data=tus_profile_img,
                        file_name=f"{analysis_type}_TUS_profiles.png",
                        mime="image/png",
                        use_container_width=True
                    )
                with col2:
                    # Add option to download as SVG for better quality
                    try:
                        tus_profile_svg = plots.get('TUS_profile').to_image(format="svg", width=1200, height=800)
                        st.download_button(
                            label="📥 Download TUS Profile Plot (SVG)",
                            data=tus_profile_svg,
                            file_name=f"{analysis_type}_TUS_profiles.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )
                    except:
                        pass  # SVG export might not be available

        with st.container(border=True):
            st.subheader("RUS Profiles")
            st.plotly_chart(plots.get('RUS_profile'), use_container_width=True)
            
            # Export RUS profile plot
            if plots.get('RUS_profile'):
                col1, col2 = st.columns(2)
                with col1:
                    rus_profile_img = plots.get('RUS_profile').to_image(format="png", width=1200, height=800)
                    st.download_button(
                        label="📥 Download RUS Profile Plot",
                        data=rus_profile_img,
                        file_name=f"{analysis_type}_RUS_profiles.png",
                        mime="image/png",
                        use_container_width=True
                    )
                with col2:
                    # Add option to download as SVG for better quality
                    try:
                        rus_profile_svg = plots.get('RUS_profile').to_image(format="svg", width=1200, height=800)
                        st.download_button(
                            label="📥 Download RUS Profile Plot (SVG)",
                            data=rus_profile_svg,
                            file_name=f"{analysis_type}_RUS_profiles.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )
                    except:
                        pass  # SVG export might not be available




def render_help_page():
    st.header("Help & Documentation")
    
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
        - **Report Download Issues:** If the downloaded report doesn't look right, try clearing your browser cache or using a different web browser.
        """)


def main():
    # --- Sidebar Navigation ---
    with st.sidebar:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
        else:
            st.markdown("<h1 style='color: white; text-align: center; margin-bottom: 1rem;'>šava</h1>", unsafe_allow_html=True)
        
        page = option_menu(
            menu_title=None,
            options=["Welcome", "Data Upload", "Pre-OL Analysis", "Post-OL Analysis", "Help"],
            icons=['house-door-fill', 'cloud-upload-fill', 'rulers', 'rulers', 'question-circle-fill'],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px !important", "background-color": "#091E42"},
                "icon": {"color": "white", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#0052D6", "border-radius": "8px", "color": "#E0E0E0"},
                "nav-link-selected": {"background-color": "#0062FF", "color": "#FFFFFF !important"},
            }
        )

    # --- Page Rendering ---
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
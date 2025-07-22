import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from .plotting import create_distribution_plot, create_thickness_profiles_plot
from utils.helpers import generate_lot_analysis_report_html

def get_session_id():
    """Get unique session ID for cache isolation between users."""
    if 'session_id' not in st.session_state:
        import uuid
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id

@st.cache_data
def load_and_validate_data(uploaded_file, _session_id=None):
    """Loads and validates the uploaded CSV file. _session_id ensures cache isolation between users."""
    df = pd.read_csv(uploaded_file)
    
    required_cols = ['sensor_id', 'position_mm', 'condition']
    if not all(col in df.columns for col in required_cols):
        raise ValueError("CSV must contain 'sensor_id', 'position_mm', and 'condition' columns.")

    df['condition'] = df['condition'].str.strip().str.title()
    
    # Check condition-specific requirements
    if 'Pre' in df['condition'].values and 'measurement_mm' not in df.columns:
        raise ValueError("Column 'measurement_mm' is required for 'Pre' condition data.")
    
    if 'Post' in df['condition'].values and 'thickness_mm' not in df.columns:
        raise ValueError("Column 'thickness_mm' is required for 'Post' condition data.")
        
    return df

@st.cache_data
def calculate_uniformity_scores(_df, target_mean=17.5, _session_id=None):
    """Calculate uniformity scores for thickness data. _session_id ensures cache isolation between users."""
    if _df.empty:
        return pd.DataFrame()
    
    df_filtered = _df[
        (_df['position_mm'] >= 0.2) & 
        (_df['position_mm'] <= 0.8) & 
        (_df['thickness_um'] > 0) & 
        (_df['thickness_um'].notna())
    ].copy()
    
    if df_filtered.empty:
        return pd.DataFrame()
    
    # Vectorized calculations for speed
    grouped = df_filtered.groupby('sensor_id')
    
    results = grouped['thickness_um'].agg(['mean', 'std', 'min', 'max']).reset_index()
    results.rename(columns={'mean': 'mean_thickness', 'std': 'thickness_sd'}, inplace=True)
    results['thickness_range'] = results['max'] - results['min']
    
    # R² straightness (requires iteration)
    r2_scores = []
    for sensor_id, sensor_data in grouped:
        if len(sensor_data) > 2 and sensor_data['position_mm'].var() > 0:
            X = sensor_data['position_mm'].values.reshape(-1, 1)
            y = sensor_data['thickness_um'].values
            model = LinearRegression().fit(X, y)
            r2_scores.append({'sensor_id': sensor_id, 'r2_straightness': r2_score(y, model.predict(X))})
        else:
            r2_scores.append({'sensor_id': sensor_id, 'r2_straightness': 0})
    
    results = pd.merge(results, pd.DataFrame(r2_scores), on='sensor_id')

    # Symmetry score (requires iteration)
    symmetry_scores = []
    for sensor_id, sensor_data in grouped:
        median_pos = sensor_data['position_mm'].median()
        left_mean = sensor_data[sensor_data['position_mm'] <= median_pos]['thickness_um'].mean()
        right_mean = sensor_data[sensor_data['position_mm'] > median_pos]['thickness_um'].mean()
        overall_mean = (left_mean + right_mean) / 2
        symmetry_score = 1 - abs(left_mean - right_mean) / overall_mean if overall_mean > 0 else 0
        symmetry_scores.append({'sensor_id': sensor_id, 'symmetry_bonus': max(symmetry_score, 0)})
        
    results = pd.merge(results, pd.DataFrame(symmetry_scores), on='sensor_id')

    # Penalties and final scores
    global_max_range = results['thickness_range'].max()
    results['mean_penalty'] = np.exp(-((results['mean_thickness'] - target_mean)**2) / (2 * 2**2))
    results['smoothness_penalty'] = 1 / (1 + results['thickness_sd'].fillna(0))
    results['range_penalty'] = 1 - results['thickness_range'] / global_max_range if global_max_range > 0 else 0
    
    results['TUS'] = (0.3 * results['mean_penalty'] + 
                      0.2 * results['smoothness_penalty'] + 
                      0.2 * results['range_penalty'] + 
                      0.2 * results['r2_straightness'] + 
                      0.1 * results['symmetry_bonus'])
    
    results['RUS'] = (0.25 * results['smoothness_penalty'] + 
                      0.35 * results['range_penalty'] + 
                      0.20 * results['r2_straightness'] + 
                      0.20 * results['symmetry_bonus'])

    # Categorize scores
    bins = [-np.inf, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, np.inf]
    labels = ["0.0 - 0.1", "0.1 - 0.2", "0.2 - 0.3", "0.3 - 0.4", "0.4 - 0.5", "0.5 - 0.6", "0.6 - 0.7", "0.7 - 0.8", "0.8 - 0.9", "0.9 - 1.0"]
    results['TUS_category'] = pd.cut(results['TUS'], bins=bins, labels=labels, right=False)
    results['RUS_category'] = pd.cut(results['RUS'], bins=bins, labels=labels, right=False)
    
    return results[['sensor_id', 'mean_thickness', 'thickness_sd', 'thickness_range', 'r2_straightness', 'TUS', 'RUS', 'TUS_category', 'RUS_category']]

def process_and_cache_results(df, target_mean_pre, target_mean_post, filename):
    """Processes both Pre and Post OL data and caches all results."""
    
    # Get session ID for cache isolation
    session_id = get_session_id()
    
    # --- Pre-OL ---
    pre_df = df[df['condition'] == 'Pre'].copy()
    if not pre_df.empty:
        # For Pre-OL data, use measurement_mm as thickness (already in microns, just rename)
        if 'measurement_mm' in pre_df.columns:
            pre_df['thickness_um'] = pre_df['measurement_mm']  # Already in microns
        else:
            st.error("Pre-OL data requires 'measurement_mm' column")
            return
        st.session_state.pre_scores = calculate_uniformity_scores(pre_df, target_mean_pre, _session_id=session_id)
        
        pre_filtered = pre_df[(pre_df['position_mm'] >= 0.2) & (pre_df['position_mm'] <= 0.8) & (pre_df['thickness_um'] > 0)]
        if not pre_filtered.empty:
            pre_y_min = pre_filtered['thickness_um'].min()
            pre_y_max = pre_filtered['thickness_um'].max()
            # Calculate dynamic range with tighter padding for better profile visibility
            y_range_padding = (pre_y_max - pre_y_min) * 0.20  # 20% padding for a taller view
            y_range_pre = [max(0, pre_y_min - y_range_padding), pre_y_max + y_range_padding]
        else:
            y_range_pre = None
        
        st.session_state.pre_plots = {
            'TUS_dist': create_distribution_plot(st.session_state.pre_scores, 'TUS'),
            'RUS_dist': create_distribution_plot(st.session_state.pre_scores, 'RUS'),
            'TUS_profile': create_thickness_profiles_plot(pre_filtered, st.session_state.pre_scores, 'TUS', target_mean_pre, y_range=y_range_pre),
            'RUS_profile': create_thickness_profiles_plot(pre_filtered, st.session_state.pre_scores, 'RUS', target_mean_pre, y_range=y_range_pre)
        }
        
        # Generate full HTML report with embedded interactive plots (INSTANT!)
        st.session_state.pre_report_html = generate_lot_analysis_report_html(
            "Pre-OL Thickness Report", st.session_state.pre_scores, 
            st.session_state.pre_plots, target_mean_pre, filename
        )
    else:
        st.session_state.pre_scores = pd.DataFrame()
        st.session_state.pre_plots = {}
        st.session_state.pre_report_html = ""

    # --- Post-OL ---
    post_df = df[df['condition'] == 'Post'].copy()
    if not post_df.empty:
        # For Post-OL data, use thickness_mm (already in microns, just rename)
        if 'thickness_mm' in post_df.columns:
            # Filter out empty/null thickness values first
            post_df = post_df[post_df['thickness_mm'].notna() & (post_df['thickness_mm'] != '')]
            post_df['thickness_um'] = pd.to_numeric(post_df['thickness_mm'], errors='coerce')  # Already in microns
            # Remove rows where conversion failed
            post_df = post_df[post_df['thickness_um'].notna()]
        else:
            st.error("Post-OL data requires 'thickness_mm' column")
            return
        st.session_state.post_scores = calculate_uniformity_scores(post_df, target_mean_post, _session_id=session_id)
        
        post_filtered = post_df[(post_df['position_mm'] >= 0.2) & (post_df['position_mm'] <= 0.8) & (post_df['thickness_um'] > 0)]
        if not post_filtered.empty:
            post_y_min = post_filtered['thickness_um'].min()
            post_y_max = post_filtered['thickness_um'].max()
            # Calculate dynamic range with tighter padding for better profile visibility
            y_range_padding = (post_y_max - post_y_min) * 0.05  # 5% padding for tighter view
            y_range_post = [max(0, post_y_min - y_range_padding), post_y_max + y_range_padding]
        else:
            y_range_post = None
        
        st.session_state.post_plots = {
            'TUS_dist': create_distribution_plot(st.session_state.post_scores, 'TUS'),
            'RUS_dist': create_distribution_plot(st.session_state.post_scores, 'RUS'),
            'TUS_profile': create_thickness_profiles_plot(post_filtered, st.session_state.post_scores, 'TUS', target_mean_post, y_range=y_range_post),
            'RUS_profile': create_thickness_profiles_plot(post_filtered, st.session_state.post_scores, 'RUS', target_mean_post, y_range=y_range_post)
        }
        
        # Generate full HTML report with embedded interactive plots (INSTANT!)
        st.session_state.post_report_html = generate_lot_analysis_report_html(
            "Post-OL Thickness Report", st.session_state.post_scores, 
            st.session_state.post_plots, target_mean_post, filename
        )
    else:
        st.session_state.post_scores = pd.DataFrame()
        st.session_state.post_plots = {}
        st.session_state.post_report_html = ""

    st.session_state.data_uploaded = True
    st.session_state.input_filename = filename
    st.success("Data processed successfully!") 
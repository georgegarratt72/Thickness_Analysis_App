import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

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
    all_categories = [
        "0.0 - 0.1", "0.1 - 0.2", "0.2 - 0.3", "0.3 - 0.4", "0.4 - 0.5", 
        "0.5 - 0.6", "0.6 - 0.7", "0.7 - 0.8", "0.8 - 0.9", "0.9 - 1.0"
    ]
    
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
            marker=dict(
                color=bar_colors,
                line=dict(color='black', width=1)  # Add black borders for solid look
            ),
            text=[f'{v}' for v in categories.values],
            textposition='outside',
            textfont=dict(size=12, color='black')
        )
    ])
    
    fig.update_layout(
        title=dict(
            text=f'{score_type} Score Distribution',
            font=dict(size=18, color='black'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text='Count', font=dict(size=14, color='black')),
            tickfont=dict(size=12, color='black'),
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1,
            showline=True,
            linecolor='black',
            linewidth=2
        ),
        yaxis=dict(
            title=dict(text=f'{score_type} Category', font=dict(size=14, color='black')),
            tickfont=dict(size=12, color='black'),
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1,
            showline=True,
            linecolor='black',
            linewidth=2
        ),
        height=500,  # Increased height for better visibility
        showlegend=False,
        margin=dict(l=120, r=60, t=80, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        transition_duration=0
    )
    
    return fig

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
    
    df_filtered = df[
        (df['position_mm'] >= 0.2) & 
        (df['position_mm'] <= 0.8) & 
        (df['thickness_um'] > 0)
    ].copy()
    
    category_col = f'{score_type}_category'
    df_plot = df_filtered.merge(
        scores_df[['sensor_id', category_col]], 
        on='sensor_id', 
        how='left'
    )
    
    categories = sorted(df_plot[category_col].dropna().unique(), reverse=True)
    
    # Handle case where no categories exist
    if len(categories) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for plotting",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            title=f'{score_type} Thickness Profiles by Category',
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    fig = make_subplots(
        rows=len(categories), 
        cols=1,
        subplot_titles=[f'{score_type}: {cat}' for cat in categories],
        vertical_spacing=0.08,
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
                    line=dict(color=colors[j % len(colors)], width=2),  # Thicker lines for solid look
                    marker=dict(size=6, line=dict(color='black', width=1)),  # Solid markers with borders
                    showlegend=False
                ),
                row=i+1, col=1
            )
        
        fig.add_trace(go.Scatter(x=[0.2, 0.8], y=[target_mean, target_mean], mode='lines', line=dict(color='red', dash='dash', width=3), hoverinfo='none', showlegend=False), row=i+1, col=1)
        fig.add_annotation(x=0.8, y=target_mean, text=f"Target: {target_mean} μm", showarrow=False, yshift=10, xanchor='right', row=i+1, col=1)
        fig.update_xaxes(title_text="Position (mm)", showticklabels=True, row=i+1, col=1)
        fig.update_yaxes(title_text="Thickness (μm)", showticklabels=True, row=i+1, col=1)
        
        # Apply tight y-axis range to each subplot individually
        if y_range:
            fig.update_yaxes(range=y_range, row=i+1, col=1)

    plot_height = max(400, 350 * len(categories))

    fig.update_layout(
        title=dict(
            text=f'{score_type} Thickness Profiles by Category',
            font=dict(size=18, color='black'),
            x=0.5,
            xanchor='center'
        ),
        height=plot_height,
        showlegend=False,
        margin=dict(l=80, r=40, t=100, b=60),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        transition_duration=0,
        template="plotly_white"
    )
    
    # Apply solid theme styling to all axes
    fig.update_xaxes(
        title_font=dict(size=14, color='black'),
        tickfont=dict(size=12, color='black'),
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1,
        zeroline=True,
        zerolinecolor='black',
        zerolinewidth=1,
        showline=True,
        linecolor='black',
        linewidth=2
    )
    
    fig.update_yaxes(
        title_font=dict(size=14, color='black'),
        tickfont=dict(size=12, color='black'),
        showgrid=True,
        gridcolor='lightgray',
        gridwidth=1,
        zeroline=False,
        showline=True,
        linecolor='black',
        linewidth=2
    )
    
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    return fig 
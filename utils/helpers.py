import pandas as pd
import base64
import datetime
import streamlit.components.v1 as components

def generate_simple_report_html(title, scores_data, target_mean, input_filename):
    """
    Generates a simple HTML report without plots.
    """
    if not isinstance(scores_data, pd.DataFrame) or scores_data.empty:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #D95D39; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
                <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            <div class="content">
                <h2>No Data Available</h2>
                <p>No analysis data was found for this report.</p>
            </div>
        </body>
        </html>
        """

    # Encode logo
    logo_base64 = ""
    try:
        with open("logo.png", "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        logo_base64 = ""

    # Calculate summary statistics
    total_sensors = len(scores_data)
    avg_tus = round(scores_data['TUS'].mean(), 3)
    avg_rus = round(scores_data['RUS'].mean(), 3)
    avg_thickness = round(scores_data['mean_thickness'].mean(), 1)

    # Create scores table HTML
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
                position: relative;
                background: linear-gradient(90deg, #D95D39, #4A0E1A);
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
                font-size: 2em;
                color: #D95D39;
                font-weight: 700;
            }}
            .section {{
                margin-bottom: 40px;
            }}
            .section h2 {{
                color: #4A0E1A;
                border-bottom: 2px solid #D95D39;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .styled-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                background-color: #FFFFFF;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .styled-table th {{
                background-color: #4A0E1A;
                color: #FFFFFF;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            .styled-table td {{
                padding: 12px;
                border-bottom: 1px solid #EAECEF;
            }}
            .styled-table tr:hover {{
                background-color: #F8F9FA;
            }}
            .footer {{
                text-align: center;
                color: #5A6474;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #EAECEF;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                {f'<img src="data:image/png;base64,{logo_base64}" alt="Logo" class="logo">' if logo_base64 else ''}
                <h1>{title}</h1>
                <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Sensors</h3>
                    <h2>{total_sensors}</h2>
                </div>
                <div class="metric-card">
                    <h3>Average Thickness</h3>
                    <h2>{avg_thickness} μm</h2>
                </div>
                <div class="metric-card">
                    <h3>Average TUS</h3>
                    <h2>{avg_tus}</h2>
                </div>
                <div class="metric-card">
                    <h3>Average RUS</h3>
                    <h2>{avg_rus}</h2>
                </div>
                <div class="metric-card">
                    <h3>Target Mean</h3>
                    <h2>{target_mean} μm</h2>
                </div>
            </div>

            <div class="section">
                <h2>📊 Detailed Results</h2>
                {scores_table_html}
            </div>

            <div class="footer">
                <p>Report generated from: {input_filename}</p>
                <p>Thickness Uniformity Analysis System</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def generate_lot_analysis_report_html(title, scores_data, plot_objects, target_mean, input_filename):
    """
    OPTIMIZED: Generates HTML report with embedded interactive plots (no image conversion needed).
    """
    if not isinstance(scores_data, pd.DataFrame) or scores_data.empty:
        return generate_simple_report_html(title, scores_data, target_mean, input_filename)

    # Encode logo
    logo_base64 = ""
    try:
        with open("logo.png", "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        logo_base64 = ""

    total_sensors = len(scores_data)
    avg_tus = round(scores_data['TUS'].mean(), 3)
    avg_rus = round(scores_data['RUS'].mean(), 3)
    avg_thickness = round(scores_data['mean_thickness'].mean(), 1)

    # OPTIMIZATION: Convert plots to HTML directly (no image conversion!)
    try:
        tus_dist_html = plot_objects.get('TUS_dist').to_html(include_plotlyjs='cdn', div_id='tus-dist-plot') if plot_objects.get('TUS_dist') else '<p>Chart not available</p>'
        rus_dist_html = plot_objects.get('RUS_dist').to_html(include_plotlyjs=False, div_id='rus-dist-plot') if plot_objects.get('RUS_dist') else '<p>Chart not available</p>'
        tus_profile_html = plot_objects.get('TUS_profile').to_html(include_plotlyjs=False, div_id='tus-profile-plot') if plot_objects.get('TUS_profile') else '<p>Chart not available</p>'
        rus_profile_html = plot_objects.get('RUS_profile').to_html(include_plotlyjs=False, div_id='rus-profile-plot') if plot_objects.get('RUS_profile') else '<p>Chart not available</p>'
    except Exception:
        # If plot conversion fails, fall back to simple report
        return generate_simple_report_html(title, scores_data, target_mean, input_filename)
    
    # Create scores table HTML
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
                position: relative;
                background: linear-gradient(90deg, #D95D39, #4A0E1A);
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
                font-size: 2em;
                color: #D95D39;
                font-weight: 700;
            }}
            .section {{
                margin-bottom: 40px;
            }}
            .section h2 {{
                color: #4A0E1A;
                border-bottom: 2px solid #D95D39;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .plot-container {{
                background-color: #FFFFFF;
                border: 1px solid #EAECEF;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }}
            .plot-container h3 {{
                margin: 0 0 15px 0;
                color: #4A0E1A;
                font-size: 1.3em;
            }}
            .styled-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
                background-color: #FFFFFF;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .styled-table th {{
                background-color: #4A0E1A;
                color: #FFFFFF;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            .styled-table td {{
                padding: 12px;
                border-bottom: 1px solid #EAECEF;
            }}
            .styled-table tr:hover {{
                background-color: #F8F9FA;
            }}
            .footer {{
                text-align: center;
                color: #5A6474;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #EAECEF;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                {f'<img src="data:image/png;base64,{logo_base64}" alt="Logo" class="logo">' if logo_base64 else ''}
                <h1>{title}</h1>
                <p>Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Sensors</h3>
                    <h2>{total_sensors}</h2>
                </div>
                <div class="metric-card">
                    <h3>Average Thickness</h3>
                    <h2>{avg_thickness} μm</h2>
                </div>
                <div class="metric-card">
                    <h3>Average TUS</h3>
                    <h2>{avg_tus}</h2>
                </div>
                <div class="metric-card">
                    <h3>Average RUS</h3>
                    <h2>{avg_rus}</h2>
                </div>
                <div class="metric-card">
                    <h3>Target Mean</h3>
                    <h2>{target_mean} μm</h2>
                </div>
            </div>

            <div class="section">
                <h2>📊 Score Distributions</h2>
                
                <div class="plot-container">
                    <h3>TUS Distribution</h3>
                    {tus_dist_html}
                </div>
                
                <div class="plot-container">
                    <h3>RUS Distribution</h3>
                    {rus_dist_html}
                </div>
            </div>

            <div class="section">
                <h2>📈 Thickness Profiles</h2>
                
                <div class="plot-container">
                    <h3>TUS Profiles</h3>
                    {tus_profile_html}
                </div>
                
                <div class="plot-container">
                    <h3>RUS Profiles</h3>
                    {rus_profile_html}
                </div>
            </div>

            <div class="section">
                <h2>📋 Detailed Results</h2>
                {scores_table_html}
            </div>

            <div class="footer">
                <p>Report generated from: {input_filename}</p>
                <p>Thickness Uniformity Analysis System</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def create_download_link_html(html_content, filename):
    """Generates a link to download the HTML report."""
    b64 = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
    filename = f"{filename.replace(' ', '_')}_{datetime.date.today().strftime('%Y%m%d')}.html"
    href = f'<a href="data:file/html;base64,{b64}" download="{filename}">Download Report</a>'
    return href 
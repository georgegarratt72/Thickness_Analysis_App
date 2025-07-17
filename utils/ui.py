import streamlit as st
import streamlit.components.v1 as components
import base64
from io import BytesIO

def load_custom_css():
    """Loads custom CSS for styling the application."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* --- Base Styles --- */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #F8F9FA;
            color: #333333;
        }

        /* --- Main Content Pane --- */
        .main, [data-testid="stAppViewContainer"] {
            overflow-y: auto; /* Allow scrolling on the main content pane */
            height: 100vh;
            scroll-behavior: auto; /* Changed from smooth to auto for better programmatic control */
            overscroll-behavior-y: contain; /* Prevent scrolling past the content */
        }

        h1, h2, h3, h4, h5, h6 {
            color: #4A0E1A;
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
            background: #D95D39;
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
            border-top: 4px solid #D95D39;
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
        background-color: #2A0813;
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
        color: #D95D39 !important;
        /* background-color: #FFFFFF !important; */
    }

    [data-testid="stSidebar"] [data-testid="stImage"] > img {
        width: 80%;
        margin: 0 auto;
        display: block;
    }

    /* --- Main UI Components --- */
    .main-header {
        background: linear-gradient(90deg, #D95D39, #4A0E1A);
        color: #FFFFFF;
        padding: 3rem;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(217, 93, 57, 0.3);
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: #FFFFFF;
        font-size: 2.5em;
        font-weight: 700;
    }

    /* Style for st.header */
    div[data-testid="stHeading"] > h2 {
        background: linear-gradient(90deg, #D95D39, #4A0E1A);
        color: #FFFFFF !important;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px 0 rgba(217, 93, 57, 0.2);
        margin-top: 1rem;
        margin-bottom: 1.5rem;
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
        justify-content: flex-start;
    }
    .feature-box:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.1);
    }
    .feature-box .icon {
        font-size: 3rem;
        color: #D95D39;
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
        color: #D95D39;
	}
	.stTabs [aria-selected="true"] {
		background-color: transparent;
        border-bottom: 2px solid #D95D39;
        color: #D95D39;
	}

    .stButton>button {
        border: 2px solid #D95D39;
        border-radius: 8px;
        background-color: #D95D39;
        color: white;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #C85030;
        color: white;
        border-color: #C85030;
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
        outline: 2px solid #D95D39;
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
    """, unsafe_allow_html=True)

def keyboard_shortcuts():
    """Renders the keyboard shortcuts help and the associated JavaScript."""
    st.markdown("""
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
    """, unsafe_allow_html=True)
    
    components.html("""
        <script>
            // Keyboard shortcuts
            document.addEventListener('keydown', function(event) {
                // Don't trigger when typing in input fields
                if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
                    return;
                }
                
                const shortcuts = window.parent.document.getElementById('keyboard-shortcuts');
                if (!shortcuts) return;

                switch(event.key) {
                    case '?':
                        shortcuts.classList.toggle('show');
                        break;
                    case 'Escape':
                        shortcuts.classList.remove('show');
                        break;
                }
            });
        </script>
    """, height=0)

def fig_to_base64(fig, width=800, height=None):
    """OPTIMIZED: Converts a Plotly figure to a base64 encoded string."""
    if fig is None:
        return ""
    
    try:
        import kaleido
    except ImportError:
        st.warning("Kaleido library not found. Please install it for full report generation: `pip install kaleido`")
        return ""
    
    try:
        buf = BytesIO()
        if height is None:
            height = fig.layout.height if fig.layout.height else 500  # Reduced from 600
        
        # OPTIMIZATION: Direct conversion without threading for better performance
        fig.write_image(buf, format="png", width=width, height=height, engine="kaleido")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
        
    except Exception as e:
        st.warning(f"Figure conversion failed: {e}. Report will be generated without this image.")
        return ""

def create_download_link_html(html_content, filename):
    """Generates a link to download the HTML report."""
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="{filename}">Download Report</a>'

def show_loading_overlay():
    """Displays a loading overlay."""
    st.markdown("""
        <div id="loading-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.8); display: flex; justify-content: center; align-items: center; z-index: 9999;">
            <div style="border: 4px solid #f3f3f3; border-top: 4px solid #D95D39; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite;"></div>
        </div>
        <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    """, unsafe_allow_html=True)

def hide_loading_overlay():
    """Hides the loading overlay."""
    st.markdown("""
        <script>
            var overlay = window.parent.document.getElementById('loading-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        </script>
    """, unsafe_allow_html=True) 

def scroll_to_top():
    """
    Minimal JavaScript scroll to top - targets document body and window.
    """
    components.html(
        """
        <script>
        // Try scrolling the parent document body
        if (parent.document.body) {
            parent.document.body.scrollTop = 0;
        }
        
        // Try scrolling the parent window
        if (parent.window) {
            parent.window.scrollTo(0, 0);
        }
        
        // Try scrolling the document element
        if (parent.document.documentElement) {
            parent.document.documentElement.scrollTop = 0;
        }
        </script>
        """,
        height=0
    )
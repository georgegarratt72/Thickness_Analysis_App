import streamlit as st
from streamlit_option_menu import option_menu
import warnings

from utils.ui import load_custom_css, keyboard_shortcuts
from views.welcome import render_welcome_page
from views.upload import render_upload_page
from views.analysis import render_analysis_dashboard
from views.help import render_help_page

warnings.filterwarnings('ignore')

# --- Page Configuration ---
st.set_page_config(
    page_title="Sava Lot Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Custom CSS and Keyboard Shortcuts ---
load_custom_css()
keyboard_shortcuts()

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
        'current_page': 'Welcome',
        'background_processing_started': False
    }
    for key, value in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

def main():
    """Main function to run the Streamlit application."""
    with st.sidebar:
        try:
            st.image("logo.png", use_container_width=True)
        except FileNotFoundError:
            st.markdown("<h1 style='color: white; text-align: center; font-size: 1.6em;'>SAVA</h1>", unsafe_allow_html=True)
        
        # Custom navigation with scroll-to-top functionality
        st.markdown("---")
        
        # Define navigation options
        nav_options = [
            ("🏠 Welcome", "Welcome"),
            ("☁️ Data Upload", "Data Upload"), 
            ("📏 Pre-OL Analysis", "Pre-OL Analysis"),
            ("📐 Post-OL Analysis", "Post-OL Analysis"),
            ("❓ Help", "Help")
        ]
        
        # Current page highlighting
        current_page = st.session_state.get('current_page', 'Welcome')
        
        # Create navigation buttons
        for display_name, page_key in nav_options:
            # Determine button style based on current page
            if current_page == page_key:
                button_type = "primary"
                use_container_width = True
            else:
                button_type = "secondary"
                use_container_width = True
            
            # Create button with unique key and handle click
            if st.button(display_name, key=f"nav_{page_key}", type=button_type, use_container_width=use_container_width):
                # Clear the current page from session state to force rebuild
                if 'current_page' in st.session_state:
                    del st.session_state['current_page']
                
                # Set the new page
                st.session_state.current_page = page_key
                
                # Add unique query parameter to force URL change
                import time
                st.query_params['t'] = str(int(time.time() * 1000))
                
                # Trigger immediate rerun
                st.rerun()
        
        page = st.session_state.current_page

    # --- Page Content ---
    # Force content rebuilding with empty container
    if 'page_container' not in st.session_state:
        st.session_state.page_container = st.empty()
    
    # Clear and rebuild page content
    st.session_state.page_container.empty()
    
    with st.session_state.page_container.container():
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
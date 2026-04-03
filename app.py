"""
GigShield AI - Main Streamlit Application Entry Point
Production-Grade Parametric Income Protection System
"""
import streamlit as st
st.set_page_config(
    page_title="GigShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.theme import apply_custom_theme
from config.database import verify_db_connection, init_collections

# Apply custom theme immediately
apply_custom_theme()

# Page configuration


def main():
    """Main app entry point."""
    # Initialize database
    try:
        if verify_db_connection():
            init_collections()
    except Exception as e:
        st.error(f"⚠️ Database connection: {str(e)}")
        st.info("The app will use in-memory data if MongoDB is unavailable.")

    # Sidebar navigation
    st.sidebar.title("🛡️ GigShield AI")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        ["📊 Dashboard", "👤 Registration", "📋 Policies", "📝 Claims", "📈 Analytics", "⚙️ Admin"]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### About
    **GigShield AI** - Parametric Income Protection for Gig Workers

    Automatic insurance claims powered by AI and environmental triggers.

    [Learn More →](https://github.com)
    """)

    # Route to appropriate page
    if page == "📊 Dashboard":
        from app_pages.dashboard import show
        show()
    elif page == "👤 Registration":
        from app_pages.registration import show
        show()
    elif page == "📋 Policies":
        from app_pages.policies import show
        show()
    elif page == "📝 Claims":
        from app_pages.claims import show
        show()
    elif page == "📈 Analytics":
        from app_pages.analytics import show
        show()
    elif page == "⚙️ Admin":
        from app_pages.admin import show
        show()


if __name__ == "__main__":
    main()

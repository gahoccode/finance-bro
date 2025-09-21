"""
Authentication UI Components

This module contains reusable UI components for authentication,
extracted from app.py to modularize authentication functionality
while preserving the exact same Streamlit built-in Google OAuth behavior.
"""

import streamlit as st


def render_login_screen():
    """
    Render the login screen with Google OAuth integration.

    This preserves the exact same UI and behavior as the original
    implementation in app.py lines 18-29, using Streamlit's built-in
    Google OAuth functionality.
    """
    st.title("🔒 Authentication Required")
    st.markdown("Please authenticate with Google to access Finance Bro")

    # Create a clean login interface - same as original
    st.button("Login with Google", on_click=st.login)

    # Show helpful information - same as original
    st.markdown("---")
    st.info("After logging in, you'll be redirected back to the app automatically.")

    # Stop execution until user is authenticated - same as original
    st.stop()


def render_logout_button():
    """
    Render logout button for sidebar.

    This preserves the exact same logout functionality as the original
    implementation in app.py lines 292-293, using Streamlit's built-in
    logout functionality.
    """
    if st.button("🚪 Logout", use_container_width=True):
        st.logout()


def is_user_logged_in() -> bool:
    """
    Check if user is currently logged in using Streamlit's built-in user object.

    Returns:
        bool: True if user is logged in, False otherwise
    """
    try:
        return hasattr(st, 'user') and st.user.is_logged_in
    except AttributeError:
        # Handle case when running outside Streamlit context (e.g., tests)
        return False


"""
Authentication Service

This module provides centralized authentication state management
while preserving the exact same Streamlit built-in Google OAuth behavior.
Allows enabling/disabling authentication via configuration.
"""

import os
from src.components.auth_components import render_login_screen, is_user_logged_in


def is_authentication_enabled() -> bool:
    """
    Check if authentication is enabled based on environment configuration.

    Returns:
        bool: True if authentication is enabled, False otherwise
    """
    return os.getenv("AUTH_ENABLED", "true").lower() == "true"


def is_authentication_required() -> bool:
    """
    Check if authentication is required for the current user.

    This preserves the exact same logic as the original app.py:
    Authentication is required when:
    1. Authentication is enabled (AUTH_ENABLED=true)
    2. AND user is not logged in (not st.user.is_logged_in)

    Returns:
        bool: True if authentication is required, False otherwise
    """
    if not is_authentication_enabled():
        return False

    return not is_user_logged_in()


def handle_authentication():
    """
    Handle the authentication flow.

    This preserves the exact same behavior as the original app.py:
    - If authentication is required, render login screen and stop execution
    - If authentication is disabled or user is logged in, continue normally

    The login screen uses the same st.login() functionality and UI.
    """
    if is_authentication_required():
        render_login_screen()  # This will call st.stop() internally


def get_authentication_status() -> dict:
    """
    Get current authentication status information.

    Returns:
        dict: Authentication status with keys:
            - enabled: Whether authentication is enabled
            - required: Whether authentication is currently required
            - logged_in: Whether user is currently logged in
    """
    return {
        "enabled": is_authentication_enabled(),
        "required": is_authentication_required(),
        "logged_in": is_user_logged_in()
    }


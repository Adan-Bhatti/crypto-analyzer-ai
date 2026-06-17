"""
Page 8 — Admin Panel
====================
Provides user generation capabilities for admin users.
"""
from __future__ import annotations

import streamlit as st

from services.db_service import DBService
from utils.logger import get_logger

logger = get_logger(__name__)

def render_page() -> None:
    """Render the Admin Panel."""
    st.markdown(
        "<h2 style='color: #00D4AA;'>🛡️ Admin Panel</h2>",
        unsafe_allow_html=True,
    )

    db = DBService()
    
    # Check if current user is admin
    user_info = st.session_state.get("user_info", {})
    if not user_info.get("is_admin", False):
        st.error("🚫 Access Denied: You do not have admin privileges.")
        return

    st.write("Welcome to the Admin Panel. Here you can generate new users.")

    st.markdown("---")
    st.subheader("Create New User")

    with st.form("create_user_form"):
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        is_admin = st.checkbox("Grant Admin Privileges")
        submit_btn = st.form_submit_button("Create User")

        if submit_btn:
            if not new_username or not new_password:
                st.warning("Please provide both a username and a password.")
            else:
                success = db.create_user(new_username, new_password, is_admin)
                if success:
                    st.success(f"User '{new_username}' created successfully!")
                else:
                    st.error("Failed to create user. The username might already exist.")

    st.markdown("---")
    st.subheader("Existing Users")
    
    users = db.get_all_users()
    if users:
        import pandas as pd
        df = pd.DataFrame(users)
        # Format the dataframe display
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No users found.")

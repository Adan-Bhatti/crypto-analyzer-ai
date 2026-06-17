"""
CryptoAI Analyzer — Streamlit Entry Point
============================================
Main application entry point. Configures the page, renders the sidebar
navigation, and routes to the appropriate page module.

Run with::

    streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Ensure the project root is on the Python path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from utils.config import PAGE_LABELS


# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="CryptoAI Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# Custom CSS for Global Styling
# =============================================================================

st.markdown(
    """
    <style>
        /* Hide the Streamlit Cloud toolbar/header */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stApp > header {visibility: hidden;}
        .stDeployButton {display:none;}

        /* Dark background override */
        .stApp {
            background-color: #0E1117;
        }

        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #0a0a1a;
            border-right: 1px solid #222;
        }

        /* Metric card styling */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border: 1px solid #333;
            border-radius: 12px;
            padding: 16px;
        }

        /* Button styling */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #00D4AA, #00B894);
            border: none;
            color: #000;
            font-weight: 600;
        }

        /* Dataframe styling */
        .stDataFrame {
            border-radius: 8px;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab"] {
            color: #aaa;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #00D4AA;
        }

        /* Hide the default Streamlit menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================================================================
# Authentication Gate
# =============================================================================

from services.db_service import DBService
db = DBService()

import extra_streamlit_components as stx

def get_cookie_manager():
    if "cookie_manager" in st.session_state:
        return st.session_state.cookie_manager
    cookie_manager = stx.CookieManager(key="cookie_manager_comp")
    st.session_state.cookie_manager = cookie_manager
    return cookie_manager

cookie_manager = get_cookie_manager()

# Try to load user from cookie
if "user_info" not in st.session_state or st.session_state["user_info"] is None:
    cookie_token = cookie_manager.get(cookie="auth_token")
    if cookie_token:
        # For simplicity, token is just username here. In prod, use JWT.
        user_info = db.get_user_by_username(cookie_token)
        if user_info:
            st.session_state["user_info"] = user_info

if not st.session_state.get("user_info"):
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='background-color: #1a1a2e; padding: 2rem; border-radius: 12px; border: 1px solid #333; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>
                <h1 style='color: #00D4AA; margin-bottom: 0;'>CryptoAI</h1>
                <p style='color: #aaa; margin-top: 5px; font-size: 1.1rem;'>Please sign in to access your dashboard</p>
            </div>
            <br>
            """,
            unsafe_allow_html=True
        )
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                user_info = db.authenticate_user(username, password)
                if user_info:
                    st.session_state["user_info"] = user_info
                    # Save token to cookie
                    cookie_manager.set("auth_token", username, expires_at=None)
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")
    st.stop()

# =============================================================================
# Sidebar Navigation
# =============================================================================

from frontend.components.sidebar import render_sidebar

sidebar_config = render_sidebar()

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["user_info"] = None
    cookie_manager.delete("auth_token")
    if "page" in st.query_params:
        del st.query_params["page"]
    st.rerun()

# =============================================================================
# Navigation Router
# =============================================================================

nav_options = list(PAGE_LABELS)
if st.session_state["user_info"].get("is_admin", False):
    nav_options.append("Admin Panel")
else:
    # Restrict Project Overview and Model Performance to admins only
    if PAGE_LABELS[0] in nav_options:
        nav_options.remove(PAGE_LABELS[0])
    
    # Model Performance is the last item (PAGE_LABELS[7] usually)
    for label in list(nav_options):
        if "Model Performance" in label:
            nav_options.remove(label)

# Parse query params for page sync
query_page = st.query_params.get("page", PAGE_LABELS[0])

# Ensure query_page is valid for the current user's role
try:
    default_index = next(i for i, v in enumerate(nav_options) if query_page in v)
except StopIteration:
    default_index = 0

# Page selection via sidebar radio
selected_page = st.sidebar.radio(
    "Navigate",
    nav_options,
    index=default_index,
    key="main_navigation",
    label_visibility="collapsed",
)

# Update query param
st.query_params["page"] = selected_page


# =============================================================================
# Handle "Run Analysis" from Sidebar
# =============================================================================

if sidebar_config["run_analysis"]:
    from backend.pipeline import CryptoPipeline

    with st.spinner("🔄 Running analysis pipeline... This may take a moment."):
        try:
            # Get or create pipeline instance
            if "pipeline_instance" not in st.session_state:
                st.session_state["pipeline_instance"] = CryptoPipeline()

            pipeline = st.session_state["pipeline_instance"]

            # Determine data source and run pipeline
            if sidebar_config["data_source"] == "csv" and sidebar_config["csv_file"] is not None:
                # Save uploaded CSV to a temp location
                import tempfile
                import os

                temp_dir = PROJECT_ROOT / "data" / "sample"
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_path = str(temp_dir / "uploaded_data.csv")

                with open(temp_path, "wb") as f:
                    f.write(sidebar_config["csv_file"].getvalue())

                result = pipeline.run_full_pipeline(
                    symbol=sidebar_config["symbol"],
                    data_source="csv",
                    csv_path=temp_path,
                    retrain=sidebar_config["retrain"],
                )
            else:
                result = pipeline.run_full_pipeline(
                    symbol=sidebar_config["symbol"],
                    data_source="api",
                    retrain=sidebar_config["retrain"],
                )

            # Store result in session state
            st.session_state["pipeline_result"] = result

            # Initialize DBService
            from services.db_service import DBService
            import datetime
            db = DBService()

            # Track prediction history
            if result.prediction:
                db.insert_prediction({
                    "user_id": st.session_state["user_info"]["id"],
                    "symbol": sidebar_config.get("symbol", "UNKNOWN"),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "bullish_prob": result.prediction.bullish_prob,
                    "bearish_prob": result.prediction.bearish_prob,
                    "rf_prediction": result.prediction.rf_prediction,
                    "lr_prediction": result.prediction.lr_prediction,
                    "xgb_prediction": getattr(result.prediction, "xgb_prediction", 0)
                })

            # Track recommendation history
            if result.recommendation:
                rec = result.recommendation
                db.insert_recommendation({
                    "user_id": st.session_state["user_info"]["id"],
                    "symbol": sidebar_config.get("symbol", "UNKNOWN"),
                    "timestamp": rec.timestamp.isoformat(),
                    "action": rec.action,
                    "confidence": rec.confidence,
                    "bullish_prob": rec.bullish_prob,
                    "bearish_prob": rec.bearish_prob,
                    "risk_level": rec.risk_level,
                    "stop_loss": rec.suggested_stop_loss,
                    "take_profit": rec.suggested_take_profit,
                })

            if result.errors:
                for error in result.errors:
                    st.error(f"❌ {error}")
            else:
                st.success("✅ Analysis completed successfully!")

            if result.warnings:
                for warning in result.warnings:
                    st.warning(f"⚠️ {warning}")

        except Exception as exc:
            st.error(f"❌ Analysis failed: {exc}")


# =============================================================================
# =============================================================================
# Page Routing
# =============================================================================

if "Project Overview" in selected_page:
    from frontend.pages.page_overview import render_page
    render_page()

elif "Live Market Dashboard" in selected_page:
    from frontend.pages.page_live_market import render_page
    render_page()

elif "Historical Analysis" in selected_page:
    from frontend.pages.page_historical import render_page
    render_page()

elif "Prediction Dashboard" in selected_page:
    from frontend.pages.page_prediction import render_page
    render_page()

elif "Risk Classification" in selected_page:
    from frontend.pages.page_risk import render_page
    render_page()

elif "Buy/Sell/Hold Engine" in selected_page:
    from frontend.pages.page_recommendation import render_page
    render_page()

elif "Personal History" in selected_page:
    from frontend.pages.page_history import render_page
    render_page()

elif "Model Performance" in selected_page:
    from frontend.pages.page_performance import render_page
    render_page()

elif selected_page == "Admin Panel":
    from frontend.pages.page_admin import render_page
    render_page()

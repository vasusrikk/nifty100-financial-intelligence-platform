"""NIFTY 100 Analytics - Streamlit dashboard entry point."""

from __future__ import annotations

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# NAVIGATION
# ============================================================

PAGES = {
    "Dashboard": [
        st.Page(
            "pages/01_home.py",
            title="Home",
            icon="🏠",
            default=True,
        ),
        st.Page(
            "pages/02_profile.py",
            title="Company Profile",
            icon="🏢",
        ),
        st.Page(
            "pages/03_screener.py",
            title="Screener",
            icon="🔎",
        ),
        st.Page(
            "pages/04_peers.py",
            title="Peer Comparison",
            icon="⚖️",
        ),
        st.Page(
            "pages/05_trends.py",
            title="Trend Analysis",
            icon="📈",
        ),
        st.Page(
            "pages/06_sectors.py",
            title="Sector Analysis",
            icon="🧩",
        ),
        st.Page(
            "pages/07_capital.py",
            title="Capital Allocation",
            icon="🗺️",
        ),
        st.Page(
            "pages/08_reports.py",
            title="Annual Reports",
            icon="📄",
        ),
    ]
}


navigation = st.navigation(
    PAGES,
    position="sidebar",
    expanded=True,
)

navigation.run()
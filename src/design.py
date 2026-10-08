"""UI configuration and styling for the Streamlit chatbot."""

import streamlit as st


PAGE_TITLE = "Knowledge Base Chatbot"
PAGE_ICON = "🤖"


_CUSTOM_CSS = """
<style>
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
</style>
"""


def configure_page() -> None:
    """Configure the Streamlit page."""

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="centered",
    )

    st.markdown(
        _CUSTOM_CSS,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the chatbot page heading."""

    st.title(f"{PAGE_ICON} {PAGE_TITLE}")

    st.caption(
        "Ask questions about accounts, projects, revenue, proposals, "
        "and other information in the internal knowledge base."
    )
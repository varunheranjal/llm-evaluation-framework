"""Streamlit UI for the internal RAG chatbot."""

import logging
import sys
import uuid
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


import streamlit as st

from src.agents import ask_with_tools
from src.design import configure_page, render_header


logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 20


configure_page()
render_header()


def _new_session_id() -> str:
    """Create a unique conversation session ID."""

    return f"chatbot-{uuid.uuid4()}"


def _initialise_session() -> None:
    """Initialise Streamlit session state."""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "session_id" not in st.session_state:
        st.session_state.session_id = _new_session_id()


def _clear_conversation() -> None:
    """Reset the conversation and create a new trace session."""

    st.session_state.messages = []
    st.session_state.session_id = _new_session_id()


def _build_chat_history() -> list[dict[str, str]]:
    """Return recent conversation history for the agent."""

    messages = st.session_state.messages[-MAX_HISTORY_MESSAGES:]

    return [
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in messages
    ]


_initialise_session()


with st.sidebar:

    st.subheader("Chat")

    if st.button(
        "Clear conversation",
        use_container_width=True,
    ):
        _clear_conversation()
        st.rerun()


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":

            retrieval_count = message.get("retrieval_count", 0)
            tool_names = message.get("tool_names", [])

            if retrieval_count or tool_names:

                with st.expander("Debug information"):

                    if tool_names:
                        st.write(
                            "Tools used:",
                            ", ".join(tool_names),
                        )

                    if retrieval_count:
                        st.write(
                            f"Retrieved chunks: {retrieval_count}"
                        )


user_question = st.chat_input(
    "Ask a question about the knowledge base..."
)


if user_question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_question)

    history = _build_chat_history()[:-1]

    try:

        with st.chat_message("assistant"):

            with st.spinner("Searching knowledge base..."):

                response = ask_with_tools(
                    question=user_question,
                    chat_history=history,
                    session_id=st.session_state.session_id,
                )

            st.markdown(response.answer)

            if response.tool_names or response.retrieval_context:

                with st.expander("Debug information"):

                    if response.tool_names:
                        st.write(
                            "Tools used:",
                            ", ".join(response.tool_names),
                        )

                    if response.retrieval_context:
                        st.write(
                            f"Retrieved chunks: "
                            f"{len(response.retrieval_context)}"
                        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response.answer,
                "tool_names": response.tool_names,
                "retrieval_count": len(response.retrieval_context),
            }
        )

    except Exception:

        logger.exception(
            "Failed to answer chatbot question."
        )

        error_message = (
            "Sorry, I couldn't process that request. "
            "Please try again."
        )

        with st.chat_message("assistant"):
            st.error(error_message)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )
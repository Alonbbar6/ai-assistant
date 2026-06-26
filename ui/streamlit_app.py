"""
Streamlit GUI for the Personal AI Assistant.
Run with: streamlit run ui/streamlit_app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stChatMessage { padding: 0.5rem 0; }
    div[data-testid="stStatusWidget"] { display: none; }
    .nav-btn button {
        background: transparent !important;
        border: 1px solid #333 !important;
        text-align: left !important;
    }
    .nav-btn button:hover {
        border-color: #666 !important;
        background: #1a1a2e !important;
    }
    .active-nav button {
        background: #1e3a5f !important;
        border-color: #4a7fb5 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "assistant" not in st.session_state:
        from core.agent import PersonalAssistant
        st.session_state.assistant = PersonalAssistant()
    if "sidebar_view" not in st.session_state:
        st.session_state.sidebar_view = "home"
    if "sidebar_data" not in st.session_state:
        st.session_state.sidebar_data = None


init_state()


def set_view(view: str, data=None):
    st.session_state.sidebar_view = view
    st.session_state.sidebar_data = data
    st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🤖 AI Assistant")
    st.caption("Powered by Claude")
    st.divider()

    view = st.session_state.sidebar_view

    # ── Back button (shown on all non-home views) ──
    if view != "home":
        if st.button("← Back to menu", use_container_width=True):
            set_view("home")
        st.divider()

    # ── HOME MENU ──────────────────────────────────
    if view == "home":
        st.subheader("Tools")

        if st.button("📄  Documents & Q&A", use_container_width=True):
            set_view("documents")

        if st.button("📅  Calendar", use_container_width=True):
            set_view("calendar")

        if st.button("📧  Email", use_container_width=True):
            set_view("email")

        if st.button("🔍  File Search", use_container_width=True):
            set_view("files")

        st.divider()
        if st.button("🗑️  Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.assistant.reset()
            st.rerun()

        st.caption("v1.0 · Personal AI Assistant")

    # ── DOCUMENTS VIEW ─────────────────────────────
    elif view == "documents":
        st.subheader("📄 Documents & Q&A")
        st.caption("Upload a file to index it, then ask questions about it in the chat.")

        uploaded = st.file_uploader(
            "Upload file to index",
            type=["pdf", "txt", "md", "py", "csv", "json"],
        )
        if uploaded:
            tmp_path = Path(f"/tmp/{uploaded.name}")
            tmp_path.write_bytes(uploaded.read())
            with st.spinner(f"Indexing {uploaded.name}..."):
                from rag.document_store import index_document
                result = index_document(str(tmp_path))
            st.success(result)
            st.info('Now ask in the chat: "What does this document say about X?"')

        st.divider()
        st.caption("**Indexed documents:**")
        from rag.document_store import list_indexed_documents
        docs = list_indexed_documents()
        if docs:
            for d in docs:
                st.caption(f"• {Path(d).name}")
        else:
            st.info("No documents indexed yet.")

    # ── CALENDAR VIEW ──────────────────────────────
    elif view == "calendar":
        st.subheader("📅 Calendar")

        days = st.slider("Days ahead", 1, 60, 7)
        if st.button("🔄 Refresh", use_container_width=True):
            with st.spinner("Fetching events..."):
                try:
                    from tools.calendar_tool import list_events
                    st.session_state.sidebar_data = list_events(days_ahead=days)
                except Exception as ex:
                    st.error(f"Calendar error: {ex}")
                    st.session_state.sidebar_data = []

        events = st.session_state.sidebar_data
        if events is None:
            # Auto-load on first open
            with st.spinner("Fetching events..."):
                try:
                    from tools.calendar_tool import list_events
                    events = list_events(days_ahead=days)
                    st.session_state.sidebar_data = events
                except Exception as ex:
                    st.error(f"Calendar error: {ex}")
                    events = []

        if events:
            for e in events:
                start = e["start"][:16].replace("T", " ")
                st.markdown(f"**{e['title']}**")
                st.caption(f"🕐 {start}")
                if e.get("location"):
                    st.caption(f"📍 {e['location']}")
                st.divider()
        else:
            st.info("No upcoming events.")

        st.caption('Tip: use the chat to create or delete events.')

    # ── EMAIL VIEW ─────────────────────────────────
    elif view == "email":
        st.subheader("📧 Email")

        col1, col2 = st.columns([2, 1])
        with col1:
            query = st.text_input("Search", placeholder="from:boss@company.com", label_visibility="collapsed")
        with col2:
            count = st.selectbox("Show", [5, 10, 20], label_visibility="collapsed")

        if st.button("🔄 Refresh", use_container_width=True):
            with st.spinner("Loading emails..."):
                try:
                    from tools.email_tool import list_emails
                    st.session_state.sidebar_data = list_emails(max_results=count, query=query)
                except Exception as ex:
                    st.error(f"Email error: {ex}")

        emails = st.session_state.sidebar_data
        if emails is None:
            with st.spinner("Loading emails..."):
                try:
                    from tools.email_tool import list_emails
                    emails = list_emails(max_results=count)
                    st.session_state.sidebar_data = emails
                except Exception as ex:
                    st.error(f"Email error: {ex}")
                    emails = []

        if emails:
            for e in emails:
                st.markdown(f"**{e['subject'] or '(no subject)'}**")
                st.caption(f"From: {e['from']}")
                st.caption(e["snippet"][:120])
                st.divider()
        else:
            st.info("No emails found.")

        st.caption('Tip: use the chat to send emails.')

    # ── FILE SEARCH VIEW ───────────────────────────
    elif view == "files":
        st.subheader("🔍 File Search")

        query = st.text_input("Filename", placeholder="resume.pdf")
        ext = st.selectbox("Type", ["Any", ".pdf", ".txt", ".md", ".py", ".csv", ".docx"])

        if query:
            from tools.file_search import search_files
            ext_filter = None if ext == "Any" else ext
            results = search_files(query, extension=ext_filter)
            if results:
                st.caption(f"{len(results)} file(s) found:")
                for r in results:
                    st.markdown(f"**{r['name']}**")
                    st.caption(f"`{r['path']}`  \n{r['size_kb']} KB · {r['modified']}")
                    if st.button("Ask about this file", key=r["path"]):
                        st.session_state._quick_prompt = f"Read and summarize the file at {r['path']}"
                        set_view("home")
            else:
                st.info("No files found.")


# ── Main chat area ────────────────────────────────────────────────────────────
st.header("Chat")

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        if msg["role"] == "assistant" and msg.get("tools_used"):
            with st.expander(f"🔧 Used tools: {', '.join(msg['tools_used'])}", expanded=False):
                st.caption("The assistant called these tools to answer your question.")
        st.markdown(msg["content"])

# Suggested prompts (only on empty chat)
if not st.session_state.messages:
    st.markdown("**Try asking:**")
    cols = st.columns(2)
    suggestions = [
        ("📅 What's on my calendar this week?", "What's on my calendar this week?"),
        ("📧 Show my recent emails", "Show my recent emails"),
        ("🔍 Find PDFs on my computer", "Find PDF files on my computer"),
        ("❓ How can you help me?", "What can you help me with?"),
    ]
    for i, (label, prompt) in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(label, use_container_width=True, key=f"suggestion_{i}"):
                st.session_state._quick_prompt = prompt
                st.rerun()

# Handle quick prompt from suggestion buttons or file search
quick_prompt = st.session_state.pop("_quick_prompt", None)

# Chat input
user_input = st.chat_input("Ask me anything — search files, manage calendar, send emails...")

if user_input or quick_prompt:
    prompt = quick_prompt or user_input

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                tools_used = []
                import core.agent as agent_module
                original_dispatch = agent_module._dispatch_tool

                def tracked_dispatch(name, inputs):
                    tools_used.append(name)
                    return original_dispatch(name, inputs)

                agent_module._dispatch_tool = tracked_dispatch
                response = st.session_state.assistant.chat(prompt)
                agent_module._dispatch_tool = original_dispatch

            except Exception as e:
                response = f"Sorry, I encountered an error: {e}"
                tools_used = []

        if tools_used:
            with st.expander(f"🔧 Used tools: {', '.join(set(tools_used))}", expanded=False):
                st.caption("The assistant called these tools to answer your question.")

        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "tools_used": list(set(tools_used)) if tools_used else [],
    })

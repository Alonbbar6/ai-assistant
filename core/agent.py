"""
Main agent loop using Claude tool-use API.
Each tool maps to a real capability (files, PDFs, RAG, calendar, email, voice).
"""

import json
from typing import Any

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from core.memory import ConversationMemory

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ── Tool definitions sent to Claude ──────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "search_files",
        "description": "Search for files on the user's computer by name. Returns a list of matching files with paths.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Filename pattern to search for"},
                "directory": {"type": "string", "description": "Optional: specific directory to search in"},
                "extension": {"type": "string", "description": "Optional: file extension filter, e.g. '.pdf'"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "read_file",
        "description": "Read the text content of a file (text, markdown, code, etc.)",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the file"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_pdf",
        "description": "Extract and return the text content of a PDF file. Use this to summarize or analyze PDF documents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the PDF file"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "index_document",
        "description": "Index a document (PDF or text file) for future semantic search queries. Call this before using query_documents on a new file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to the document to index"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "query_documents",
        "description": "Semantic search over previously indexed documents. Use to answer questions about document content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "The question or topic to search for"},
                "top_k": {"type": "integer", "description": "Number of passages to return (default 5)", "default": 5},
            },
            "required": ["question"],
        },
    },
    {
        "name": "list_indexed_documents",
        "description": "List all documents currently indexed in the knowledge base.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_calendar_events",
        "description": "List upcoming Google Calendar events.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "How many days ahead to look (default 7)"},
                "max_results": {"type": "integer", "description": "Max events to return (default 15)"},
            },
        },
    },
    {
        "name": "create_calendar_event",
        "description": "Create a new Google Calendar event.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "description": "ISO 8601 datetime, e.g. 2026-07-01T10:00:00-05:00"},
                "end": {"type": "string", "description": "ISO 8601 datetime"},
                "description": {"type": "string"},
                "location": {"type": "string"},
                "attendees": {"type": "array", "items": {"type": "string"}, "description": "List of email addresses"},
            },
            "required": ["title", "start", "end"],
        },
    },
    {
        "name": "delete_calendar_event",
        "description": "Delete a Google Calendar event by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string"},
            },
            "required": ["event_id"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an email via Gmail.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "list_emails",
        "description": "List recent emails from Gmail inbox.",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Number of emails to return"},
                "query": {"type": "string", "description": "Gmail search query, e.g. 'from:boss@company.com'"},
            },
        },
    },
]

SYSTEM_PROMPT = """You are a capable personal AI assistant running locally on the user's computer.
You can search and read files, summarize PDFs, answer questions about documents using RAG,
manage Google Calendar events, send/read emails via Gmail, and engage in conversation.

When helping with documents: search for the file first, then read or index it as appropriate.
When asked to index a document for Q&A, always call index_document first, then query_documents.
Be concise, accurate, and proactively helpful. Always confirm before deleting events or sending emails.
Today's date: {date}
"""


def _dispatch_tool(name: str, inputs: dict) -> Any:
    """Route a tool call to the correct implementation."""
    from tools.file_search import search_files, read_text_file
    from tools.pdf_tool import extract_pdf_text
    from rag.document_store import index_document, query_documents, list_indexed_documents
    from tools.calendar_tool import list_events, create_event, delete_event
    from tools.email_tool import send_email, list_emails

    match name:
        case "search_files":
            return search_files(**inputs)
        case "read_file":
            return read_text_file(inputs["path"])
        case "read_pdf":
            return extract_pdf_text(inputs["path"])
        case "index_document":
            return index_document(inputs["path"])
        case "query_documents":
            return query_documents(inputs["question"], inputs.get("top_k", 5))
        case "list_indexed_documents":
            return list_indexed_documents()
        case "list_calendar_events":
            return list_events(inputs.get("days_ahead", 7), inputs.get("max_results", 15))
        case "create_calendar_event":
            return create_event(**inputs)
        case "delete_calendar_event":
            return delete_event(inputs["event_id"])
        case "send_email":
            return send_email(**inputs)
        case "list_emails":
            return list_emails(inputs.get("max_results", 10), inputs.get("query", ""))
        case _:
            return f"Unknown tool: {name}"


class PersonalAssistant:
    def __init__(self):
        self.memory = ConversationMemory(max_turns=20)

    def chat(self, user_message: str) -> str:
        """Send a message and return the assistant's response (handles tool loops)."""
        import datetime
        self.memory.add("user", user_message)

        system = SYSTEM_PROMPT.format(date=datetime.date.today().isoformat())
        messages = self.memory.history()

        while True:
            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=4096,
                system=system,
                tools=TOOLS,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                text = next(
                    (b.text for b in response.content if hasattr(b, "text")), ""
                )
                self.memory.add("assistant", response.content)
                return text

            if response.stop_reason == "tool_use":
                # Execute all tool calls in this response
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = _dispatch_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": json.dumps(result, default=str, ensure_ascii=False),
                        })

                # Add assistant turn + tool results, then loop
                messages = messages + [
                    {"role": "assistant", "content": response.content},
                    {"role": "user", "content": tool_results},
                ]
            else:
                break

        return "[No response]"

    def reset(self) -> None:
        self.memory.clear()

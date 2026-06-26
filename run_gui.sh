#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
streamlit run ui/streamlit_app.py --server.port 8501

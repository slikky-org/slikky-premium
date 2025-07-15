#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Open browser in new window
open -n -a "Google Chrome" http://localhost:8501

# Start Streamlit with browser auto-opening
streamlit run voedingsadvies.py --server.headless true --browser.serverAddress localhost --browser.serverPort 8501 
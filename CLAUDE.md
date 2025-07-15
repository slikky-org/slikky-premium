# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SLIKKY® Premium is a Streamlit-based web application for healthcare professionals to generate nutritional advice based on IDDSI (International Dysphagia Diet Standardisation Initiative) levels. The application serves Dutch-speaking healthcare professionals in rehabilitation centers, nursing homes, and hospitals.

## Key Commands

### Development
```bash
# Activate virtual environment and run the app
./start.sh

# Or manually:
source venv/bin/activate
streamlit run voedingsadvies.py

# Install dependencies
pip install -r requirements.txt
```

### Deployment
- The app is deployed on Streamlit Cloud at: https://slikky-premium-v1.streamlit.app
- Main application file: `voedingsadvies.py`

## Architecture Overview

### Application Flow
1. **Authentication**: Users log in with email/password against a MySQL database (db4free.net)
2. **Form Input**: Healthcare professionals fill out client details, IDDSI levels, and dietary restrictions
3. **AI Processing**: Constructs prompts and sends to OpenAI API for advice generation
4. **Output**: Displays nutritional advice on screen; premium users can export to PDF
5. **Usage Tracking**: Logs usage to local CSV file

### Key Components
- **Frontend**: Streamlit UI with session state management
- **Authentication**: MySQL-based user verification with role differentiation (premium/standard)
- **AI Integration**: OpenAI API for generating personalized nutritional recommendations
- **PDF Generation**: ReportLab for creating formatted PDF exports (premium feature)
- **IDDSI Framework**: Supports both solid (levels 3-7) and liquid (levels 0-4) consistency levels

### Security Considerations
- Environment variables should be used for API keys and database credentials (via python-dotenv)
- User passwords are stored in plaintext in the database (consider hashing)
- API usage is tracked per user with monthly limits

### Database Schema
The MySQL database contains a `users` table with:
- email (primary identifier)
- password
- subscription_status (premium/standard)
- usage statistics fields

## Development Notes

- No test suite exists currently
- No linting or formatting configuration
- The app uses Dutch language throughout the UI
- Images are stored in the `images/` directory
- Alternative version exists in `app1_prompt_1_v2_met_footer_definitief.py`
#!/bin/bash

# Create .streamlit directory if it doesn't exist
mkdir -p ~/.streamlit/

# Create required application directories for runtime data
# These directories are needed for the app to store:
# - cache/: Stock data and API response caching
# - exports/: Generated charts and reports
# - outputs/: Additional output files
mkdir -p cache exports/charts exports/reports exports/tearsheets outputs

# Generate Streamlit config.toml for production
echo "\
[server]\n\
headless = true\n\
port = \$PORT\n\
address = \"0.0.0.0\"\n\
enableCORS = false\n\
enableXsrfProtection = true\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
" > ~/.streamlit/config.toml

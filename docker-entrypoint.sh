#!/bin/bash
set -e

# Default service type is backend if not specified
SERVICE_TYPE="${SERVICE_TYPE:-backend}"

if [ "$SERVICE_TYPE" = "backend" ]; then
    echo "Starting FastAPI Backend..."
    exec uvicorn src.main:app --host 0.0.0.0 --port 8000
elif [ "$SERVICE_TYPE" = "frontend" ]; then
    echo "Starting Streamlit Frontend..."
    exec streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
else
    echo "Error: SERVICE_TYPE must be set to either 'backend' or 'frontend' (currently: '$SERVICE_TYPE')"
    exit 1
fi

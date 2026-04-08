"""
API Key configuration for Google Gemini
"""
import os

# Get the API key only from environment variable.
# Do not keep hardcoded fallback keys in source control.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
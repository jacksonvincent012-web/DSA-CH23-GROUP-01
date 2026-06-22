"""
Vercel serverless entry point.
Sets SERVERLESS=1 so the simulator thread is skipped,
then delegates all /api/* requests to the Flask app.
"""
import os
import sys

os.environ['SERVERLESS'] = '1'

# Add backend/ to path so 'structures' and 'api' imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from api.server import app  # noqa: F401 — Vercel needs the name 'app'

# Vercel expects a callable named 'handler' or the module-level 'app'
handler = app

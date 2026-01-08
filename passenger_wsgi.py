import sys
import os
import time
from datetime import datetime
import traceback

# Redirect output to log files to prevent Passenger 502 errors from startup noise
sys.stdout = open("passenger_stdout.log", "a", buffering=1)
sys.stderr = open("passenger_stderr.log", "a", buffering=1)


def log(msg):
    print(f"[{datetime.now()}] {msg}", flush=True)


try:
    log("Starting passenger_wsgi.py...")
    # Add 'src' to the path so we can import our modules
    # Assuming this file is in the project root and 'src' is a subdirectory
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
    log("Path updated.")

    log("Importing modules...")
    from a2wsgi import ASGIMiddleware
    from nicegui import app

    # Import your application logic
    from price_list.app import entry_point
    from price_list.state import State
    from price_list.dao_panda import DaoPanda

    log("Modules imported.")

    # Initialize the application state and dao
    # This needs to run once when the application starts
    log("Initializing State...")
    state = State()
    log("Initializing DaoPanda...")
    dao = DaoPanda(state)

    log("Running entry_point (Data Loading)...")
    entry_point(state, dao)
    log("entry_point completed.")

    # NiceGUI exposes 'app' which is a FastAPI (ASGI) application.
    # Passenger (on cPanel) typically expects a WSGI application.
    # ASGIMiddleware adapts the ASGI app to WSGI.
    log("Creating ASGIMiddleware...")
    application = ASGIMiddleware(app)
    log("Application ready.")

except Exception as e:
    log(f"CRITICAL ERROR IN STARTUP: {e}")
    traceback.print_exc()
    raise e

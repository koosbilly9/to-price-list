import sys
import os

# Add 'src' to the path so we can import our modules
# Assuming this file is in the project root and 'src' is a subdirectory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from a2wsgi import ASGIMiddleware
from nicegui import app

# Import your application logic
from price_list.app import entry_point
from price_list.state import State
from price_list.dao_panda import DaoPanda

# Initialize the application state and dao
# This needs to run once when the application starts
state = State()
dao = DaoPanda(state)
entry_point(state, dao)

# NiceGUI exposes 'app' which is a FastAPI (ASGI) application.
# Passenger (on cPanel) typically expects a WSGI application.
# ASGIMiddleware adapts the ASGI app to WSGI.
application = ASGIMiddleware(app)

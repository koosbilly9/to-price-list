import sys
import os
from a2wsgi import ASGIMiddleware  # type: ignore
from nicegui import app

# Add src to path so we can import our modules
# We use os.path.dirname(__file__) to get the directory where passenger_wsgi.py is located
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from price_list.app import entry_point
from price_list.state import State
from price_list.dao_panda import DaoPanda

# Initialize the application state and DAO
state = State()
dao = DaoPanda(state)

# Load the application content (routes, UI, etc.)
entry_point(state, dao)

# specific to cpanel/passenger
# Wrap the ASGI app (NiceGUI) with ASGIMiddleware to make it WSGI compatible
application = ASGIMiddleware(app)

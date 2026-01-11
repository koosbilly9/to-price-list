import sys
import os
import time


# Logging helper to write to server logs (stderr)
def log(msg):
    # Using stderr ensures it ends up in Apache/Nginx/Passenger error logs
    print(f"[passenger_wsgi] {msg}", file=sys.stderr)


log("Initializing passenger_wsgi.py...")

try:
    # 1. Setup Path
    # We use os.path.dirname(__file__) to get the directory where passenger_wsgi.py is located
    # This ensures we can import from 'src' regardless of current working directory
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

    # 2. Imports
    # We wrap imports to catch missing dependency errors early
    try:
        from a2wsgi import ASGIMiddleware  # type: ignore
        from nicegui import app
    except ImportError as e:
        raise ImportError(f"Failed to import infrastructure (a2wsgi/nicegui): {e}")

    # FORCE HTTP POLLING (Fix for Passenger/LiteSpeed timeouts)
    # Shared hosting kills persistent WebSockets, so we force standard HTTP requests
    app.config.socket_io_js_transports = ["polling"]

    try:
        from price_list.app import entry_point
        from price_list.state import State
        from price_list.dao_panda import DaoPanda
    except ImportError as e:
        raise ImportError(f"Failed to import application modules: {e}")

    log("Imports successful.")

    # 3. Application Setup
    # Initialize the application state and DAO
    state = State()
    dao = DaoPanda(state)

    # log("Loading application data (entry_point)...")
    # start_time = time.time()

    # Load the application content (routes, UI, etc.)
    # This might take a few seconds as it reads the Excel file
    # entry_point(state, dao)

    # elapsed = time.time() - start_time
    # log(
    #     f"Data verification: Loaded {len(dao.panda_tsoeneops_price_list)} rows in {elapsed:.2f}s"
    # )

    from nicegui import ui

    @ui.page("/")
    def index():
        ui.label("Minimal NiceGUI Test - Success!")

    # 4. Create WSGI Application
    # Wrap the ASGI app (NiceGUI) with ASGIMiddleware to make it WSGI compatible
    application = ASGIMiddleware(app)

    log("Application initialized successfully.")

except Exception as e:
    log(f"CRITICAL ERROR: {e}")

    # Fallback application to show error in browser instead of Generic 500
    def application(environ, start_response):
        status = "500 Internal Server Error"
        output = f"App Startup Failed.\n\nError: {e}\n\nCheck server logs for details.".encode(
            "utf-8"
        )
        response_headers = [
            ("Content-type", "text/plain"),
            ("Content-Length", str(len(output))),
        ]
        start_response(status, response_headers)
        return [output]

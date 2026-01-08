import sys
import os
import time
from datetime import datetime

# Add src to path just like passenger_wsgi.py
sys.path.insert(0, os.path.join(os.getcwd(), "src"))

print(f"[{datetime.now()}] Starting simulation of passenger_wsgi startup...")

start_time = time.time()

try:
    print(f"[{datetime.now()}] Importing modules...")
    try:
        from a2wsgi import ASGIMiddleware

        has_a2wsgi = True
    except ImportError:
        print(
            "[WARNING] a2wsgi module not found. Skipping middleware creation, but will test data loading."
        )
        has_a2wsgi = False

    from nicegui import app
    from price_list.app import entry_point
    from price_list.state import State
    from price_list.dao_panda import DaoPanda

    print(f"[{datetime.now()}] Modules imported. Time: {time.time() - start_time:.2f}s")

    print(f"[{datetime.now()}] Initializing State and DAO...")
    state = State()
    dao = DaoPanda(state)

    print(f"[{datetime.now()}] Running entry_point (This triggers data loading)...")
    load_start = time.time()
    entry_point(state, dao)
    load_end = time.time()

    print(
        f"[{datetime.now()}] entry_point completed. Data load time: {load_end - load_start:.2f}s"
    )

    if has_a2wsgi:
        print(f"[{datetime.now()}] Creating ASGIMiddleware...")
        application = ASGIMiddleware(app)
    else:
        print(f"[{datetime.now()}] Skipping ASGIMiddleware creation (module missing).")

    total_time = time.time() - start_time
    print(f"[{datetime.now()}] Startup complete. Total time: {total_time:.2f}s")

except Exception as e:
    print(f"\n[ERROR] Startup failed: {e}")
    import traceback

    traceback.print_exc()

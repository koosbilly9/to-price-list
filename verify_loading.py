import sys
import os
import pandas as pd

# Add the project directory to sys.path
project_root = "/home/qxu6895/projects/tsoeneops-price-list"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "src"))

from price_list.state import State
from price_list.dao_panda import DaoPanda

state = State()
# Adjust formatted file path if necessary because we are running from root
# state.file_path is absolute based on __file__ in state.py, so it should be fine.

print(f"Loading from: {state.file_path}")

dao = DaoPanda(state)
dao.load_amrod_price_list()

df = dao.panda_tsoeneops_price_list
print(f"Total rows: {len(df)}")

if "sheet name" in df.columns:
    clothing = df[df["sheet name"] == "Continuing Clothing"]
    print(f"Clothing rows: {len(clothing)}")
    if len(clothing) > 0:
        print("SUCCESS: Clothing loaded with correct columns")
        print(clothing.iloc[0])
    else:
        print("FAILURE: Clothing sheet found but no rows (or filtered out)")
else:
    print("FAILURE: 'sheet name' column missing")

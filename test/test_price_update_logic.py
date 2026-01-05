import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from price_list.state import State
from price_list.dao_panda import DaoPanda


def verify_logic():
    print("Initializing State and DAO...")
    state = State()
    # Mock file path to be absolute or correct relative
    # state.file_path is already set in State, but we might need to adjust if running from root
    state.file_path = os.path.abspath(
        "src/price_list/other_lists/amrod_price_list.xlsx"
    )

    dao = DaoPanda(state)

    print(f"Loading data from {state.file_path}...")
    try:
        dao.load_amrod_price_list()
    except Exception as e:
        print(f"Error loading file: {e}")
        # Create dummy data if file load fails (for testing logic)
        print("Creating dummy data for testing...")
        data = {
            "Simple Code": ["A1", "A2"],
            "Description": ["Desc1", "Desc2"],
            "Category": ["Cat1", "Cat2"],
            "Jade": [100.0, 200.0],
            "vat %": [0.15, 0.15],
            "with tax": [115.0, 230.0],
        }
        dao.panda_tsoeneops_price_list = pd.DataFrame(data)
        dao.add_columns_tsoeneops_price_list()  # This might re-calc based on Jade/etc

    if dao.panda_tsoeneops_price_list.empty:
        print("DataFrame is empty after load. Cannot verify.")
        return

    # Check if 'price' is numeric
    print("\nChecking column types...")
    print(dao.panda_tsoeneops_price_list.dtypes)

    if not pd.api.types.is_numeric_dtype(dao.panda_tsoeneops_price_list["price"]):
        print("FAIL: 'price' column is not numeric!")
        print(dao.panda_tsoeneops_price_list["price"].head())
    else:
        print("PASS: 'price' column is numeric.")

    # Check initial values
    initial_markup = state.markup_percent
    # We take the first row
    row0 = dao.panda_tsoeneops_price_list.iloc[0]
    initial_price = row0["price"]
    print(f"\nInitial Markup: {initial_markup}")
    print(f"Initial Price (Row 0): {initial_price}")

    # Change markup using DAO method
    new_markup = 0.50
    print(f"\nChanging markup to {new_markup}...")
    state.markup_percent = new_markup
    dao.change_markup()

    # Verify update
    updated_row0 = dao.panda_tsoeneops_price_list.iloc[0]
    updated_price = updated_row0["price"]
    print(f"Updated Price (Row 0): {updated_price}")

    if updated_price > initial_price:
        print("PASS: Price increased as expected.")
    else:
        print("FAIL: Price did not increase.")

    # Expected calculation
    # price = with_tax + markup + vat_on_markup
    # markup = with_tax * markup_percent
    # vat_on_markup = markup * vat_percent
    # effectively: price = with_tax * (1 + markup_percent * (1 + vat_percent))

    with_tax = row0["with tax"]
    expected_price = (
        with_tax + (with_tax * new_markup) + (with_tax * new_markup * state.vat_percent)
    )

    print(f"Expected Price: {expected_price}")
    if abs(updated_price - expected_price) < 0.01:
        print("PASS: Price matches expected calculation.")
    else:
        print(f"FAIL: Price mismtach. Got {updated_price}, expected {expected_price}")


if __name__ == "__main__":
    verify_logic()

import os
from datetime import datetime

import pandas as pd

from price_list.state import State


class DaoPanda:
    def __init__(self, state: State):

        self.state = state
        self.panda_tsoeneops_price_list = pd.DataFrame()
        self.all_dfs = []
        self.state.reward_tier_list = [
            "Jade",
            "Chrome",
            "Bronze",
            "Cobalt",
            "Silver",
            "Gold",
            "Platinum",
            "Diamond",
            "Titanium",
            "Tanzanite",
        ]

    def change_markup(self):
        df = self.panda_tsoeneops_price_list.copy()
        df["markup %"] = self.state.markup_percent
        df["markup"] = df["with tax"] * df["markup %"]
        df["vat on markup"] = df["markup"] * df["vat %"]
        df["price"] = df["with tax"] + df["markup"] + df["vat on markup"]
        self.panda_tsoeneops_price_list = df

    def add_columns_tsoeneops_price_list(self):
        # Add new columns
        self.panda_tsoeneops_price_list["vat %"] = self.state.vat_percent

        # Ensure reward tier column is numeric
        self.panda_tsoeneops_price_list[self.state.reward_tier] = pd.to_numeric(
            self.panda_tsoeneops_price_list[self.state.reward_tier], errors="coerce"
        ).fillna(0)

        self.panda_tsoeneops_price_list["vat"] = (
            self.panda_tsoeneops_price_list[self.state.reward_tier]
            * self.panda_tsoeneops_price_list["vat %"]
        )
        self.panda_tsoeneops_price_list["with tax"] = (
            self.panda_tsoeneops_price_list[self.state.reward_tier]
            + self.panda_tsoeneops_price_list["vat"]
        )
        self.panda_tsoeneops_price_list["markup %"] = self.state.markup_percent
        self.panda_tsoeneops_price_list["markup"] = (
            self.panda_tsoeneops_price_list["with tax"]
            * self.panda_tsoeneops_price_list["markup %"]
        )
        self.panda_tsoeneops_price_list["vat on markup"] = (
            self.panda_tsoeneops_price_list["markup"]
            * self.panda_tsoeneops_price_list["vat %"]
        )
        self.panda_tsoeneops_price_list["price"] = (
            self.panda_tsoeneops_price_list["with tax"]
            + self.panda_tsoeneops_price_list["markup"]
            + self.panda_tsoeneops_price_list["vat on markup"]
        )
        self.panda_tsoeneops_price_list["url"] = (
            "https://amrod.co.za/product/"
            + self.panda_tsoeneops_price_list["Simple Code"].astype(str)
        )

    def combine_sheets(self):
        # Fix for "Continuing Clothing" sheet having header on the second line
        if "Continuing Clothing" in self.state.dict_amrod_prices:
            try:
                # Reload this specific sheet correctly
                print("Reloading 'Continuing Clothing' sheet with header=1")
                df_cc = pd.read_excel(
                    self.state.file_path, sheet_name="Continuing Clothing", header=1
                )
                self.state.dict_amrod_prices["Continuing Clothing"] = df_cc
            except Exception as e:
                print(f"Failed to reload 'Continuing Clothing' sheet: {e}")

        # Normalize Columns
        for sheet, df in self.state.dict_amrod_prices.items():
            # Rename columns if they exist
            df.rename(
                columns={"Product Code": "Simple Code", "Product Name": "Description"},
                inplace=True,
            )
            # Handle " Product Name" with leading space if present (seen in Workwear)
            df.rename(columns={" Product Name": "Description"}, inplace=True)

            # Ensure Category exists
            if "Category" not in df.columns:
                df["Category"] = sheet  # Default category to sheet name

        # Clean up: only include rows with a value in 'Simple Code'
        for sheet, df in self.state.dict_amrod_prices.items():
            if "Simple Code" in df.columns:
                self.state.dict_amrod_prices[sheet] = df.dropna(subset=["Simple Code"])

        # Combine all sheets into 1 df
        all_dfs = []
        for sheet, df in self.state.dict_amrod_prices.items():
            print(f"{sheet}: {len(df)} rows")

            # Only include sheets that have the required columns
            required_cols = {
                "Simple Code",
                "Description",
                "Category",
                self.state.reward_tier,
            }
            if required_cols.issubset(df.columns):
                # Create a copy to avoid SettingWithCopyWarning when modifying
                df_subset = df[
                    [
                        "Simple Code",
                        "Description",
                        "Category",
                        self.state.reward_tier,
                    ]
                ].copy()
                df_subset["sheet name"] = sheet
                all_dfs.append(df_subset)
            else:
                missing = required_cols - set(df.columns)
                print(f"  SKIPPING {sheet}: Missing columns {missing}")
                print(f"  Actual columns: {df.columns.tolist()}")

            # Check if all_dfs is empty before insert or update
            if all_dfs:
                self.panda_tsoeneops_price_list = pd.concat(all_dfs, ignore_index=True)
            else:
                self.panda_tsoeneops_price_list = pd.DataFrame(
                    columns=[
                        "Simple Code",
                        "Description",
                        "Category",
                        "sheet name",
                        self.state.reward_tier,
                    ]
                )

            print(sheet)

        # Next step: add columns
        self.add_columns_tsoeneops_price_list()

    def load_amrod_price_list(self) -> pd.DataFrame:
        try:
            print("Loading price list...")
            self.state.dict_amrod_prices = pd.read_excel(
                self.state.file_path, sheet_name=None
            )

            # Get file size and modification time
            size_bytes = os.path.getsize(self.state.file_path)  # Size in bytes
            self.state.file_size = f"{size_bytes / (1024 ** 2):.2f} MB"
            timestamp = os.path.getmtime(self.state.file_path)  # Modification date
            self.state.file_mod_time = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            print("--- END Loading price list...")

            # Next step: combine sheets
            self.combine_sheets()

        except Exception as e:
            print(f"Could not read price list: {e}")
            return pd.DataFrame()

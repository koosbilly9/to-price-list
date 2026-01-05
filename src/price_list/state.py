from datetime import datetime

from nicegui import binding
import pandas as pd
from dataclasses import field
import os


@binding.bindable_dataclass
class State:
    dict_amrod_prices: dict = field(default_factory=dict)
    reward_tier: str = "Jade"
    reward_tier_list: list = field(default_factory=list)
    selected_items: list = field(default_factory=list)

    selected_sheet_name: str = "Continuing Gifts"

    vat_percent: float = 0.15
    markup_percent: float = 0.34

    script_dir: str = os.path.dirname(os.path.abspath(__file__))
    file_location: str = "other_lists/amrod_price_list.xlsx"
    file_path: str = os.path.join(script_dir, file_location)

    file_mod_time: str = "????/??/??"
    file_size: str = "?mb"

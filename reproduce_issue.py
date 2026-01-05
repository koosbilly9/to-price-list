from nicegui import binding
import pandas as pd
from dataclasses import field

@binding.bindable_dataclass
class State:
    df: pd.DataFrame = field(default_factory=pd.DataFrame)

try:
    s = State()
    print("Initial state created")
    # This should trigger the comparison s.df != new_df
    s.df = pd.DataFrame({'a': [1, 2]})
    print("State updated successfully")
except Exception as e:
    print(f"Caught expected error: {e}")

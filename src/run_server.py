from price_list.app import entry_point
from nicegui import ui
from price_list.state import State
from price_list.dao_panda import DaoPanda


if __name__ in {'__main__', '__mp_main__'}:
    state = State()
    dao = DaoPanda(state)
    entry_point(state, dao)
    ui.run(port= 5000)
    
from nicegui import ui, app

from price_list.dao_panda import DaoPanda
from price_list.state import State

from icecream import ic


def entry_point(state: State, dao: DaoPanda):
    # On Start
    # dao.load_amrod_price_list() # Defer loading to prevent startup timeout
    app.add_static_files("/images", "src/images")

    # Other Functions

    def upload_different_price_list():
        with ui.dialog() as dialog, ui.card():
            with ui.card_section():
                ui.label("Upload different price list")
                ui.upload(
                    auto_upload=True,
                    on_upload=lambda e: upload_different_price_list_file(e, dialog),
                )
            with ui.card_section():
                ui.button("Close", on_click=dialog.close)

        dialog.open()

    async def upload_different_price_list_file(e, dialog):
        await e.file.save(state.file_path)
        dao.load_amrod_price_list()
        main_table.refresh()
        dialog.close()

    # main table
    @ui.refreshable
    def main_table():
        # Create a copy for display to avoid modifying the actual data in the DAO
        df_display = dao.panda_tsoeneops_price_list.copy()

        # Format numeric columns for display
        for col in [
            state.reward_tier,
            "vat",
            "with tax",
            "markup",
            "vat on markup",
            "price",
        ]:
            if col in df_display.columns:
                df_display[col] = df_display[col].map("R {:,.2f}".format)

        price_table = ui.table.from_pandas(
            df_display,
            pagination=10,
            selection="multiple",
            row_key="Simple Code",
        )

        def handle_selection(e):
            state.selected_items = price_table.selected

        price_table.on("selection", handle_selection)

        # Debugging
        # ic(dir(price_table))

        ui.input("Search").bind_value(price_table, "filter").props("clearable")

        price_table.add_slot(
            "body-cell-url",
            '<q-td :props="props"><a :href="props.value" target="_blank">{{ props.value }}</a></q-td>',
        )
        for column in price_table.columns:
            column["sortable"] = True

        price_table.add_slot(
            "body-cell-price", '<q-td :props="props">{{ props.value }}</q-td>'
        )

    #  Main Display
    # Header
    with ui.row().classes("items-center gap-4"):
        ui.image("/images/to_logo.png").classes("w-24")
        with ui.label("Price List").classes("text-xl underline").style(
            "white-space: pre-line"
        ):
            ui.tooltip(
                f"source: ../{state.file_location} ({state.file_mod_time}) {state.file_size}"
            ).classes("text-lg")

        def manual_load():
            ui.notify("Loading data... please wait.")
            dao.load_amrod_price_list()
            main_table.refresh()
            ui.notify("Data loaded!")

        ui.button("Load Data", on_click=manual_load).classes("m-2 p-2 bg-orange-500")

    # Body
    with ui.card(align_items="start").classes("w-full ") as card_main:
        with ui.card_section() as card_sec_main:
            main_table()

        with ui.card_actions().classes(
            "w-full gap-4 items-center"
        ) as card_actions_main:

            def update_markup_percent(x):
                state.markup_percent = x.value
                dao.change_markup()
                main_table.refresh()

            def update_vat_percent(x):
                state.vat_percent = x.value
                dao.add_columns_tsoeneops_price_list()
                main_table.refresh()

            def update_reward_tier(x):
                state.reward_tier = x.value
                dao.combine_sheets()
                main_table.refresh()

            ui.number(label="Markup %", value=0.34, format="%.2f").bind_value_to(
                state, "markup_percent"
            ).classes("w-32").on_value_change(update_markup_percent)

            number_vat = (
                ui.number(label="Vat %", value=0.15, format="%.2f")
                .bind_value_to(state, "vat_percent")
                .classes("w-32")
                .on_value_change(update_vat_percent)
            )

            select_rewards_tier = (
                ui.select(
                    label="Reward Tier",
                    options=state.reward_tier_list,
                    value="Jade",
                )
                .bind_value_to(state, "reward_tier")
                .classes("w-32")
                .on_value_change(update_reward_tier)
            )

            with ui.button(
                "Upload different price list", on_click=upload_different_price_list
            ).classes("m-2 p-2"):
                ui.tooltip(
                    f"source: ../{state.file_location} ({state.file_mod_time}) {state.file_size}"
                ).classes("text-lg")

            def create_quote():
                if not state.selected_items:
                    ui.notify("No items selected", type="warning")
                    return

                with ui.dialog().classes("w-full") as dialog, ui.card().classes(
                    "w-full h-full p-0"
                ):
                    # Header
                    with ui.row().classes(
                        "w-full justify-between items-center p-4 bg-gray-100"
                    ):
                        with ui.row().classes("items-center gap-4"):
                            ui.image("/images/to_logo.png").classes("w-16")
                            ui.label("Quote").classes("text-2xl font-bold")
                        ui.button(icon="close", on_click=dialog.close).props(
                            "flat round"
                        )

                    # Customer Name Input
                    with ui.row().classes("w-full p-4 pb-0"):
                        input_customer = (
                            ui.input("Customer Name")
                            .classes("w-full")
                            .props("autofocus")
                        )

                    # Scrollable Content
                    with ui.scroll_area().classes("w-full flex-grow p-4"):

                        # Labels for Totals (defined early to be accessible)
                        lbl_total_ex = ui.label().classes("text-lg")
                        lbl_total_vat = ui.label().classes("text-lg")
                        lbl_total_inc = ui.label().classes("text-xl font-bold")

                        # Item State Management
                        quote_items = []

                        def parse_currency(val):
                            try:
                                return float(
                                    str(val).replace("R ", "").replace(",", "")
                                )
                            except (ValueError, AttributeError):
                                return 0.0

                        def recalculate():
                            total_inc = 0.0
                            total_vat = 0.0

                            for item in quote_items:
                                count = int(item["count_select"].value)
                                price = item["price_val"]
                                vat_per_item = item["vat_val"]

                                line_total = price * count
                                item["lbl_total"].text = f"R {line_total:,.2f}"

                                total_inc += line_total
                                total_vat += vat_per_item * count

                            total_ex = total_inc - total_vat

                            lbl_total_ex.text = f"Total Ex VAT: R {total_ex:,.2f}"
                            lbl_total_vat.text = f"VAT Amount: R {total_vat:,.2f}"
                            lbl_total_inc.text = f"Total Inc VAT: R {total_inc:,.2f}"

                        # Header Row
                        with ui.grid(columns="3fr 1fr 2fr 1fr 1fr 1fr").classes(
                            "w-full font-bold mb-2 border-b pb-2"
                        ):
                            ui.label("Description")
                            ui.label("Size")
                            ui.label("Color")
                            ui.label("Count")
                            ui.label("Unit Price").classes("text-right")
                            ui.label("Total").classes("text-right")

                        # Item Rows
                        for original_item in state.selected_items:
                            price_val = parse_currency(original_item.get("price", "0"))
                            vat_val = parse_currency(
                                original_item.get("vat", "0")
                            ) + parse_currency(original_item.get("vat on markup", "0"))

                            with ui.grid(columns="3fr 1fr 2fr 1fr 1fr 1fr").classes(
                                "w-full items-center mb-2 border-b border-gray-100 pb-2"
                            ):
                                ui.label(original_item.get("Description", ""))

                                select_size = ui.select(
                                    ["N/A", "S", "M", "L", "XL", "XXL"], value="N/A"
                                ).classes("w-full")
                                input_color = (
                                    ui.input(value="N/A")
                                    .props("dense")
                                    .classes("w-full")
                                )
                                select_count = ui.select(
                                    list(range(1, 100)),
                                    value=1,
                                    on_change=lambda _: recalculate(),
                                ).classes("w-full")

                                ui.label(original_item.get("price", "R 0.00")).classes(
                                    "text-right"
                                )
                                lbl_line_total = ui.label().classes(
                                    "text-right font-bold"
                                )

                            quote_items.append(
                                {
                                    "original": original_item,
                                    "price_val": price_val,
                                    "vat_val": vat_val,
                                    "size_select": select_size,
                                    "color_input": input_color,
                                    "count_select": select_count,
                                    "lbl_total": lbl_line_total,
                                }
                            )

                        # Footer / Totals Section
                        with ui.column().classes("w-full items-end mt-4 pt-4 border-t"):
                            lbl_total_ex
                            lbl_total_vat
                            lbl_total_inc

                        # Initial Calculation
                        recalculate()

                    # Actions
                    with ui.row().classes(
                        "w-full justify-end p-4 bg-gray-50 border-t gap-4"
                    ):

                        def save_quote():
                            customer_name = input_customer.value.strip()
                            if not customer_name:
                                ui.notify(
                                    "Please enter a customer name", type="warning"
                                )
                                return

                            content = "TO Branding Quote\n"
                            content += f"Customer: {customer_name}\n"
                            content += "=" * 50 + "\n\n"

                            f_total_inc = 0.0
                            f_total_vat = 0.0

                            for item in quote_items:
                                desc = item["original"].get("Description", "")
                                count = int(item["count_select"].value)
                                size = item["size_select"].value
                                color = item["color_input"].value
                                u_price = item["original"].get("price", "R 0.00")
                                price_val = item["price_val"]
                                vat_val = item["vat_val"]

                                line_total = price_val * count
                                f_total_inc += line_total
                                f_total_vat += vat_val * count

                                content += f"Item: {desc}\n"
                                content += (
                                    f"  Size: {size} | Color: {color} | Qty: {count}\n"
                                )
                                content += (
                                    f"  Unit: {u_price} | Total: R {line_total:,.2f}\n"
                                )
                                content += "-" * 30 + "\n"

                            f_total_ex = f_total_inc - f_total_vat

                            content += "\n\n" + "=" * 50 + "\n"
                            content += f"Total Ex VAT:  R {f_total_ex:,.2f}\n"
                            content += f"VAT Amount:    R {f_total_vat:,.2f}\n"
                            content += f"Total Inc VAT: R {f_total_inc:,.2f}\n"

                            # Save to file
                            import os
                            import datetime

                            timestamp = datetime.datetime.now().strftime(
                                "%Y-%m-%d_%H-%M-%S"
                            )
                            # Sanitize filename
                            safe_name = (
                                "".join(
                                    [
                                        c
                                        for c in customer_name
                                        if c.isalpha() or c.isdigit() or c == " "
                                    ]
                                )
                                .strip()
                                .replace(" ", "_")
                            )
                            filename = f"quote_{safe_name}_{timestamp}.txt"
                            filepath = os.path.join("src/quotes", filename)

                            # Ensure dir exists (just in case)
                            os.makedirs("src/quotes", exist_ok=True)

                            with open(filepath, "w") as f:
                                f.write(content)

                            ui.download(content.encode("utf-8"), filename)
                            ui.notify(f"Quote saved to {filepath}")
                            dialog.close()

                        ui.button("Close", on_click=dialog.close).classes("bg-gray-500")
                        ui.button("Save Quote", on_click=save_quote).classes(
                            "bg-blue-500"
                        )

                dialog.open()

            ui.button("Create Quote", on_click=create_quote).classes(
                "m-2 p-2 bg-green-500"
            )

    with ui.footer().classes("bg-white items-center justify-center"):
        ui.image("/images/to_corporate_atte.png").classes("h-12")

    # Intial refreshables

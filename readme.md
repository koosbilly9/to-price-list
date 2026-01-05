# TsoeneOps Price List

A NiceGUI-based application to manage and generate quotes from the Amrod price list.

## Features

*   **Price List Management**:
    *   Upload the latest Amrod price list (Excel format with multiple sheets).
    *   Automatic data cleaning and processing using Pandas.
    *   Combines multiple category sheets (Clothing, Gifts, Workwear, etc.) into a unified view.
*   **Dynamic Pricing**:
    *   **Tier Selection**: Select your specific pricing tier (Jade, Gold, etc.).
    *   **VAT & Markup**: Automatically calculates VAT and applies configurable markup logic.
    *   **Hidden Tiers**: Hover features to reveal comparison prices.
*   **Product Links**: Direct links to Amrod product pages.
*   **Quote Generation**:
    *   Select multiple items across different categories.
    *   Customize size, color, and quantity per item.
    *   Generate and download a professional PDF/Text quote.

## Usage

1.  **Update Price List**:
    *   Login to Amrod and download the latest Excel price list.
    *   Use the "Upload Latest Price List" button in the app to update the data.
2.  **Browse & Select**:
    *   Filter products by category or search by name.
    *   Select items to add them to your current session.
3.  **Generate Quote**:
    *   Click "Create Quote" to review selected items.
    *   Adjust quantities and variations.
    *   Enter Customer Name and save the quote.

## Installation & Running

### Windows
1.  Run `install.bat` to set up the environment.
2.  Run `run.cmd` to start the application.

### Linux/Mac
1.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2.  Install dependencies:
    ```bash
    pip install -e .
    ```
3.  Run the server:
    ```bash
    python src/run_server.py
    ```

## Roadmap (v2)

*   [ ] AI interface to expedite search and selection.
*   [ ] Add Barron price list integration.
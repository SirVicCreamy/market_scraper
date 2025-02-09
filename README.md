# Supermarket Scraper (Multi-Market Expansion Project)

This project scrapes product information from online supermarkets, starting with Auchan Romania.  The goal is to expand to other major supermarket chains.

## Current Functionality (Auchan)

* Search for products by name.
* Retrieve product title, price (including availability), and product page link.
* Filter results: Show all products, only available, or only unavailable.
* Sort results by title or price.

## Future Plans

* Support other supermarkets (e.g., Carrefour, Cora, Mega Image).
* Unified data format across markets.
* Market comparison features.
* UI enhancements for multiple markets.
* Data export (CSV, JSON).

## Setup

1. **Clone:**
   ```bash
   git clone [https://github.com/your-username/auchan-scraper.git](https://github.com/your-username/auchan-scraper.git)
   cd auchan-scraper
Virtual Environment (recommended):

Bash

python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
Install Dependencies:

Bash

pip install Flask requests urllib3 beautifulsoup4  # If using Beautiful Soup


Run:

Bash

python app.py
Access:
Open your browser to http://127.0.0.1:5000/.

Usage
Search: Enter a product name and click "Search."
Filter: Use the "Show Unavailable" switch.
Sort: Click column headers (Product Title, Price).
View: Click "View Product" to open the product page.

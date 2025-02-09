# Supermarket Scraper (Multi-Market Expansion)

A web scraper for online supermarkets, starting with Auchan Romania. Built with Python 3.10+.

## Features (Auchan Romania)
- **Search**: Find products by name
- **Product Data**: Title, price, availability, and link
- **Filters**: Show all, available, or unavailable products
- **Sorting**: By title or price

## Future Plans
- Add support for Carrefour, Cora, Mega Image
- Unified data format for all markets
- Price comparison features
- Export data to CSV/JSON

## Setup

1. Clone the repo
2. Install dependencies:
```
pip install Flask requests beautifulsoup4 urllib3
```
Run the app:
```python app.py```
Open your browser:
```
http://127.0.0.1:5000
```
Usage
Search: Enter a product name and click "Search."

Filter: Toggle availability filters.

Sort: Click column headers (Title/Price).

View: Click "View Product" for details.

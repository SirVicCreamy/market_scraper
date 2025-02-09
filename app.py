from flask import Flask, render_template, request, jsonify
import requests
import logging
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Tuple, List, Dict, Optional
import json
import time
import concurrent.futures

app = Flask(__name__)

# --- Configuration ---
app.config['ITEMS_PER_PAGE'] = 49  # Set to 49 or less
app.config['REQUEST_TIMEOUT'] = 15
app.config['RETRY_TOTAL'] = 3
app.config['RETRY_BACKOFF_FACTOR'] = 0.5
app.config['RETRY_STATUS_FORCELIST'] = [500, 502, 503, 504]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
AUCHAN_REFERER = "https://www.auchan.ro/"
BASE_API_URL = "https://www.auchan.ro/api/catalog_system/pub/products/search"

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=app.config['RETRY_TOTAL'], backoff_factor=app.config['RETRY_BACKOFF_FACTOR'],
                    status_forcelist=app.config['RETRY_STATUS_FORCELIST'], allowed_methods=["GET"])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json",
                            "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7", "Referer": AUCHAN_REFERER})
    return session

def validate_product_data(item: dict) -> bool:
    required_fields = ['productName', 'items', 'link']
    is_valid = all(item.get(field) for field in required_fields)
    if not is_valid:
        logger.warning(f"Product data validation failed for item: {item.get('productName', 'Unknown Product')}")
    return is_valid

def parse_price(item: dict) -> float:
    try:
        return float(item['items'][0]['sellers'][0]['commertialOffer']['Price'])
    except (KeyError, IndexError, TypeError, ValueError) as e:
        logger.warning(f"Failed to parse price for product: {item.get('productName', 'Unknown Product')}. Error: {e}")
        return 0.0

def fetch_products_data(session: requests.Session, query: str, offset: int, to: int) -> Optional[List[Dict]]:
    items_per_page = app.config['ITEMS_PER_PAGE']
    encoded_query = quote(query).replace('+', '%20')
    api_url = (f"{BASE_API_URL}/{encoded_query}"
               f"?_q={encoded_query}&map=ft&O=OrderByScoreDESC&_from={offset}&_to={to}")

    logger.info(f"Request URL: {api_url}")

    try:
        response = session.get(api_url, timeout=app.config['REQUEST_TIMEOUT'])
        response.raise_for_status()

        logger.info(f"Response Status Code: {response.status_code}")
        if response.status_code == 200 and isinstance(response.json(), list):
            log_limit = 5
            products_to_log = response.json()[:log_limit]
            logger.info(f"Response Content (first {log_limit} items): {json.dumps(products_to_log, indent=4)}")

        return response.json()
    except requests.RequestException as e:
        logger.error(f"Products request failed for query '{query}', offset {offset}: {e}")
        if hasattr(response, 'text'):
            logger.error(f"Response content (error): {response.text}")
        return None

def scrape_auchan_page(session: requests.Session, query: str, offset: int, to: int) -> Optional[List[Dict]]:
    products_data = fetch_products_data(session, query, offset, to)
    if products_data and isinstance(products_data, list):
        return products_data
    return None

def scrape_auchan(query: str, show_only_unavailable: bool = False) -> Tuple[List[Dict[str, str]], int]:
    products = []
    total_available_products = 0
    max_products_to_scrape = 9999
    items_per_page = app.config['ITEMS_PER_PAGE']
    start_time = time.time()
    api_limit = 2500

    try:
        session = get_session()
        encoded_query = quote(query).replace('+', '%20')

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            offset = 0
            while offset < max_products_to_scrape:
                to = min(offset + items_per_page - 1, max_products_to_scrape - 1)
                to_within_limit = None  # Initialize to_within_limit here

                if offset >= api_limit:
                    offset_within_limit = offset % api_limit
                    to_within_limit = min(offset_within_limit + items_per_page - 1, api_limit - 1)
                    futures.append(executor.submit(scrape_auchan_page, session, query, offset_within_limit, to_within_limit))  # Pass session here
                else:
                    futures.append(executor.submit(scrape_auchan_page, session, query, offset, to))  # Pass session here

                offset += items_per_page

                # Corrected conditional check
                if to_within_limit is not None and offset >= api_limit and to_within_limit == api_limit - 1:
                    break  # Break if at limit and last item
                elif offset >= api_limit * 2:
                    break  # Break if reached double the limit

            for future in concurrent.futures.as_completed(futures):
                products_data = future.result()
                if products_data:
                    for item in products_data:
                        if validate_product_data(item):
                            price = parse_price(item)
                            price_display = f"{price:.2f} RON" if price > 0 else "Indisponibil"

                            if show_only_unavailable:
                                if price == 0:  # Only add unavailable products if the switch is ON
                                    products.append({
                                        "title": item['productName'],
                                        "price": price,
                                        "price_display": price_display,
                                        "url": item['link']
                                    })
                            else:  # Add all products (available and unavailable) if the switch is OFF
                                if price > 0:
                                    total_available_products += 1
                                products.append({
                                    "title": item['productName'],
                                    "price": price,
                                    "price_display": price_display,
                                    "url": item['link']
                                })

    except Exception as e:
        logger.exception(f"Scraping failed for query '{query}': {e}")
        return [], 0  # Return empty list and 0 on exception

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Scraping for query '{query}' took {elapsed_time:.2f} seconds.")

    return products, total_available_products


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    query = ""
    error = None
    total_results = 0
    show_unavailable = False  # Initialize show_unavailable

    if request.method == "POST":
        query = request.form.get("query", "").strip()
        show_unavailable = bool(request.form.get("show_unavailable"))  # Get show_unavailable from the form
    else:
        query = request.args.get('query', '').strip()
        show_unavailable = bool(request.args.get('show_unavailable'))  # Get show_unavailable from the query parameters

    if query:
        try:
            results, total_results = scrape_auchan(query, show_only_unavailable=show_unavailable)  # Corrected call!

        except Exception as e:
            error = f"An unexpected error occurred: {str(e)}"
            logger.error(f"Error in route handler for query '{query}': {e}")
            results = []

    return render_template(
        "index.html",
        results=results,
        query=query,
        error=error,
        total_results=total_results,
        show_unavailable=show_unavailable,  # Pass show_unavailable to the template
        items_per_page=app.config['ITEMS_PER_PAGE']
    )

@app.route("/load_more", methods=["GET"])
def load_more():
    return jsonify(error="This endpoint is no longer available.")

if __name__ == "__main__":
    app.run(debug=True)
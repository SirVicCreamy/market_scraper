# 🛒 Supermarket Scraper 

A scalable web scraper that collects product information from online supermarkets, starting with Auchan Romania. Designed for easy expansion to other retail chains.

## 🌟 Features (Current: Auchan Romania)

### Product Operations
- **Search**: Find products by name across entire catalog
- **Data Retrieval**:
  - Product title
  - Current price (with availability status)
  - Direct product page link
- **Filters**:
  - Show all products
  - Available-only filter
  - Unavailable-only filter
- **Sorting**:
  - Alphabetical (A-Z/Z-A)
  - Price (Low-High/High-Low)

## 🚀 Roadmap (Future Features)

### Market Expansion
- **New Retailers**: Carrefour, Cora, Mega Image (Q2 2024)
- **Unified API**: Standardized data format across all markets
- **Price Comparison**: Cross-market price analysis tool

### UI Improvements
- Multi-market dashboard
- Historical price charts
- User preference profiles

### Data Features
- CSV/JSON export capabilities
- Email price alerts
- Bulk data export API

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Start
```bash
# Clone repository
git clone https://github.com/your-username/auchan-scraper.git
cd auchan-scraper

# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate    # Linux/macOS
.\venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt  # Create this file with listed packages

# Launch application
python app.py

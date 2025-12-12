"""
Sales Server - Flask REST API for sales data
Runs on localhost:5002

Endpoints:
- GET /sales?start_date=yyyymmdd&end_date=yyyymmdd: Returns sales within date range
"""

from flask import Flask, jsonify, request
from pathlib import Path
import csv
from typing import List, Dict

app = Flask(__name__)

# Get the directory where this script is located (for Windows-compatible paths)
SCRIPT_DIR = Path(__file__).parent

# In-memory storage for sales data
sales: List[Dict[str, str]] = []


def load_sales() -> None:
    """Load sales data from CSV file at startup."""
    global sales
    csv_path = SCRIPT_DIR / "sales.csv"
    
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            sales = list(reader)
    except FileNotFoundError:
        sales = []


@app.route("/sales")
def get_sales():
    """
    Get sales within a specified date range (inclusive).
    
    Query Parameters:
        start_date: Start date in yyyymmdd format (e.g., "20260101")
        end_date: End date in yyyymmdd format (e.g., "20260131")
    
    Returns:
        JSON array of sales objects (ordid, custid, orddate, ordamount)
        Empty array if no sales in range or if parameters missing
    """
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    
    # Return empty array if parameters are missing
    if not start_date or not end_date:
        return jsonify([])
    
    # Filter sales by date range (string comparison works for yyyymmdd format)
    result = [
        {
            "ordid": s["ordid"],
            "custid": s["custid"],
            "orddate": s["orddate"],
            "ordamount": int(s["ordamount"])  # Convert to integer for proper JSON
        }
        for s in sales
        if start_date <= s["orddate"] <= end_date
    ]
    
    return jsonify(result)


# Load data when module is imported
load_sales()


if __name__ == "__main__":
    print(f"Sales Server starting...")
    print(f"Loaded {len(sales)} sales records from CSV")
    print(f"Server running at http://localhost:5002")
    
    # Run Flask development server
    app.run(host="localhost", port=5002, debug=False)

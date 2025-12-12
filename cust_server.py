"""
Customer Server - Flask REST API for customer data
Runs on localhost:5001

Endpoints:
- GET /customer/<custid>: Returns customer data for specified custid
- GET /customers/city/<city>: Returns all customers in specified city
"""

from flask import Flask, jsonify
from pathlib import Path
import csv
from typing import List, Dict

app = Flask(__name__)

# Get the directory where this script is located (for Windows-compatible paths)
SCRIPT_DIR = Path(__file__).parent

# In-memory storage for customer data
customers: List[Dict[str, str]] = []


def load_customers() -> None:
    """Load customer data from CSV file at startup."""
    global customers
    csv_path = SCRIPT_DIR / "customers.csv"
    
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            customers = list(reader)
    except FileNotFoundError:
        customers = []


@app.route("/customer/<custid>")
def get_customer(custid: str):
    """
    Get customer data for a specific customer ID.
    
    Args:
        custid: Customer ID (e.g., "011")
    
    Returns:
        JSON with custid, custname, city or empty object if not found
    """
    for customer in customers:
        if customer["custid"] == custid:
            return jsonify({
                "custid": customer["custid"],
                "custname": customer["custname"],
                "city": customer["city"]
            })
    
    # Return empty object if customer not found
    return jsonify({})


@app.route("/customers/city/<city>")
def get_customers_by_city(city: str):
    """
    Get all customers in a specified city.
    
    Args:
        city: City name (case-insensitive matching)
    
    Returns:
        JSON array of customer objects or empty array if no customers found
    """
    # Case-insensitive city matching
    result = [
        {
            "custid": c["custid"],
            "custname": c["custname"],
            "city": c["city"]
        }
        for c in customers
        if c["city"].lower() == city.lower()
    ]
    
    return jsonify(result)


# Load data when module is imported
load_customers()


if __name__ == "__main__":
    print(f"Customer Server starting...")
    print(f"Loaded {len(customers)} customers from CSV")
    print(f"Server running at http://localhost:5001")
    
    # Run Flask development server
    app.run(host="localhost", port=5001, debug=False)

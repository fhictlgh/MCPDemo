"""
MCP Server - Model Context Protocol server for Sales & Customer Analysis
Uses stdio transport for Claude Desktop integration

Tools:
- get_customer_revenue_by_period: Get revenue for a specific customer
- get_city_revenue_by_period: Get revenue for all customers in a city
"""

import sys
import json
import requests
from typing import Any
from mcp.server.fastmcp import FastMCP

# Create the MCP server instance
mcp = FastMCP("Sales & Customer Analysis Server")

# API endpoints for Flask servers
CUSTOMER_API = "http://localhost:5001"
SALES_API = "http://localhost:5002"


def log(message: str) -> None:
    """Log messages to stderr (stdout is reserved for MCP protocol)."""
    print(message, file=sys.stderr)


def get_customer_data(cust_id: str) -> dict[str, Any]:
    """
    Fetch customer data from the customer API.
    
    Args:
        cust_id: Customer ID
    
    Returns:
        Customer data dict or empty dict if not found/error
    """
    try:
        response = requests.get(f"{CUSTOMER_API}/customer/{cust_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log(f"Error fetching customer {cust_id}: {e}")
        return {}


def get_customers_by_city(city: str) -> list[dict[str, Any]]:
    """
    Fetch all customers in a city from the customer API.
    
    Args:
        city: City name
    
    Returns:
        List of customer data dicts or empty list if not found/error
    """
    try:
        response = requests.get(f"{CUSTOMER_API}/customers/city/{city}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log(f"Error fetching customers for city {city}: {e}")
        return []


def get_sales_by_period(start_date: str, end_date: str) -> list[dict[str, Any]]:
    """
    Fetch sales within a date range from the sales API.
    
    Args:
        start_date: Start date in yyyymmdd format
        end_date: End date in yyyymmdd format
    
    Returns:
        List of sales data dicts or empty list if not found/error
    """
    try:
        response = requests.get(
            f"{SALES_API}/sales",
            params={"start_date": start_date, "end_date": end_date},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        log(f"Error fetching sales for period {start_date}-{end_date}: {e}")
        return []


@mcp.tool()
def get_customer_revenue_by_period(cust_id: str, start_date: str, end_date: str) -> str:
    """
    Get customer revenue for a specified period.
    
    Retrieves customer information and calculates total revenue from sales
    within the specified date range.
    
    Args:
        cust_id: Customer ID (e.g., "012")
        start_date: Start date in yyyymmdd format (e.g., "20260101")
        end_date: End date in yyyymmdd format (e.g., "20260131")
    
    Returns:
        JSON string with customer info (custid, custname, city), revenue, and sales_count
    """
    log(f"Getting revenue for customer {cust_id} from {start_date} to {end_date}")
    
    # Get customer data
    customer = get_customer_data(cust_id)
    
    # If customer not found, return empty result with zero revenue
    if not customer or not customer.get("custid"):
        result = {
            "custid": cust_id,
            "custname": "",
            "city": "",
            "revenue": 0,
            "sales_count": 0
        }
        return json.dumps(result, indent=2)
    
    # Get all sales in the period
    sales = get_sales_by_period(start_date, end_date)
    
    # Filter sales for this customer and calculate totals
    customer_sales = [s for s in sales if s["custid"] == cust_id]
    revenue = sum(s["ordamount"] for s in customer_sales)
    sales_count = len(customer_sales)
    
    result = {
        "custid": customer["custid"],
        "custname": customer["custname"],
        "city": customer["city"],
        "revenue": revenue,
        "sales_count": sales_count
    }
    
    log(f"Result: {result}")
    return json.dumps(result, indent=2)


@mcp.tool()
def get_city_revenue_by_period(city: str, start_date: str, end_date: str) -> str:
    """
    Get revenue for all customers in a city for a specified period.
    
    Retrieves all customers in the specified city and calculates their
    individual and total revenue from sales within the date range.
    Includes customers with zero revenue (no sales in period).
    
    Args:
        city: City name (e.g., "Eindhoven")
        start_date: Start date in yyyymmdd format (e.g., "20260101")
        end_date: End date in yyyymmdd format (e.g., "20260131")
    
    Returns:
        JSON string with city name, total_revenue, customer_count, and 
        array of customer details (custid, custname, revenue, sales_count)
    """
    log(f"Getting revenue for city {city} from {start_date} to {end_date}")
    
    # Get all customers in the city
    customers = get_customers_by_city(city)
    
    # If no customers found, return empty result
    if not customers:
        result = {
            "city": city,
            "total_revenue": 0,
            "customer_count": 0,
            "customers": []
        }
        return json.dumps(result, indent=2)
    
    # Get all sales in the period
    sales = get_sales_by_period(start_date, end_date)
    
    # Calculate revenue for each customer
    customer_details = []
    total_revenue = 0
    
    for customer in customers:
        cust_id = customer["custid"]
        
        # Filter sales for this customer
        customer_sales = [s for s in sales if s["custid"] == cust_id]
        revenue = sum(s["ordamount"] for s in customer_sales)
        sales_count = len(customer_sales)
        
        customer_details.append({
            "custid": cust_id,
            "custname": customer["custname"],
            "revenue": revenue,
            "sales_count": sales_count
        })
        
        total_revenue += revenue
    
    result = {
        "city": city,
        "total_revenue": total_revenue,
        "customer_count": len(customers),
        "customers": customer_details
    }
    
    log(f"Result: {result}")
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    log("Starting MCP Sales & Customer Analysis Server...")
    log("Using stdio transport for Claude Desktop integration")
    log(f"Customer API: {CUSTOMER_API}")
    log(f"Sales API: {SALES_API}")
    
    # Run the MCP server with stdio transport (default)
    mcp.run()

**Build MCP-Based Sales & Customer Analysis System**

**Project Goal:** Create a learning project to understand Model Context Protocol (MCP) by building a system with two Flask web APIs, an MCP server that consumes them, and Claude Desktop integration on Windows.

**Data Files:** Two CSV files with the following structure:

1. **customers.csv:**

```
custid,custname,city
011,Annie,Eindhoven
012,Bert,Eindhoven
013,Carla,Helmond
014,Dirk,Tilburg
015,Eric,Tilburg
016,Fien,Eindhoven
```

1. **sales.csv:**

```
ordid,custid,orddate,ordamount
501,012,20260103,9
502,014,20260107,11
503,012,20260119,5
504,016,20260119,21
505,011,20260123,12
506,013,20260127,3
507,011,20260130,7
508,012,20260203,9
509,014,20260209,5
510,015,20260209,5
511,016,20260211,10
512,014,20260217,7
```

**System Components:**

**1. Customer Server (cust_server.py) - Flask on localhost:5001** Implements two endpoints:

- `GET /customer/<custid>`: Returns customer data for specified custid (e.g., `/customer/011`)
  - Returns: JSON with custid, custname, city
  - Empty result if custid not found
- `GET /customers/city/<city>`: Returns all customers in specified city (e.g., `/customers/city/Eindhoven`)
  - Returns: JSON array of customer objects
  - Empty array if no customers in city

**2. Sales Server (sales_server.py) - Flask on localhost:5002** Implements one endpoint:

- `GET /sales?start_date=yyyymmdd&end_date=yyyymmdd`: Returns sales within date range (inclusive)
  - Date format: yyyymmdd (e.g., `20260103`)
  - Returns: JSON array of sales objects (ordid, custid, orddate, ordamount)
  - Empty array if no sales in range

**3. MCP Server (mcp_server.py) - stdio-based** Exposes two tools that Claude Desktop can call:

**Tool 1: get_customer_revenue_by_period**

- Parameters: `cust_id` (string), `start_date` (string, yyyymmdd), `end_date` (string, yyyymmdd)
- Logic:
  1. Call cust_server to get customer data by custid
  1. Call sales_server to get all sales in date range
  1. Filter sales by the specified custid
  1. Sum ordamount for matching sales
  1. Return: JSON with customer info (custid, custname, city), revenue (sum), sales count

**Tool 2: get_city_revenue_by_period**

- Parameters: `city` (string), `start_date` (string, yyyymmdd), `end_date` (string, yyyymmdd)
- Logic:
  1. Call cust_server to get all customers in specified city
  1. Call sales_server to get all sales in date range
  1. For each customer in city, filter sales by their custid and sum ordamount
  1. Include customers with zero revenue (no sales in period)
  1. Return: JSON with city name, total revenue, customer count, and array of customer revenue details (custid, custname, revenue, sales count)

**Technical Requirements:**

- **Framework:** Flask for web services
- **Platform:** Windows-compatible (use proper path handling)
- **Error Handling:** Return empty results (empty arrays/objects) for not-found cases; no error messages
- **CSV Reading:** Read CSV files at startup and keep in memory (no database)
- **Dependencies:** Create requirements.txt with all necessary packages
- **MCP Implementation:** Use the official MCP Python SDK (`mcp` package)

**Deliverables:**

1. **cust_server.py** - Customer web service
1. **sales_server.py** - Sales web service
1. **mcp_server.py** - MCP server implementing the two tools
1. **requirements.txt** - All Python dependencies
1. **claude_desktop_config.json** - Claude Desktop configuration for Windows
1. **README.md** - Clear instructions including:
   - How to install dependencies (`pip install -r requirements.txt`)
   - How to start the two Flask servers
   - How to configure Claude Desktop (where to place config file on Windows)
   - How to test the MCP tools in Claude Desktop
   - Example queries to try

**Configuration Details:**

- cust_server: `http://localhost:5001`
- sales_server: `http://localhost:5002`
- MCP server: stdio-based (no port, communicates via stdin/stdout)
- Claude Desktop config location on Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Expected Behavior Examples:**

Example 1: Get revenue for customer 012 in January 2026

```
Tool: get_customer_revenue_by_period
Input: cust_id="012", start_date="20260101", end_date="20260131"
Output: {custid: "012", custname: "Bert", city: "Eindhoven", revenue: 14, sales_count: 2}
```

Example 2: Get revenue for Eindhoven in January 2026

```
Tool: get_city_revenue_by_period
Input: city="Eindhoven", start_date="20260101", end_date="20260131"
Output: {
  city: "Eindhoven",
  total_revenue: 47,
  customer_count: 3,
  customers: [
    {custid: "011", custname: "Annie", revenue: 19, sales_count: 2},
    {custid: "012", custname: "Bert", revenue: 14, sales_count: 2},
    {custid: "016", custname: "Fien", revenue: 21, sales_count: 1}
  ]
}
```

**Code Quality Expectations:**

- Clean, readable code with comments
- Proper error handling (try-catch blocks)
- Type hints where appropriate
- Follow Python best practices
- Windows-compatible file paths (use `os.path` or `pathlib`)

**Please generate all files with complete, working code that can be run immediately after installing dependencies.**


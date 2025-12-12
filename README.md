# MCP Sales & Customer Analysis System

A learning project to understand the **Model Context Protocol (MCP)** by building a system with two Flask web APIs, an MCP server that consumes them, and Claude Desktop integration on Windows.

## System Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                      Claude Desktop                             │
│                    (Natural Language UI)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MCP Protocol (stdio)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MCP Server                                │
│                    (mcp_server.py)                              │
│   Tools:                                                        │
│   - get_customer_revenue_by_period                              │
│   - get_city_revenue_by_period                                  │
└─────────────────────────────────────────────────────────────────┘
                    │                       │
        HTTP REST   │                       │   HTTP REST
                    ▼                       ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│    Customer Server      │   │     Sales Server        │
│   (cust_server.py)      │   │   (sales_server.py)     │
│   localhost:5001        │   │   localhost:5002        │
│                         │   │                         │
│   /customer/<custid>    │   │   /sales?start_date=    │
│   /customers/city/<city>│   │        &end_date=       │
└─────────────────────────┘   └─────────────────────────┘
            │                             │
            ▼                             ▼
    ┌─────────────┐              ┌─────────────┐
    │customers.csv│              │  sales.csv  │
    └─────────────┘              └─────────────┘
```

## Prerequisites

- **Python 3.10+** (MCP SDK requirement)
- **Claude Desktop** installed on Windows
- **Windows Terminal** or PowerShell

## Installation

### Step 1: Create Virtual Environment (Recommended)

Open PowerShell in the project directory:

```powershell
# Navigate to project folder
cd "c:\Users\Analyst\OneDrive - Office 365 Fontys\Sync\25-26\1\Dev\S6-BDA\Explorations\Unified View over Data in External Systems\Possible Solution"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Flask Servers

You need **two separate terminal windows** for the Flask servers:

**Terminal 1 - Customer Server:**
```powershell
cd "c:\Users\Analyst\OneDrive - Office 365 Fontys\Sync\25-26\1\Dev\S6-BDA\Explorations\Unified View over Data in External Systems\Possible Solution"
.\venv\Scripts\Activate.ps1
python cust_server.py
```

You should see:
```
Customer Server starting...
Loaded 6 customers from CSV
Server running at http://localhost:5001
```

**Terminal 2 - Sales Server:**
```powershell
cd "c:\Users\Analyst\OneDrive - Office 365 Fontys\Sync\25-26\1\Dev\S6-BDA\Explorations\Unified View over Data in External Systems\Possible Solution"
.\venv\Scripts\Activate.ps1
python sales_server.py
```

You should see:
```
Sales Server starting...
Loaded 12 sales records from CSV
Server running at http://localhost:5002
```

### Step 3: Test Flask APIs (Optional)

Open a browser or use curl to test the APIs:

```powershell
# Test customer endpoint
Invoke-RestMethod http://localhost:5001/customer/012

# Test customers by city
Invoke-RestMethod http://localhost:5001/customers/city/Eindhoven

# Test sales by date range
Invoke-RestMethod "http://localhost:5002/sales?start_date=20260101&end_date=20260131"
```

### Step 4: Configure Claude Desktop

1. **Locate the config file:** Open File Explorer and navigate to:
   ```
   %APPDATA%\Claude\
   ```
   (Type this in the address bar, or navigate to `C:\Users\<YourUsername>\AppData\Roaming\Claude\`)

2. **Copy the config:** Copy `claude_desktop_config.json` from this project to the Claude folder.

   Or create/edit the file manually with this content:
   ```json
   {
     "mcpServers": {
       "sales-analysis": {
         "command": "python",
         "args": [
           "c:\\Users\\Analyst\\OneDrive - Office 365 Fontys\\Sync\\25-26\\1\\Dev\\S6-BDA\\Explorations\\Unified View over Data in External Systems\\Possible Solution\\mcp_server.py"
         ]
       }
     }
   }
   ```

3. **Restart Claude Desktop:** Close and reopen Claude Desktop to load the new configuration.

4. **Verify MCP connection:** In Claude Desktop, you should see the MCP server connection indicator (usually a small icon or status message).

## Using the MCP Tools

Once configured, you can ask Claude natural language questions about customer and sales data:

### Example Queries

**Query 1: Individual Customer Revenue**
> "What was the revenue for customer 012 in January 2026?"

Claude will use the `get_customer_revenue_by_period` tool with:
- `cust_id`: "012"
- `start_date`: "20260101"
- `end_date`: "20260131"

Expected result:
```json
{
  "custid": "012",
  "custname": "Bert",
  "city": "Eindhoven",
  "revenue": 14,
  "sales_count": 2
}
```

**Query 2: City Revenue**
> "Show me all revenue from Eindhoven in January 2026"

Claude will use the `get_city_revenue_by_period` tool with:
- `city`: "Eindhoven"
- `start_date`: "20260101"
- `end_date`: "20260131"

Expected result:
```json
{
  "city": "Eindhoven",
  "total_revenue": 47,
  "customer_count": 3,
  "customers": [
    {"custid": "011", "custname": "Annie", "revenue": 19, "sales_count": 2},
    {"custid": "012", "custname": "Bert", "revenue": 14, "sales_count": 2},
    {"custid": "016", "custname": "Fien", "revenue": 21, "sales_count": 1}
  ]
}
```

**Query 3: Comparative Analysis**
> "Compare revenue between Eindhoven and Tilburg in February 2026"

Claude will call the tool twice and compare the results.

**Query 4: Zero Revenue Period**
> "Did customer 013 have any sales in February 2026?"

## Data Files

### customers.csv
| custid | custname | city       |
|--------|----------|------------|
| 011    | Annie    | Eindhoven  |
| 012    | Bert     | Eindhoven  |
| 013    | Carla    | Helmond    |
| 014    | Dirk     | Tilburg    |
| 015    | Eric     | Tilburg    |
| 016    | Fien     | Eindhoven  |

### sales.csv
| ordid | custid | orddate  | ordamount |
|-------|--------|----------|-----------|
| 501   | 012    | 20260103 | 9         |
| 502   | 014    | 20260107 | 11        |
| 503   | 012    | 20260119 | 5         |
| 504   | 016    | 20260119 | 21        |
| 505   | 011    | 20260123 | 12        |
| 506   | 013    | 20260127 | 3         |
| 507   | 011    | 20260130 | 7         |
| 508   | 012    | 20260203 | 9         |
| 509   | 014    | 20260209 | 5         |
| 510   | 015    | 20260209 | 5         |
| 511   | 016    | 20260211 | 10        |
| 512   | 014    | 20260217 | 7         |

## Troubleshooting

### Flask servers won't start
- Check that ports 5001 and 5002 are not in use
- Verify the virtual environment is activated
- Ensure Python 3.10+ is installed

### MCP server not connecting
- Verify both Flask servers are running first
- Check the path in `claude_desktop_config.json` is correct
- Restart Claude Desktop after config changes
- Check Windows path uses double backslashes (`\\`)

### Tool returns empty results
- Verify the Flask servers are running
- Check the customer ID or city name exists in the data
- Verify the date range format is `yyyymmdd`

### Debug MCP Server
Test the MCP server directly using the MCP Inspector:
```powershell
# Make sure venv is activated
mcp dev mcp_server.py
```

## Project Files

| File | Description |
|------|-------------|
| `cust_server.py` | Flask API for customer data (port 5001) |
| `sales_server.py` | Flask API for sales data (port 5002) |
| `mcp_server.py` | MCP server with analysis tools |
| `customers.csv` | Customer master data |
| `sales.csv` | Sales transaction data |
| `requirements.txt` | Python dependencies |
| `claude_desktop_config.json` | Claude Desktop MCP configuration |
| `README.md` | This documentation |

## Learning Objectives

This project demonstrates:

1. **MCP Protocol**: How to create an MCP server that exposes tools to Claude
2. **Tool Definition**: Using `@mcp.tool()` decorator to define callable functions
3. **stdio Transport**: Communication between Claude Desktop and MCP server
4. **API Aggregation**: Combining data from multiple REST APIs
5. **Flask APIs**: Simple REST endpoints for serving CSV data
6. **Windows Integration**: Proper path handling and Claude Desktop configuration

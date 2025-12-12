## How MCP works in this sample

### How MCP Tools Advertise Functionality

When the MCP server starts, it goes through an initialization handshake with Claude Desktop:

#### 1. Tool Registration
The MCP server responds to a tools/list request by sending metadata about each tool:

```json
{
  "tools": [
    {
      "name": "get_customer_revenue_by_period",
      "description": "Get customer revenue for a specified period...",
      "inputSchema": {
        "type": "object",
        "properties": {
          "cust_id": {
            "type": "string",
            "description": "Customer ID (e.g., \"012\")"
          },
          "start_date": {
            "type": "string", 
            "description": "Start date in yyyymmdd format (e.g., \"20260101\")"
          },
          "end_date": {
            "type": "string",
            "description": "End date in yyyymmdd format (e.g., \"20260131\")"
          }
        },
        "required": ["cust_id", "start_date", "end_date"]
      }
    }
  ]
}
```

#### 2. FastMCP Extracts Metadata
In your mcp_server.py:92-110, the @mcp.tool() decorator automatically extracts:

- Function name → Tool name
- Docstring → Tool description
- Type hints → Parameter types
- Docstring Args section → Parameter descriptions

```python
@mcp.tool()
def get_customer_revenue_by_period(cust_id: str, start_date: str, end_date: str) -> str:
    """
    Get customer revenue for a specified period.  # ← Description
    
    Args:
        cust_id: Customer ID (e.g., "012")         # ← Parameter descriptions
        start_date: Start date in yyyymmdd format
        end_date: End date in yyyymmdd format
    """
```

### How the LLM Decides Which Tools to Call

#### 1. Semantic Matching
When you ask Claude a question, the LLM:

User: "What was the revenue for customer 012 in January 2026?"

LLM thinks:

- Sees "revenue for customer" → matches tool description "Get customer revenue"
- Sees "customer 012" → needs cust_id parameter
- Sees "January 2026" → needs date range → start_date and end_date

#### 2. Parameter Extraction
The LLM extracts parameters from natural language:

```json{
"customer 012 in January 2026"
    ↓
{
  "cust_id": "012",
  "start_date": "20260101",
  "end_date": "20260131"
}
```

#### 3. Tool Call
Claude sends an MCP tools/call request:

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_customer_revenue_by_period",
    "arguments": {
      "cust_id": "012",
      "start_date": "20260101",
      "end_date": "20260131"
    }
  }
}
```

#### 4. Multiple Tools
For complex queries, Claude can call multiple tools:

User: "Compare revenue between Eindhoven and Tilburg"

LLM strategy:

- Call get_city_revenue_by_period with city="Eindhoven"
- Call get_city_revenue_by_period with city="Tilburg"
- Compare results and present analysis

### Why Good Descriptions Matter
The quality of your tool descriptions directly affects LLM accuracy:

❌ Bad:

```python
@mcp.tool()
def get_rev(id: str, sd: str, ed: str) -> str:
    """Get revenue"""
```

✅ Good:

```python
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
    """
```

The detailed description and examples help the LLM:

- Understand when to use the tool
- Know what format parameters should be in
- Generate accurate tool calls

### Behind the Scenes in Your Code
The FastMCP framework in mcp_server.py:17 handles all the protocol communication automatically. You just need to write good docstrings and type hints!
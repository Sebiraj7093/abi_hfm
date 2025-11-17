import os
import asyncio
import time
import re
import asyncpg
from functools import lru_cache
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain.agents import create_agent
from typing import Dict, Tuple, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

console = Console()
load_dotenv()

# --- Global State ---
DB_POOL = None
SCHEMA_CACHE = None

DB_CONFIG = {
    "user": "avivekanandan",
    "password": "HotForex!",
    "host": "localhost",
    "database": "hfm_assistant",
    "table": "forex_trades"
}

# Pre-compiled regex patterns for speed
DANGEROUS_PATTERNS = [
    re.compile(r'\bDROP\b', re.IGNORECASE),
    re.compile(r'\bDELETE\b', re.IGNORECASE),
    re.compile(r'\bUPDATE\b', re.IGNORECASE),
    re.compile(r'\bINSERT\b', re.IGNORECASE),
    re.compile(r'\bTRUNCATE\b', re.IGNORECASE),
    re.compile(r'\bALTER\b', re.IGNORECASE),
    re.compile(r'\bCREATE\b', re.IGNORECASE),
    re.compile(r'\bGRANT\b', re.IGNORECASE),
    re.compile(r'\bREVOKE\b', re.IGNORECASE),
    re.compile(r'\bEXECUTE\b', re.IGNORECASE),
    re.compile(r'\b--\b'),
    re.compile(r'/\*'),
    re.compile(r'\bEXEC\b', re.IGNORECASE)
]

class SQLValidator:
    """Optimized validator with pre-compiled patterns."""
    
    @staticmethod
    def security_check(sql: str) -> Tuple[bool, str]:
        """Phase 1: Fast security validation with pre-compiled patterns."""
        if not sql.strip().upper().startswith('SELECT'):
            return False, "SECURITY_VIOLATION: Only SELECT queries allowed."
        
        for pattern in DANGEROUS_PATTERNS:
            if pattern.search(sql):
                return False, f"SECURITY_VIOLATION: Dangerous operation detected."
        
        if sql.strip().rstrip(';').count(';') > 0:
            return False, "SECURITY_VIOLATION: Multiple statements not allowed."
        
        return True, "OK"
    
    @staticmethod
    def intent_match_check(sql: str, user_query: str) -> Tuple[bool, str]:
        """Phase 2: Streamlined intent validation."""
        sql_upper = sql.upper()
        user_lower = user_query.lower()
        
        if 'FOREX_TRADES' not in sql_upper:
            return False, "INTENT_VIOLATION: Must reference 'forex_trades' table."
        
        # Simplified checks - only critical mismatches
        if ('profit' in user_lower or 'loss' in user_lower or 'pnl' in user_lower):
            if not any(col in sql_upper for col in ['PNL', 'PROFIT', 'LOSS', 'DAILY']):
                return False, "INTENT_VIOLATION: Missing profit/loss column."
        
        if ('percentage' in user_lower or '%' in user_lower):
            if 'COUNT' not in sql_upper or '100' not in sql:
                return False, "INTENT_VIOLATION: Percentage needs COUNT and * 100."
        
        if ('total' in user_lower or 'sum' in user_lower):
            if 'SUM(' not in sql_upper:
                return False, "INTENT_VIOLATION: Total query needs SUM()."
        
        if ('average' in user_lower or 'avg' in user_lower):
            if 'AVG(' not in sql_upper:
                return False, "INTENT_VIOLATION: Average query needs AVG()."
        
        if any(kw in user_lower for kw in ['most', 'highest', 'best', 'top']):
            if 'ORDER BY' not in sql_upper or 'DESC' not in sql_upper:
                return False, "INTENT_VIOLATION: 'Most/highest' needs ORDER BY DESC."
        
        return True, "OK"
    
    @staticmethod
    def syntax_check(sql: str) -> Tuple[bool, str]:
        """Phase 3: Fast syntax validation."""
        sql_upper = sql.upper()
        
        if 'SELECT' not in sql_upper or 'FROM' not in sql_upper:
            return False, "SYNTAX_ERROR: Missing SELECT or FROM."
        
        if sql.count('(') != sql.count(')'):
            return False, "SYNTAX_ERROR: Unbalanced parentheses."
        
        return True, "OK"
    
    @staticmethod
    def validate_complete(sql: str, user_query: str) -> Dict:
        """Fast 3-phase validation."""
        # Security check
        is_valid, msg = SQLValidator.security_check(sql)
        if not is_valid:
            return {"valid": False, "error": msg}
        
        # Intent check
        is_valid, msg = SQLValidator.intent_match_check(sql, user_query)
        if not is_valid:
            return {"valid": False, "error": msg}
        
        # Syntax check
        is_valid, msg = SQLValidator.syntax_check(sql)
        if not is_valid:
            return {"valid": False, "error": msg}
        
        return {"valid": True, "error": None}



class ChartGenerator:
    """Intelligent chart generation based on query type."""
    
    @staticmethod
    def should_visualize(user_query: str, results: List) -> bool:
        """Dual-layer visualization detection: Keywords + LLM."""
        if not results or len(results) == 0:
            return False
        
        # Single value results rarely need visualization
        if len(results) == 1 and len(results[0]) == 1:
            return False
        
        query_lower = user_query.lower()
        
        # Layer 1: Keyword-based check (fast)
        viz_keywords = [
            'trend', 'over time', 'performance', 'report',
            'last', 'months', 'weeks', 'days', 
            'compare', 'comparison', 'distribution',
            'gain', 'loss over', 'profit over',
            'daily', 'weekly', 'monthly',
            'chart', 'graph', 'visualize', 'show me',
            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
            'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
            '2024', '2023', 'period', 'from', 'to', 'top', 'list'
        ]
        
        has_viz_keywords = any(keyword in query_lower for keyword in viz_keywords)
        
        # If keywords found, return True immediately
        if has_viz_keywords:
            return True
        
        # Layer 2: LLM-based intelligent check (for edge cases)
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                max_output_tokens=10
            )
            
            columns = list(results[0].keys())
            prompt = f"Query: '{user_query}' | {len(results)} rows, columns: {columns}. Would a chart help? Answer YES/NO:"
            
            response = llm.invoke(prompt)
            return 'YES' in response.content.upper()
            
        except:
            # Fallback: multiple rows suggest potential for visualization
            return len(results) > 1
    
    @staticmethod
    def detect_chart_type(results: List, user_query: str) -> str:
        """Detect appropriate chart type based on data structure."""
        if not results:
            return None
        
        columns = list(results[0].keys())
        query_lower = user_query.lower()
        
        # Time series data
        has_date = any('date' in col.lower() or 'time' in col.lower() for col in columns)
        has_numeric = any(isinstance(results[0][col], (int, float)) for col in columns)
        
        if has_date and has_numeric:
            return 'line'
        
        # Distribution/comparison
        if 'distribution' in query_lower or 'breakdown' in query_lower:
            return 'pie'
        
        # Performance comparison
        if len(results) > 1 and len(results) < 20:
            if any(kw in query_lower for kw in ['compare', 'vs', 'versus', 'top', 'best', 'worst']):
                return 'bar'
        
        # Default for time-series like data
        if len(results) > 2:
            return 'line'
        
        return 'bar'
    
    @staticmethod
    def create_visualization(results: List, user_query: str, chart_type: str = None):
        """Create appropriate Plotly visualization."""
        if not results:
            return None
        
        if chart_type is None:
            chart_type = ChartGenerator.detect_chart_type(results, user_query)
        
        if not chart_type:
            return None
        
        columns = list(results[0].keys())
        
        # Convert results to lists
        data = {col: [row[col] for row in results] for col in columns}
        
        # Detect x and y columns
        date_col = next((col for col in columns if 'date' in col.lower() or 'time' in col.lower()), None)
        numeric_cols = [col for col in columns if isinstance(results[0][col], (int, float))]
        
        # If no numeric data, can't create meaningful charts
        if not numeric_cols and len(columns) == 1:
            return None
        
        fig = None
        
        if chart_type == 'line' and numeric_cols:
            fig = go.Figure()
            
            x_data = data[date_col] if date_col else list(range(len(results)))
            
            for col in numeric_cols:
                fig.add_trace(go.Scatter(
                    x=x_data,
                    y=data[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
            
            fig.update_layout(
                title="Performance Over Time",
                xaxis_title=date_col if date_col else "Period",
                yaxis_title="Value",
                hovermode='x unified',
                template='plotly_dark',
                height=500
            )
        
        elif chart_type == 'bar':
            x_col = columns[0]
            
            if numeric_cols:
                y_col = numeric_cols[0]
                fig = go.Figure(data=[
                    go.Bar(
                        x=data[x_col],
                        y=data[y_col],
                        marker=dict(
                            color=data[y_col],
                            colorscale='RdYlGn'
                        ),
                        text=data[y_col],
                        textposition='auto',
                    )
                ])
                
                fig.update_layout(
                    title="Performance Comparison",
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    template='plotly_dark',
                    height=500
                )
            else:
                # Count frequency for categorical data
                from collections import Counter
                counts = Counter(data[x_col])
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(counts.keys()),
                        y=list(counts.values()),
                        marker=dict(color='blue'),
                        text=list(counts.values()),
                        textposition='auto',
                    )
                ])
                
                fig.update_layout(
                    title="Frequency Distribution",
                    xaxis_title=x_col,
                    yaxis_title="Count",
                    template='plotly_dark',
                    height=500
                )
        
        elif chart_type == 'pie':
            label_col = columns[0]
            
            if numeric_cols:
                value_col = numeric_cols[0]
                fig = go.Figure(data=[
                    go.Pie(
                        labels=data[label_col],
                        values=data[value_col],
                        hole=0.3,
                        textinfo='label+percent'
                    )
                ])
            else:
                # Count frequency for categorical data
                from collections import Counter
                counts = Counter(data[label_col])
                
                fig = go.Figure(data=[
                    go.Pie(
                        labels=list(counts.keys()),
                        values=list(counts.values()),
                        hole=0.3,
                        textinfo='label+percent'
                    )
                ])
            
            fig.update_layout(
                title="Distribution Analysis",
                template='plotly_dark',
                height=500
            )
        
        return fig

# --- Database Pool Management ---
async def init_db_pool():
    """Initialize connection pool with aggressive settings."""
    global DB_POOL
    if DB_POOL is None:
        DB_POOL = await asyncpg.create_pool(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            host=DB_CONFIG["host"],
            min_size=5,
            max_size=20,
            command_timeout=3,
            max_inactive_connection_lifetime=300
        )

async def cleanup_db_pool():
    """Close pool on exit."""
    global DB_POOL
    if DB_POOL:
        await DB_POOL.close()

# --- Internal Schema Function (not a tool) ---
async def _fetch_schema() -> str:
    """Internal function to fetch and cache schema."""
    global SCHEMA_CACHE
    if DB_POOL is None:
        await init_db_pool()
    
    if DB_POOL is None:
        return "ERROR: Database not initialized"
    
    if SCHEMA_CACHE:
        return SCHEMA_CACHE
    
    async with DB_POOL.acquire() as conn:
        results = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'forex_trades'
            ORDER BY ordinal_position
        """)
    
    if not results:
        return "ERROR: Table 'forex_trades' not found"
    
    # Compact schema format
    schema = "TABLE: forex_trades\n\nCOLUMNS:\n"
    schema += "\n".join(f"  - {r['column_name']} ({r['data_type']})" for r in results)
    schema += "\n\nNOTE: Use double quotes for mixed-case columns!"
    
    SCHEMA_CACHE = schema
    return schema

# --- Optimized Tools ---
@tool("validate_and_execute")
async def validate_and_execute(sql_query: str, user_query: str, attempt: int = 1) -> str:
    """Fast validation and execution with concise output."""
    if DB_POOL is None:
        await init_db_pool()
    
    if DB_POOL is None:
        return "ERROR: Database not initialized"
    
    # Fast validation
    validation = SQLValidator.validate_complete(sql_query, user_query)
    
    if not validation["valid"]:
        return f"""VALIDATION FAILED (Attempt {attempt}/3)

{validation['error']}

ACTION: Fix the issue and retry."""
    
    # Execute query
    try:
        async with DB_POOL.acquire() as conn:
            results = await conn.fetch(sql_query)
        
        if not results:
            return "VALIDATION PASSED\nEXECUTION SUCCESSFUL\nNo results returned."
        
        # Convert to list of dicts for visualization
        results_list = [dict(row) for row in results]
        
        # Minimal formatting for speed
        columns = list(results[0].keys())
        header = " | ".join(columns)
        rows = "\n".join(" | ".join(str(row[col]) for col in columns) for row in results[:15])
        more = f"\n... +{len(results) - 15} more" if len(results) > 15 else ""
        
        output = f"""VALIDATION PASSED
EXECUTION SUCCESSFUL

{header}
{"-" * len(header)}
{rows}{more}

Rows: {len(results)}"""

        # Check if visualization is needed
        if ChartGenerator.should_visualize(user_query, results_list):
            output += "\n\n[VISUALIZATION_RECOMMENDED]"
            # Store results globally for visualization
            global LAST_QUERY_RESULTS, LAST_USER_QUERY
            LAST_QUERY_RESULTS = results_list
            LAST_USER_QUERY = user_query
        
        return output
    
    except asyncpg.exceptions.UndefinedColumnError as e:
        col_name = str(e).split('"')[1] if '"' in str(e) else "unknown"
        return f"""EXECUTION ERROR (Attempt {attempt}/3)

Column '{col_name}' not found.

SOLUTION:
1. Call get_schema for exact names
2. Use double quotes for mixed-case: "Daily_PnL"
3. Retry with corrected query"""
    
    except Exception as e:
        return f"""EXECUTION ERROR (Attempt {attempt}/3)

{str(e)}

SOLUTION: Fix SQL and retry."""

@tool("get_schema")
async def get_schema() -> str:
    """Return cached schema instantly."""
    return await _fetch_schema()

# --- Global storage for visualization ---
LAST_QUERY_RESULTS = None
LAST_USER_QUERY = None

# --- Optimized LLM Setup ---
def setup_llm():
    api_key = os.getenv("GOOGLE_API_KEY") or "AIzaSyDsxcWqWgmjfH8BqyNi4AzkWezkNXAIeWE"
    if not api_key:
        raise RuntimeError("Set GOOGLE_API_KEY")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=api_key,
        max_output_tokens=800,
        max_retries=1,
        timeout=5
    )

llm = setup_llm()
tools = [validate_and_execute, get_schema]

# --- Streamlined Agent Instructions ---
instructions = """You are a RELIABLE SQL Agent for HFM trading data. Execute with ACCURACY.

WORKFLOW:

1. SCHEMA (ALWAYS FIRST):
   - Call get_schema for every query to see exact column names
   - Use the returned schema information for accurate SQL generation

2. GENERATE SQL (One shot - be precise):
   
   Quick Patterns:
   - "profit percentage" → (COUNT(CASE WHEN "Daily_PnL" > 0 THEN 1 END) * 100.0 / COUNT(*))
   - "total profit" → SUM("Daily_PnL")
   - "most profitable" → SELECT "Symbol", "Daily_PnL" FROM forex_trades ORDER BY "Daily_PnL" DESC LIMIT 10
   - "top profitable pairs" → SELECT "Symbol", SUM("Daily_PnL") as total_profit FROM forex_trades GROUP BY "Symbol" ORDER BY total_profit DESC LIMIT 10
   - "average" → AVG("Daily_PnL")
   - "profit over time/period" → SELECT "Trade_Date", "Daily_PnL" WHERE date_range ORDER BY "Trade_Date"
   - "monthly breakdown" → SELECT DATE_TRUNC('month', "Trade_Date") as month, SUM("Daily_PnL") GROUP BY month ORDER BY month
   - "performance over time" → SELECT "Trade_Date", "Daily_PnL" FROM forex_trades ORDER BY "Trade_Date"
   
   CRITICAL:
   - Use exact column names with double quotes: "Daily_PnL"
   - Only SELECT statements
   - Include proper aggregations
   - For time-based queries, include date columns

3. VALIDATE & EXECUTE:
   - Call validate_and_execute(sql_query, user_query, attempt=1)
   - If fails, fix the specific error and retry (max 3 attempts)
   - Tool will indicate if visualization is recommended

4. RESPOND (MANDATORY):
   - After successful execution, provide a clear 1-2 sentence answer
   - Example: "Your profit percentage is 49.08%"
   - Example: "Total profit is -19765.65, so you are not profiting"
   - If [VISUALIZATION_RECOMMENDED] appears, mention that a chart has been generated

SPEED RULES:
- Generate correct SQL on first attempt
- No explanations of process
- No clarifying questions
- Max 3 tool calls (1 get_schema + 2 validate_and_execute)
- ALWAYS end with a text response after tool output

NEVER:
- Use DROP, DELETE, UPDATE, INSERT
- Forget double quotes on mixed-case columns
- End on a tool call without a final response
"""

# Create agent
agent = create_agent(
    llm,
    tools,
    system_prompt=instructions
)

# --- Optimized Main Loop ---
async def main():
    """Fast query loop with minimal overhead."""
    global LAST_QUERY_RESULTS, LAST_USER_QUERY
    
    try:
        # Pre-warm connection pool
        await init_db_pool()
        
        console.print("[bold cyan]SQL Agent with Visualization Ready![/bold cyan]")
        console.print("[dim]Type 'exit', 'quit', or 'q' to exit[/dim]\n")
        
        while True:
            query = await asyncio.to_thread(console.input, "> Query: ")
            
            if query.lower() in ['exit', 'quit', 'q']:
                break
            
            if not query.strip():
                continue
            
            start = time.perf_counter()
            console.print()
            
            # Reset visualization data
            LAST_QUERY_RESULTS = None
            LAST_USER_QUERY = None
            
            try:
                response = await agent.ainvoke({
                    "messages": [{"role": "user", "content": query}]
                })
                
                messages = response.get("messages", [])
                final_answer = ""
                attempt = 1
                
                for msg in messages[1:]:
                    role = getattr(msg, 'type', 'unknown')
                    content = getattr(msg, 'content', '')
                    
                    if role == 'ai':
                        tool_calls = getattr(msg, 'tool_calls', [])
                        
                        if tool_calls:
                            for tc in tool_calls:
                                if tc.get('name') == 'validate_and_execute':
                                    sql = tc.get('args', {}).get('sql_query', '')
                                    if sql:
                                        console.print(Panel(
                                            Syntax(sql, "sql", theme="monokai", line_numbers=False),
                                            title=f"SQL (Attempt {attempt})" if attempt > 1 else "SQL",
                                            border_style="yellow"
                                        ))
                                        attempt += 1
                        elif content:
                            final_answer = content
                    
                    elif role == 'tool':
                        if 'VALIDATION FAILED' in str(content) or 'EXECUTION ERROR' in str(content):
                            console.print(Panel(str(content), title="Error", border_style="red"))
                        elif 'EXECUTION SUCCESSFUL' in str(content):
                            # Extract data table only
                            lines = str(content).split('\n')
                            data_lines = [l for l in lines if '|' in l or '---' in l or 'Rows:' in l]
                            if data_lines:
                                console.print(Panel('\n'.join(data_lines), title="Results", border_style="green"))
                
                if final_answer:
                    console.print(Panel(final_answer, title="Answer", border_style="cyan"))
                
                # Generate visualization if recommended
                if LAST_QUERY_RESULTS and LAST_USER_QUERY:
                    try:
                        fig = ChartGenerator.create_visualization(
                            LAST_QUERY_RESULTS, 
                            LAST_USER_QUERY
                        )
                        if fig:
                            console.print("[bold green]📊 Opening visualization...[/bold green]")
                            fig.show()
                    except Exception as viz_error:
                        console.print(f"[yellow]Note: Visualization error: {viz_error}[/yellow]")
            
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
            
            elapsed = time.perf_counter() - start
            color = "green" if elapsed < 5 else "yellow" if elapsed < 8 else "red"
            console.print(f"[{color}]⏱️  {elapsed:.2f}s[/{color}]\n")
    
    finally:
        await cleanup_db_pool()

if __name__ == "__main__":
    asyncio.run(main())
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import psycopg2
import json

load_dotenv()

mcp = FastMCP(
    name= "Calculator",
    host="0.0.0.0",
    port = 8050
)

@mcp.tool()
def add(a: int, b: int) -> int:
    "This Tool is used to Add two numbers"
    return a + b

@mcp.tool()
def query_db(query: str) -> str:
    """Queries a Postgres Database and returns the output"""
    try:
        connection = psycopg2.connect(
            dbname = 'sales_data_db',
            user = "User",
            password = 'Parthiv9',
            host='localhost',
            port='5432'
        )
        print("Connection to PostgreSQL established successfully!")
        cursor = connection.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        # Format results into a list of dictionaries
        formatted_results = []
        for row in results:
            formatted_results.append(dict(zip(column_names, row)))

        print("Server: Query executed and results fetched.")
        # Return the results as a JSON string
        return json.dumps(formatted_results)
    except Exception as e:
        print(f"Error Connecting to postgres {e}")
        return f"Error executing query: {e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            print("Postgres connection closed")

if __name__ == "__main__":
    transport = "stdio"
    if transport == "stdio":
        print("Running Server with stdio transport")
        mcp.run(transport = "stdio")
    elif transport == "sse":
        print("Running Server with sse transport")
        mcp.run(transport = "sse")
    else:
        raise ValueError(f"Unknown transport: {transport}")        

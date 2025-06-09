import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json
import os
from openai import OpenAI

async def main():
    server_params = StdioServerParameters(
        command = "python",
        args = ["server.py"]
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("Available Tools")

            for tool in tools_result.tools:
                print(f"  -{tool.name}: {tool.description}")

            print("\nClient: Calling query_db tool...")
            try:
                user_query = input("Enter Your Prompt : ")
                client = OpenAI(
                    # This is the default and can be omitted
                    api_key=os.environ.get("OPENAI_API_KEY"),
                )

                response = client.responses.create(
                    model="gpt-4o",
                    instructions="""You are an expert in RDBMS and you are a professional in querying these SQL Databases. I want you to fetch the data from a postgreSQL database. I will provide the table Name and the schema of the table. Your Tassk is to write an accurate and a valid query. The Output should be a valid string.
                    Here are the details of the table
                    Table Name : sales
                    Schema of sales Table: 
                    sale_id : integer
                    product_name : string
                    category : string
                    region : string
                    quantity : integer
                    unit_price : numeric(10,2)
                    total_sale : numeric(10,2)
                    sales_rep : string
                    
                    """,
                    input=user_query,
                )

                query = response.output_text
                print(query)
                result = await session.call_tool("query_db", arguments={'query' : query[6:-3]})
                print(result)
                if result.content and result.content[0].text:
                    # The content is a list of parts, usually one text part
                    json_data = json.loads(result.content[0].text)
                    print("Client: Received query_db result:")
                    for row_data in json_data:
                        print(f"  {row_data}")
                else:
                    print("Client: query_db tool returned no content or an error.")
                    # You might want to check result.error for errors
                    if result.error:
                        print(f"Client: Tool error: {result.error.message}")

            except Exception as e:
                print(f"Client: Error calling query_db tool: {e}")

if __name__ == "__main__":
    asyncio.run(main())
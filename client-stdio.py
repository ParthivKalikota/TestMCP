import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

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
                result = await session.call_tool("query_db", arguments={'query' : 'select product_name from sales'})
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
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import requests
import os
from handlers import register_handlers
import psycopg2

load_dotenv()

mcp = FastMCP("data-mcp")

register_handlers(mcp=mcp)

notion_base_url = "https://api.notion.com/v1/databases/{DATABASE_ID}/query"

headers = {
    "Authorization": f"Bearer {os.getenv('notion_secret')}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

username = os.getenv("username")
host = os.getenv("host")
database = os.getenv("database")
password = os.getenv("password")


@mcp.tool()
def retrieve_tickets(database_id: str):
    """
    Retrieve the all tickets from the Notion database.

    Args:
        database_id (str): The ID of the Notion database.
        
    Returns:
        dict: The query result or an error message.
    """
    url = notion_base_url.format(DATABASE_ID=database_id)
    
    body = {}

    try:
        response = requests.post(url, headers=headers, json=body)
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@mcp.tool()
def postgres_data(query: str):
    """
    returns data from the postgres database based on the user question or query

    Args:
        query: PostgresSQL query for quering the database

    Returns: 
        The query result from the database
    """
    try : 
        conn = psycopg2.connect(
            port = 5432,
            host = host,
            database = database,
            password = password,
            user = username
        )
        cursor = conn.cursor()
        cursor.execute(query=query)

        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        return results

    except psycopg2.Error as e:
        return {"error": str(e)}

@mcp.prompt()
def query_prompt(question: str):
    return f"based on the question give the postgrsSQL query, use the mcp resource for getting the structre of the database. \n\n question : {question}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

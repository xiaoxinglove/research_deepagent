from dotenv import load_dotenv
import os

from tavily import TavilyClient


load_dotenv()


client = TavilyClient(
    api_key=os.getenv(
        "TAVILY_API_KEY"
    )
)


result = client.search(
    "LangChain DeepAgents",
    max_results=3
)


print(result)
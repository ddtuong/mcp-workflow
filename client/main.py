from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os
from dotenv import load_dotenv
load_dotenv()

client = MultiServerMCPClient(
    {
        "math": {
            # Make sure you start your math server on port 8000
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        },
        "weather": {
            # Make sure you start your weather server on port 8001
            "url": "http://localhost:8001/mcp",
            "transport": "streamable_http",
        }
    }
)

async def main():
    tools = await client.get_tools()
    print("List tools: ", len(tools))
    model = init_chat_model("google_genai:gemini-2.5-flash", temperature=0.0)
    agent = create_agent(
        model=model, 
        tools=tools,
        system_prompt="you are a helpful assistant that can answer user questions based on the information from the available tools.",
        )

    user_query = "what's (3 + 5) x 12?"
    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": user_query}
            ]
        })
    print("user_query: ", user_query)
    print("the answer: ", response['messages'][-1].content)

    print("=="*10)

    user_query = "what is the weather in VietNam?"
    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": user_query}
            ]
        })
    print("user_query: ", user_query)
    print("the answer: ", response['messages'][-1].content)

import asyncio
asyncio.run(main())

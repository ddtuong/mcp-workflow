from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

app = FastAPI()
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

@app.post("/invoke")
async def invoke_agent(request: QueryRequest):
    tools = await client.get_tools()
    model = init_chat_model("google_genai:gemini-2.5-flash", temperature=0.0)
    agent = create_agent(model, tools)

    response = await agent.ainvoke({
        "messages": [
            {"role": "user", "content": request.query}
            ]
        })
    return {"response": response['messages'][-1].content}


'''
LangChain code for Agent Invocation, Tavily Search tool call, Async invocation of the agent and async streaming of the agent
'''

import asyncio #async utilities

import os #import os utility
#load environment variables from the .env file
from dotenv import load_dotenv
from pydantic import SecretStr
load_dotenv()

# pip install -qU langchain "langchain[openai]" langchain-tavily
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

 # Pretty terminal formatter for the agent response (Markdown, bullets, panels)
from langchain_docs.formatting import format_response

#Prompts Message
from Prompts.System import information_research as system_information_research

# Nous Research Inference Server (OpenAI-compatible endpoint)
llm = ChatOpenAI(
    model=os.environ["NOUS_MODEL"],  # list available models: GET /v1/models on the base_url
    api_key=SecretStr(os.environ["NOUS_API_KEY"]),  # key read from the environment, set in .env
    base_url="https://inference-api.nousresearch.com/v1",
)
# Tavily web search tool (requires TAVILY_API_KEY in the environment / .env)
from langchain_tavily import TavilySearch

# Web Search tool for the LLM
# max_results caps how many search results are returned to the model
web_search = TavilySearch(max_results=1)

# Creating an Agent
# while creating an agent, this code reads the OpenAI_API_Key automatically once the environment variables are loaded,
# no explicitly supplying the same to the agent creation function

'''
Here "create_agent" call returns a LangGraph graph, which exposes async variants of every method:

- agent.invoke(...) → await agent.ainvoke(...), wrapped in an async main() run via asyncio.run()
- The event loop stays free while the agent waits on the LLM/Tavily, so you could asyncio.gather() several invocations concurrently
- Included a commented-out agent.astream(..., stream_mode="messages") variant if you want token-by-token streaming
'''

agent = create_agent(
    model=llm, # model instance pointed at the Nous Research inference server
    tools=[web_search], # tools attached
   # system_prompt="You are a helpful assistant", # system prompt for initial direction and the role play
)

# Async entry point
async def main():
    # Non-blocking invocation: agent.ainvoke() returns a coroutine, so the event loop
    # stays free while the agent waits on the LLM / tool calls (unlike .invoke())
    result = await agent.ainvoke(
        {"messages": [
            {"role": "system", "content":system_information_research}, # system prompt set explicitly on the message list
            {"role": "user", "content": "How does AI agents manage memory?"}, # user prompt
        ]}
    )

   
    format_response(result, title="AI Agents Memory Management(Tavily Search)")

    # --- Streaming variant (token-by-token, also non-blocking) ---
    # async for chunk, metadata in agent.astream(
    #     {"messages": [{"role": "user", "content": "What is the latest news about LangChain?"}]},
    #     stream_mode="messages",
    # ):
    #     print(chunk.content, end="", flush=True)

# Run the event loop
asyncio.run(main())
'''
LangChain code for simple Agent Invocation and Tool call
'''
import os #import os utility
#load environment variables from the .env file  
from dotenv import load_dotenv
from pydantic import SecretStr
load_dotenv()

# pip install -qU langchain "langchain[openai]"
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

# Get Weather tool for the LLM
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# Creating an Agent
# while creating an agent, this code reads the OpenAI_API_Key automatically once the environment variables are loaded, 
# no explciitly supplying the same to the agent creation function
# Nous Inference Server - https://inference-api.nousresearch.com/v1

agent = create_agent(
    model=llm, # model invoked
    tools=[get_weather], # tools attached
    # system_prompt="You are a helpful assistant", # system prompt for initial direction and the role play
)

#Invoking an agent asynchronously
result = agent.invoke(
    {"messages": [
        {"role": "system", "content":system_information_research}, # system prompt set explicitly on the message list
        {"role": "user", "content": "What's the weather in San Francisco?"}, # user prompt
    ]}
)

#printing result
format_response(result, title="Agent Response")
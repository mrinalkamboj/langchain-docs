import os #import os utility

#load environment variables from the .env file  
from dotenv import load_dotenv
load_dotenv()

#pydantic conversion of string usiong Secret 
from pydantic import SecretStr

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_docs.prompts.tools import AGENT_TOOLS

# Markdown output directory (relative to the parent directory of this file)
MARKDOWN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "markDown/docs")

llm = ChatOpenAI(
    model=os.environ["NOUS_MODEL"],  # list available models: GET /v1/models on the base_url
    api_key=SecretStr(os.environ["NOUS_API_KEY"]),  # key read from the environment, set in .env
    base_url="https://inference-api.nousresearch.com/v1",
)

agent = create_agent(
    model=llm, # model invoked
    tools=AGENT_TOOLS, # tools attached
    # system_prompt="You are a helpful assistant", # system prompt for initial direction and the role play
)
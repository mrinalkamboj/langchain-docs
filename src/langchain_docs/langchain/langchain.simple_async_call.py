'''
LangChain code for simple Agent Invocation and Tool call
'''

#import agent
from langchain_docs.langchain.init import agent

# System Prompt Message
from langchain_docs.prompts.system import information_research as system_information_research
from langchain_docs.prompts.user import get_user_question
# Pretty terminal formatter for the agent response (Markdown, bullets, panels)
from langchain_docs.response.formatting import format_response

#Invoking an agent asynchronously
result = agent.invoke(
    {"messages": [
        {"role": "system", "content":system_information_research}, # system prompt set explicitly on the message list
        {"role": "user", "content": get_user_question()}, # user prompt
    ]}
)

#printing result
format_response(result, title="Agent Response")
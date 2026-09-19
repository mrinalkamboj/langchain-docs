'''
LangChain code for Agent Invocation, Tavily Search tool call, Async invocation of the agent and async streaming of the agent
'''

import asyncio #async utilities
import os
from langchain_core.messages import AIMessageChunk

#import agent
from langchain_docs.langchain.init import agent, MARKDOWN_DIR

# System Prompt Message
from langchain_docs.prompts.system import information_research as system_information_research
from langchain_docs.prompts.user import get_user_question
# unique hash of the question, registered in the markdownhash set
from langchain_docs.markdown.code.markdownhash import register_question_hash
# Pretty terminal formatter for the agent response (Markdown, bullets, panels)
from langchain_docs.response.formatting import format_response

# User prompt asked to the agent: override_question wins when set, else random pick from the pool
user_question = get_user_question()

# Common filler words dropped when building the short-form file name
_STOP_WORDS = {"how", "does", "do", "the", "a", "an", "is", "are", "what", "why",
               "in", "on", "of", "to", "and", "for", "with", "about", "can", "ai"}

def short_name_from_question(question: str) -> str:
    """Build a 2-3 word short form of the question, joined with underscores."""
    words = [w.strip("?!.,:'\"") for w in question.split()]
    words = [w.lower() for w in words if w and w.lower() not in _STOP_WORDS]
    return "_".join(words[:3]) or "response"

def save_response_markdown(question: str, response_text: str) -> str:
    """Save question + response to a uniquely named markdown file.

    Returns the file path, or "" when the question was already saved (hash dedupe).
    """
    questionsummary = short_name_from_question(question)
    
    if not register_question_hash(question,questionsummary):
        print("Question already saved earlier (hash match) — skipping markdown file creation")
        return ""

    os.makedirs(MARKDOWN_DIR, exist_ok=True)
    file_path = os.path.join(MARKDOWN_DIR, f"{short_name_from_question(question)}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# Question\n\n{question}\n\n# Response\n\n{response_text}\n")
    print(f"Response saved to: {file_path}")
    return file_path

def response_text(result) -> str:
    """Extract the plain markdown text of the final agent message."""
    blocks = getattr(result, "content_blocks", None) or []
    if blocks:
        return "\n\n".join(b["text"] for b in blocks if b.get("type") == "text")
    return str(result.content)

# Async entry point
async def main(stream=True,save_file_flag=True):
    # Non-blocking invocation: agent.ainvoke() returns a coroutine, so the event loop
    # stays free while the agent waits on the LLM / tool calls (unlike .invoke())

    # Model Call (Async)
    result = None
    if not stream:
        result = await agent.ainvoke(
            {"messages": [
                {"role": "system", "content":system_information_research}, # system prompt set explicitly on the message list
                {"role": "user", "content": user_question}, # user prompt
            ]}
        )
    else:
    # --- Streaming variant (token-by-token, also non-blocking) ---
        streamed_result = None
        async for chunk, metadata in agent.astream(
            {"messages": [
                {"role": "system", "content":system_information_research}, # system prompt set explicitly on the message list
                {"role": "user", "content": user_question}
            ]
        },
        stream_mode="messages",
    ):
            if isinstance(chunk, AIMessageChunk):
                print(chunk.content, end="", flush=True)
                if streamed_result is None or not isinstance(streamed_result, AIMessageChunk) or getattr(streamed_result, "id", None) != getattr(chunk, "id", None):
                    streamed_result = chunk
                else:
                    streamed_result = streamed_result + chunk
        result = streamed_result

    if result:
        format_response({"messages": [result]}, title="AI Agents Memory Management(Tavily Search)", question=user_question)

        # Save question + response as markdown when the flag is set
        if save_file_flag:
            save_response_markdown(user_question, response_text(result))

# Run the event loop
asyncio.run(main())
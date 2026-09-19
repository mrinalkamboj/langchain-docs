'''
Collection of user questions for the agent, plus an optional manual override.

- QUESTIONS: pool of questions one of which is picked at random at run time
- override_question: when set (not None), it takes precedence over the random pick
- get_user_question(): resolves the question to ask using the rules above
'''
import random

# Pool of user questions to randomly choose from
# dict(str, list[str])
QUESTIONS  = {
    "ai" : [
    "How does AI agents manage memory?",
    "What is the latest news about LangChain?",
    "How do LangGraph agents handle tool calling?",
    "What are the best practices for designing multi-agent systems?",
    "How does retrieval augmented generation (RAG) work?",
    "What is the difference between fine-tuning and prompt engineering?",
],
 "weather" : [
    "What is the weather like in San Francisco?",
    "What is the weather like in New York?",
    "What is the weather like in London?",
    "What is the weather like in Paris?",
    "What is the weather like in Tokyo?",
    "What is the weather like in Sydney?",
],
 "calculation" : [
    "What is the square root of 144?",
    "What is the cube root of 216?",
    "What is the 2 to the power of 4?",
    "What is the log of 100 to the base 10?",
    "What is the sine of 90 degrees?",
    "What is the cosine of 60 degrees?",
    "What is the tangent of 45 degrees?",
    "What is the exponential of 2?",
    "What is the absolute value of -10?",
    "What is the round of 10.5?",
    "What is the value of pi?",
    "What is the value of e?",
],
"gk": [
    "What is the capital of France?",
    "What is the currency of Japan?",
    "What is the largest mammal on Earth?",
    "What is the smallest country in the world?",
    "What is the highest mountain in the world?",
    "What is the longest river in the world?",
    "What is the largest ocean in the world?",
    "What is the smallest ocean in the world?",
    "What is the largest desert in the world?",
    "What is the smallest desert in the world?",
]
}

# Manual override: when not None, this question is used instead of a random pick
override_question: str | None = None


def get_user_question() -> str:
    """Return override_question if set, else a random question from QUESTIONS."""
    if override_question is not None:
        return override_question
    question_key =  random.choice(list(QUESTIONS.keys()))
    random_question = random.choice(QUESTIONS[question_key])
    return random_question

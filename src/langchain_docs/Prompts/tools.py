'''
Tool definitions for the LangChain agent.

All tool callables are collected here so the agent script just imports
AGENT_TOOLS and passes them to create_agent(tools=AGENT_TOOLS).

Each tool has a clear name and a detailed docstring - LangChain turns the
function name into the tool name and the docstring into the tool description
the LLM reads to decide when (and how) to call the tool.
'''
import ast
import math
import operator

from langchain_core.tools import tool

import os #import os utility
#load environment variables from the .env file
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Placeholder API key for the weather provider (e.g. OpenWeatherMap).
# Fill this in or export WEATHER_API_KEY in the environment / .env file.
# ---------------------------------------------------------------------------
WEATHER_API_KEY: str | None = os.environ["WEATHER_API_KEY"]  # TODO: placeholder - put your weather API key here


# ---------------------------------------------------------------------------
# Web search tool
# ---------------------------------------------------------------------------
# Tavily web search tool (requires TAVILY_API_KEY in the environment / .env)
from langchain_tavily import TavilySearch

# max_results caps how many search results are returned to the model
web_search = TavilySearch(max_results=3)


# ---------------------------------------------------------------------------
# Weather tool (API call with a placeholder API key)
# ---------------------------------------------------------------------------
@tool
def get_weather(city: str) -> str:
    """Get the current weather conditions (temperature, humidity, sky state, wind)
    for a given city anywhere in the world.

    Use this tool whenever the user asks about the weather, temperature,
    forecast or climate conditions in a specific location. The city name
    should be plain text, e.g. 'San Francisco' or 'London'. Requires a valid
    weather provider API key (WEATHER_API_KEY) to perform the live API call.
    """
    if not WEATHER_API_KEY:
        return ("Weather lookup unavailable: no API key configured. "
                "Set WEATHER_API_KEY in Prompts/Tools.py or the environment.")

  #  --- Real API call (OpenWeatherMap-style, untested without a key) ---
    import requests
    url = "https://api.openweathermap.org/data/2.5/weather"
    resp = requests.get(url, params={"q": city, "appid": WEATHER_API_KEY, "units": "metric"}, timeout=10)
    data = resp.json()
    if resp.status_code != 200:
        return f"Weather lookup failed for '{city}': {data.get('message', resp.status_code)}"
    main = data["main"]; wind = data["wind"]; sky = data["weather"][0]["description"]
    return (f"Weather in {city}: {sky}, {main['temp']}°C "
            f"(feels like {main['feels_like']}°C), humidity {main['humidity']}%, "
            f"wind {wind.get('speed', 0)} m/s")

    # # Placeholder response until the API key is configured
    # return f"It's always sunny in {city}! (placeholder - configure WEATHER_API_KEY for live data)"


# ---------------------------------------------------------------------------
# Calculator tool
# ---------------------------------------------------------------------------
# Supported arithmetic operators
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Math functions / constants the calculator recognises
_ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "log2": math.log2,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "exp": math.exp, "abs": abs, "round": round,
    "pi": math.pi, "e": math.e,
}


def _safe_eval(node):
    """Recursively evaluate an AST node using only whitelisted operations."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in _ALLOWED_FUNCTIONS:
        return _ALLOWED_FUNCTIONS[node.id]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCTIONS:
        return _ALLOWED_FUNCTIONS[node.func.id](*[_safe_eval(a) for a in node.args])
    raise ValueError(f"Unsupported expression element: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the numeric result.

    Handles all basic arithmetic (+, -, *, /, //, %, **) plus common math
    functions: sqrt, log, log10, log2, sin, cos, tan, exp, abs, round, and
    the constants pi and e. Examples of valid expressions:
    '2 + 3 * 4', '(18 / 3) ** 2', 'sqrt(144) + log(100)', 'round(pi, 4)'.

    Use this tool whenever the user asks for any calculation - adding,
    subtracting, multiplying, dividing, percentages, powers, roots, trig
    or logarithms - instead of computing the answer yourself, to guarantee
    arithmetic accuracy. The input must be a single Python-style arithmetic
    expression as a plain string, not natural language.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return f"{expression} = {result}"
    except ZeroDivisionError:
        return f"Error: division by zero in expression '{expression}'"
    except Exception as exc:
        return f"Error: could not evaluate '{expression}' ({exc})"


# ---------------------------------------------------------------------------
# Python code execution tool
# ---------------------------------------------------------------------------
@tool
def python_executor(code: str) -> str:
    """Execute a short snippet of Python code and return its printed output.

    Use this tool when the task requires running actual Python code - data
    processing, string or list manipulation, date/time computations, quick
    simulations, verifying logic, or anything the calculator tool cannot
    express. The code runs in an isolated namespace with no access to the
    file system or network; anything the snippet `print()`s is captured and
    returned (stdout only). The final expression value is also returned if
    there are no prints. Keep the snippet self-contained and fast (< a few
    seconds). Example input: "print(sum(range(1, 101)))".
    """
    import contextlib
    import io

    stdout = io.StringIO()
    try:
        # isolated namespace: no imports of the host module state leak in
        namespace: dict = {"__builtins__": __builtins__}
        with contextlib.redirect_stdout(stdout):
            exec(code, namespace)  # noqa: S102 - deliberate, sandboxed-by-convention tool
        output = stdout.getvalue().strip()
        if not output:
            # no prints: fall back to the value of the last expression, if any
            try:
                output = repr(eval(code.splitlines()[-1], namespace))
            except Exception:
                output = "(no output produced)"
        return output
    except Exception as exc:
        return f"Error executing code: {type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# All tools exposed to the agent
# ---------------------------------------------------------------------------
AGENT_TOOLS = [web_search, get_weather, calculator, python_executor]

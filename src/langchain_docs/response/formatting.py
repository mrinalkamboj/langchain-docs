'''
Text formatter for agent responses.

Renders the raw model output (which is usually Markdown with bullet points,
headers, bold text, etc.) neatly in the terminal instead of dumping the
raw content_blocks structure.
'''
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

_console = Console()


def format_response(result: dict, title: str = "Agent Response", question: str | None = None) -> None:
    """Pretty-print the final agent response from a create_agent result dict.

    - Renders Markdown (bullets, headers, bold, code blocks) natively
    - Falls back to plain text for non-text content blocks
    - Wraps everything in a titled panel with a subtle border
    - Optionally shows the user question asked, above the answer
    """
    final_message = result["messages"][-1]
    blocks = getattr(final_message, "content_blocks", None) or []

    _console.print()
    _console.rule(f"[bold cyan]{title}[/bold cyan]")
    _console.print()

    if question:
        _console.print(Panel(question, title="Question Asked", border_style="green"))
        _console.print()

    if not blocks:
        # Simple string content (no structured blocks)
        _console.print(Panel(Markdown(str(final_message.content)), border_style="cyan"))
        return

    for block in blocks:
        block_type = block.get("type")
        if block_type == "text":
            _console.print(Panel(Markdown(block["text"]), border_style="cyan"))
        else:
            # Any non-text block (tool calls, citations, etc.) shown as key-value details
            details = Text()
            for key, value in block.items():
                details.append(f"{key}: ", style="bold yellow")
                details.append(f"{value}\n")
            _console.print(Panel(details, title=block_type or "detail", border_style="dim"))

"""Rich CLI interface for the personal assistant."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print as rprint

console = Console()


def print_welcome():
    console.print(Panel(
        "[bold cyan]Personal AI Assistant[/bold cyan]\n"
        "Commands: [yellow]/reset[/yellow] clear memory  |  "
        "[yellow]/index <path>[/yellow] add doc to knowledge base  |  "
        "[yellow]/voice[/yellow] speak input  |  "
        "[yellow]/docs[/yellow] list indexed docs  |  "
        "[yellow]/exit[/yellow] quit",
        expand=False,
    ))


def print_response(text: str):
    console.print(Markdown(text))
    console.print()


def get_input(voice_mode: bool = False) -> str:
    if voice_mode:
        from tools.voice import listen
        text = listen()
        console.print(f"[dim]You (voice): {text}[/dim]")
        return text
    return Prompt.ask("[bold green]You[/bold green]")


def run_cli(voice_output: bool = False):
    from core.agent import PersonalAssistant
    from rag.document_store import index_document, list_indexed_documents

    assistant = PersonalAssistant()
    print_welcome()

    while True:
        try:
            user_input = get_input()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break

        if not user_input.strip():
            continue

        # Handle slash commands
        if user_input.startswith("/exit"):
            console.print("[dim]Goodbye![/dim]")
            break
        elif user_input.startswith("/reset"):
            assistant.reset()
            console.print("[yellow]Memory cleared.[/yellow]")
            continue
        elif user_input.startswith("/docs"):
            docs = list_indexed_documents()
            if docs:
                console.print("[cyan]Indexed documents:[/cyan]")
                for d in docs:
                    console.print(f"  • {d}")
            else:
                console.print("[yellow]No documents indexed yet. Use /index <path>[/yellow]")
            continue
        elif user_input.startswith("/index "):
            path = user_input[7:].strip()
            with console.status(f"Indexing {path}..."):
                result = index_document(path)
            console.print(f"[green]{result}[/green]")
            continue
        elif user_input.startswith("/voice"):
            from tools.voice import listen
            user_input = listen()
            if user_input.startswith("[voice]"):
                console.print(f"[red]{user_input}[/red]")
                continue
            console.print(f"[dim]You (voice): {user_input}[/dim]")

        with console.status("[dim]Thinking...[/dim]"):
            response = assistant.chat(user_input)

        print_response(response)

        if voice_output:
            from tools.voice import speak
            speak(response)

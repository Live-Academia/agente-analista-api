from __future__ import annotations

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

app = typer.Typer(
    name="deep-agent",
    help="Deep Agent - Análise de dados inteligente com IA",
)
console = Console()


@app.command()
def analyze(
    file: str = typer.Argument(..., help="Caminho para o arquivo CSV ou Excel"),
    question: str | None = typer.Option(
        None, "--question", "-q", help="Pergunta específica sobre os dados"
    ),
):
    """Analisa um arquivo de dados e gera um relatório ou responde uma pergunta."""
    from deep_agent.graph import build_graph

    mode = "qa" if question else "report"

    console.print(
        Panel(
            f"[bold]Deep Agent[/bold] — Modo: {'Q&A' if mode == 'qa' else 'Relatório'}\n"
            f"Arquivo: {file}",
            title="🔍 Análise de Dados",
        )
    )

    with console.status("[bold green]Processando..."):
        graph = build_graph()
        result = graph.invoke(
            {
                "file_path": file,
                "user_question": question,
                "mode": mode,
                "insights": [],
                "patterns": [],
            }
        )

    if result.get("error"):
        console.print(f"\n[bold red]Erro:[/bold red] {result['error']}")
        raise typer.Exit(1)

    if mode == "report":
        console.print()
        console.print(Markdown(result["report"]))
        console.print("\n[green]Relatório salvo na pasta output/[/green]")
    else:
        console.print()
        console.print(Panel(result["qa_answer"], title="Resposta"))


@app.command()
def chat(
    file: str = typer.Argument(..., help="Caminho para o arquivo CSV ou Excel"),
):
    """Sessão interativa de perguntas e respostas sobre um arquivo de dados."""
    from deep_agent.chains.qa import qa_node
    from deep_agent.graph import build_graph
    from deep_agent.nodes.analyze import analyze_node
    from deep_agent.nodes.ingest import ingest_node

    console.print(
        Panel(
            f"[bold]Deep Agent[/bold] — Modo Chat Interativo\nArquivo: {file}",
            title="💬 Chat com Dados",
        )
    )

    # Executar ingestão e análise uma única vez
    with console.status("[bold green]Carregando e analisando dados..."):
        state = {
            "file_path": file,
            "user_question": None,
            "mode": "qa",
            "insights": [],
            "patterns": [],
        }
        state.update(ingest_node(state))

        if state.get("error"):
            console.print(f"\n[bold red]Erro:[/bold red] {state['error']}")
            raise typer.Exit(1)

        state.update(analyze_node(state))

    shape = state.get("data_summary", {}).get("shape", {})
    console.print(
        f"\n[green]Dados carregados:[/green] {shape.get('rows', '?')} linhas, "
        f"{shape.get('columns', '?')} colunas"
    )
    console.print("Digite suas perguntas (ou 'sair' para encerrar):\n")

    while True:
        try:
            question = console.input("[bold blue]Pergunta>[/bold blue] ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not question or question.lower() in ("sair", "exit", "quit"):
            console.print("\n[yellow]Até logo![/yellow]")
            break

        state["user_question"] = question

        with console.status("[bold green]Pensando..."):
            result = qa_node(state)

        console.print()
        console.print(Panel(result["qa_answer"], title="Resposta"))
        console.print()


if __name__ == "__main__":
    app()

from pathlib import Path
from typing import Optional, cast

from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
import typer

from nsql import console, parser
from nsql.utils import (
    complete_env,
    create_env,
    get_config_path,
    get_env_creds,
    get_envs,
    save_envs,
)
from nsql.xog import (
    Databases,
    Format,
    QueryID,
    XOG,
    Writer,
)


app = typer.Typer(name="nsql", pretty_exceptions_show_locals=False)

runner = typer.Typer()

creds = typer.Typer()

app.add_typer(runner, name="run", help="Runs NSQL")
app.add_typer(creds, name="credentials", help="Manages credentials")


@app.command(
    short_help="Converts SQL to NSQL.",
    help="""
Converts SQL to NSQL.\n
Some limitations apply:\n
    - The SQL MUST have a WHERE clause.\n
    - The SQL should not have any sub-queries/function calls inside SELECT.\n
    - CTEs are prohibited. NSQL doesn't permit any kind of code before the SELECT keyword.
""",
)
def convert(
    sql: Path = typer.Argument(..., exists=True, readable=True),
    output: typer.FileTextWrite = typer.Option(
        "-", "--output", "-o", help="Save nsql to FILENAME.", writable=True
    ),
):
    with sql.open("r") as f:
        output.write(parser.sql_to_nsql(f))


@creds.command()
def new(name: str, env_url: str, username: str, password: str):
    """
    Adds a new environment to the application's config file.
    """
    path = get_config_path()
    envs = get_envs(path)
    if name in envs:
        if not Confirm.ask(
            "This will replace an existing env. Are you sure you want to continue?",
            default=True,
        ):
            raise typer.Abort()
    create_env(envs, name, env_url, username, password)
    save_envs(envs, path)
    console.log(f"Saved env {name} -> {env_url}. 🚀")


@runner.command(name="id")
def run_with_id(
    query_id: str = typer.Argument(..., help="NSQL Query ID"),
    env: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment name.",
        autocompletion=complete_env,
    ),
    output: typer.FileTextWrite = typer.Option(
        "-",
        "--output",
        "-o",
        help="Save output to FILENAME.",
        writable=True,
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-n",
        help="Limit output to n lines.",
        writable=True,
    ),
    format: Format = typer.Option(
        Format.table, "--format", "-f", case_sensitive=False, show_choices=True
    ),
    xog: str = typer.Option(None, hidden=True, lazy=True),
):
    """
    Runs a query on the specified ENV and writes it to STDOUT or OUTPUT.
    """
    if format is Format.table and not output.isatty():
        raise typer.BadParameter(
            f"Format: {Format.table} is not compatible if output is not STDOUT\nOutput: {output.name}."
        )
    env_url, username, passwd = get_env_creds(env)
    xog_c = cast(XOG, xog)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as p, (xog_c or XOG(env_url, username, passwd)) as client:
        p.add_task(description="Running query...")
        query_id = QueryID(query_id)

        result = client.run_query(query_id)[:limit]
        # if output is not stdout
        p.add_task(description=f"Writing {len(result)} lines to {output.name}...")
        Writer(output, format, console).write(query_id, result)


@runner.command()
def file(
    nsql_path: typer.FileText = typer.Argument(
        ..., help="NSQL code file path.", exists=True, readable=True
    ),
    db: Databases = typer.Option(
        Databases.niku,
        "--db",
        "-d",
        show_choices=True,
        case_sensitive=False,
        help="Database ID in which the query is supposed to run on.",
    ),
    env: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment name.",
        autocompletion=complete_env,
    ),
    output: typer.FileTextWrite = typer.Option(
        "-",
        "--output",
        "-o",
        help="Save output to FILENAME.",
        writable=True,
    ),
    format: Format = typer.Option(
        Format.table, "--format", "-f", case_sensitive=False, show_choices=True
    ),
    limit: Optional[int] = typer.Option(
        None,
        "--limit",
        "-n",
        help="Limit output to n lines.",
        writable=True,
    ),
    launch: bool = typer.Option(False, "--launch", "-l", help="Open the CSV"),
):
    """
    XOGs and runs a file to ENV and writes it to STDOUT or OUTPUT.
    """
    if output.isatty() and launch:
        console.log(
            "--launch and --output = (STDIN or -) are not compatible.", style="red"
        )
        raise typer.Abort()

    env_url, username, passwd = get_env_creds(env)

    if nsql_path.isatty():
        console.print("Copy & paste your NSQL")

    nsql = parser.sql_to_nsql(nsql_path)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
        console=console,
    ) as p, XOG(env_url, username, passwd) as client:
        p.add_task(description="Uploading query...")
        query_id = client.upload_query(nsql, db)
        p.stop()
        run_with_id(query_id, env, output, limit, format, xog=cast(str, client))
    console.log("Done!")


@runner.command()
def wsdl(
    query_id: str = typer.Argument(..., help="NSQL Query ID"),
    env: Optional[str] = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment name.",
        autocompletion=complete_env,
    ),
):
    env_url, username, passwd = get_env_creds(env)
    with XOG(env_url, username, passwd) as xog:
        xog.query_types(QueryID(query_id))


@app.command(help="Highlights SQL")
def highlight(
    query: Path = typer.Argument(..., exists=True),
    line_numbers: bool = typer.Option(False, "-n"),
):
    from rich.syntax import Syntax

    syntax = Syntax.from_path(str(query), lexer="sql", line_numbers=line_numbers)
    console.print(syntax)


if __name__ == "__main__":
    app(prog_name="nsql")
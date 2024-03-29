from pathlib import Path
from typing import Optional

from rich.columns import Columns
from rich.panel import Panel
from rich.rule import Rule
import typer

from cautils import APP_NAME, err_console
from cautils import opts
from cautils.credentials import app as creds
from cautils.exceptions import XogException
from cautils.queries import queries
from cautils.thin_xml import Xml
from cautils.utils import get_env_creds
from cautils.xog import XOG

app = typer.Typer(
    name=APP_NAME,
    pretty_exceptions_show_locals=False,
    no_args_is_help=True,
    add_completion=True,
)


app.add_typer(queries, name="query", help="N/SQL utils")
app.add_typer(creds, name="credentials", help="Manages credentials")


def print_header(env_url: str, input_file: str, output_file: str, title: str = "XOG"):
    panel = Columns(
        [
            Panel.fit(env_url, title="URL"),
            Panel.fit(Path(input_file).absolute().as_uri(), title="Input file"),
            Panel.fit(Path(output_file).absolute().as_uri(), title="Output file"),
        ],
        expand=True,
        align="center",
    )
    err_console.print(Rule(title))
    err_console.print(panel, style="green")


def print_xml_preview(
    xml: Xml, limit: Optional[int] = None, subtitle: Optional[str] = None
):
    if not limit:
        return
    err_console.print(
        Panel.fit(
            xml.syntax(limit),
            title="Input preview",
            subtitle=subtitle,
            style="green",
        )
    )


@app.command(short_help="Run a XOG")
def xog(
    input_file: typer.FileText = typer.Argument(
        ..., readable=True, dir_okay=False, exists=True
    ),
    env: str = opts.EnvOpt,
    output: typer.FileTextWrite = opts.OutputOpt,
    timeout: float = opts.TimeoutOpt,
    preview_lines: Optional[int] = typer.Option(
        30,
        "--preview-lines",
        "-n",
        help="Preview n lines of the input file.",
    ),
) -> None:
    env_url, username, passwd = get_env_creds(env)
    print_header(env_url, input_file.name, output.name)

    with err_console.status("Reading XOG..."), input_file as f:
        xml = Xml.read(f)

    if preview_lines:
        print_xml_preview(xml, preview_lines, input_file.name)

    action = (
        header[0].get("action", "?") if (header := xml.xpath("//Header")) else "read"
    )

    with err_console.status(f"Running {action} XOG..."), XOG(
        env_url, username, passwd, timeout=timeout
    ) as client:
        try:
            resp = client.send(xml)
        except XogException as e:
            # Catch the exception so we can save it to the output file.
            err_console.print_exception()
            resp = e.raw

    with err_console.status("Writing output file..."):
        written = resp.write_to(output)
    err_console.log(f"Wrote {written} bytes")


if __name__ == "__main__":
    app(prog_name=APP_NAME)

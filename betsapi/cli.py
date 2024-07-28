import typer
from rich.console import Console
from betsapi import (
    __app_name__,
    __version__
)
from typing import Annotated, Optional
import betsapi.layout as lt
import betsapi.config as conf
from betsapi.links import main_links
from betsapi.table import main_tables, create_table
from betsapi.utils import compose
from functools import partial


app = typer.Typer()
terminal = Console()


def version(value: bool) -> None:
    if value:
        terminal.print(f'{__app_name__} v{__version__}')
        raise typer.Exit()


typer_version = Annotated[   
    Optional[bool],
    typer.Option(
        '--version', '-v',
        callback=version,
        is_eager=True,
        help='versao do sistema'
    )
]

type_start = Annotated[
    int,
    typer.Option(
        '--start',
        '-s',
        help='pagina inicial'
    )
]

type_end = Annotated[
    int,
    typer.Option(
        '--end',
        '-e',
        help='pagina final'
    )
]

type_url = Annotated[
    str,
    typer.Argument(
        help='link da pagina de download'
    )
]


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: typer_version = None
) -> None:
    """
    Sistema para download de .xlsx

    referente ao site https://pt.betsapi.com
    """
    
    if ctx.invoked_subcommand:
        return

    lt.msg_callback(terminal)


@app.command(
    help='Inicializa as configurações do sistema'
)
def init(
    version: typer_version = None
):
    
    data = lt.input_start_json(terminal)
    file = conf.init_start_json(**data)

    if not file:
        lt.msg_error(terminal, 'Erro na configuração do arquivo !')
        raise typer.Exit()
    
    lt.msg_error(terminal, "Arquivo configurado com sucesso !", 'ok')


@app.command(
    help='Exporta os dados a partir de um intervalo de paginas'
)
def page(
    start: type_start = 1,
    end: type_end = 5,
    version: typer_version = None
):
    try:
        if not conf.is_start_json():
            lt.msg_error(terminal, "Arquivo de config não existe !")
            raise typer.Exit()
        
        data = conf.read_start_json()

        terminal.rule("AUTENTICAÇÃO - headers", style='magenta', characters='*')
        terminal.log(f'🔐 Gerando arquivo de autenticação')

        # NOTE: Cria o arquivo de cookie
        headers = conf.main_heades(data['email'], data['login'])
        terminal.log(f'🔑 Autenticação GITHUB - [b blue]OK[/], "{data["email"]}"')
        terminal.print()

        with terminal.status(
            '[gray50] download em andamento[/]', 
            spinner='aesthetic', 
            spinner_style='red'
        ) as sta:
                
            # NOTE: Pesquisa e exporta as tabelas
            terminal.rule("LOGS - page", style='magenta', characters='*')
            terminal.log(f'📕 Intervalo de paginas {start} - {end}')
            main_gera_base = compose(
                partial(main_links, terminal, headers),
                partial(main_tables, terminal, headers)
            )

            main_gera_base((start, end))

    except Exception as e:
        lt.msg_error(terminal, "Falha no Web Scraping")
        raise typer.Exit()


@app.command(
    help='Exporta os dados a partir de um link'
)
def link(
    url: type_url,
    version: typer_version = None
):
    try:
        if not conf.is_start_json():
            lt.msg_error(terminal, "Arquivo de config não existe !")
            raise typer.Exit()
        
        data = conf.read_start_json()

        terminal.rule("AUTENTICAÇÃO - headers", style='magenta', characters='*')
        terminal.log(f'🔐 Gerando arquivo de autenticação')

        # NOTE: Cria o arquivo de cookie
        headers = conf.main_heades(data['email'], data['login'])
        terminal.log(f'🔑 Autenticação GITHUB - [b blue]OK[/], "{data["email"]}"')
        terminal.print()

        with terminal.status(
            '[gray50] download em andamento[/]', 
            spinner='aesthetic', 
            spinner_style='red'
        ) as sta:
                
            # NOTE: Pesquisa e exporta as tabelas
            terminal.rule("LOGS - url", style='magenta', characters='*')
            terminal.log(f'🚀 URL - {url}')
            create_table(terminal, headers, url)
            
    except Exception as e:
        lt.msg_error(terminal, e)
        raise typer.Exit()
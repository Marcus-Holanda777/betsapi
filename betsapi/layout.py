from rich.console import Console
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from typing import Literal
from rich.prompt import Prompt


DEFAULT_BOX = box.ASCII2


def msg_callback(
    terminal: Console
) -> None:
    
    MARKDOWN = """
# Web scraping API BETSAPI

O aplicativo tem como objetivo coletar informações da página [https://pt.betsapi.com](https://pt.betsapi.com), 
como partidas, horários, odds e outros dados relevantes, utilizando técnicas de web scraping.

---

## Como usar ?

```diff
- O site exige autenticação e gerenciamento de cookies, por isso a cada execução será gerado um novo arquivo `json` com o `Headers` atualizado.
```

Para usar, basta chamar o app `betsapi`, e depois digitar os comandos.

1. init
> Faz a configuração inicial do programa.
```js
init options: --version -v, --help -h
```

2. page
> Exporta os dados a partir de um intervalo de `paginas`.
```js
page options: --start -s, --end -e, --version -v, --help -h
```

3. link
> Exporta os dados a partir de um link.
```js
link args: url [required], options: --version -v, --help -h
```

Des. Marcus Holanda
"""

    md = Markdown(MARKDOWN, code_theme="monokai")
    terminal.print(
        '[b yellow]Use[/] '
        'os comando: '
        '[[b blue]init[/]], '
        '[[b red]page[/]] ou '
        '[[b red]link[/]]'
        '[b cyan] --help[/] para ajuda'
    )
    terminal.print(md)

def msg_error(
    terminal: Console,
    msg: str,
    tips: Literal['erro', 'ok'] = 'erro',
    justify: str = None
) -> None:
    
    if tips == 'erro':
        emoji = 'warning'
        color = 'red'
    else:
        emoji = 'muscle'
        color = 'green'
    
    terminal.print(
        Panel.fit(
            f':{emoji}:  {msg}',
            box=DEFAULT_BOX, 
            title=tips.upper(),
            border_style=color
        ),
        justify=justify
    )


def input_start_json(
    terminal: Console
) -> dict:
    
    import re

    email = None
    login = None

    compile_email = re.compile(
        r'''
        ([A-Za-z0-9]+[.-_])* # Zero ou, letras ou numeros terminando com .-_ 
        [A-Za-z0-9]+         # Letras ou numeros
        @
        [A-Za-z0-9-]+        # letras ou numeros ou -
        (\.[A-Z|a-z]{2,})+   # . letras maiusculas ou minusculas no minino 2 caracteres
        ''',
        re.X
    )

    terminal.rule('CONFIG', characters='*')

    while True:
        email = Prompt.ask(
            "Digite seu email :email:",
            console=terminal
        )

        if compile_email.search(email):
            break

        terminal.print("[prompt.invalid]email invalida :loudly_crying_face:")
    
    while True:
        login = Prompt.ask(
            "Digite sua senha :sunglasses:",
            console=terminal,
            password=True
        )

        if len(login) > 5:
            break

        terminal.print("[prompt.invalid]senha invalida :loudly_crying_face:")
    
    return dict(email=email, login=login)
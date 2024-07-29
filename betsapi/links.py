from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import pandas as pd
from itertools import chain
from datetime import datetime
from time import sleep
from betsapi.utils import (
    compile_link,
    compile_link_clube,
    compile_period,
    get_period
)
from functools import partial
from rich.console import Console


URL_PAGE = (
    "https://pt.betsapi.com"
    "/le/25067"
    "/Ebasketball-H2H-GG-League--4x5mins/p.{page}"
)


def par_clubes(iterable):
    iterator = iter(iterable)
    a = next(iterator, None)

    for b in iterator:
        yield a, b
        a = next(iterable, None)


def get_points(title: str) -> tuple[int, int]:
    if title is None:
        return (0, 0)
    
    if '-' not in title:
        return (-0, -0)
    
    return tuple(
        map(
            int,
            title.strip()
            .replace('[', '')
            .replace(']', '')
            .split('-')
        )
    )


def get_link(link_home: str, link: str):
    parse_url = urlparse(link_home)
    template = '{}://{}{}'
    link = re.sub(r'/r/', r'/rs/bet365/', link)
    link_to = template.format(parse_url.scheme, parse_url.netloc, link)

    return link_to


# TODO: Acessar a url raiz -- SIMULAR NAVEGADOR
def request_pagina(
    terminal: Console, 
    headers: dict, 
    page: int
):
    
    link_home = URL_PAGE.format(page=page)

    endpoint = Request(
        link_home,
        headers = headers
    )

    try:
        content = urlopen(endpoint)
        soup = BeautifulSoup(content.read(), 'html.parser')

        clubes = [
            *par_clubes(
                map(
                    lambda tag: tag.get_text().strip(), 
                    soup.find_all('a', href=compile_link_clube)
                )
            )
        ]

        points = [
            *map(
                lambda tag: get_points(tag.string), 
                soup.find_all('a', href=compile_link)
            )
        ]

        periods = [
            *map(
                lambda tag: get_period(tag['data-dt']), 
                soup.find_all('td', {'data-dt': compile_period})
            )
        ]

        links = [
            *map(
                lambda tag: get_link(link_home, tag.attrs['href']), 
                soup.find_all('a', href=compile_link)
            )
        ]

        table_link = {
            'link': links,
            'period': periods,
            'clube_left': [clube[0] for clube in clubes],
            'clube_right': [clube[1] for clube in clubes],
            'point_left': [point[0] for point in points],
            'point_right': [point[1] for point in points],
            'page': [link_home] * len(periods)
        }
        
    except HTTPError as e:
        print(e)
    else:
        sleep(2.0)

        terminal.log(f"📑 Pagina: {page}, links: {len(table_link['link'])}")
        
        return table_link


def main_links(
    terminal: Console, 
    headers: dict, 
    args: tuple[int, int]
) -> str:

    page_start = args[0]
    page_end = args[1]

    data = (
        pd.concat(
            [
            *map(
                    pd.DataFrame, 
                    chain([*map(partial(request_pagina, terminal, headers), range(page_start, page_end + 1))])
                )
            ]
        )
    )
    
    to_file = f'hrefs_{datetime.now():%Y%m%d_%H_%M_%S}.xlsx'

    terminal.log(f'📂 Arquivo exportado - {to_file}')
    data.to_excel(to_file, index=False)

    return to_file
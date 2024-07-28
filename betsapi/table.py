from urllib.request import (
    urlopen, 
    Request
)
from bs4 import BeautifulSoup
from betsapi.utils import (
    get_period, 
    compile_c_path, 
    compile_link_clube
)
import pandas as pd
from collections import defaultdict
import re
import os
from time import sleep
from openpyxl import open as open_pyxl
from contextlib import closing
from itertools import islice
from rich.console import Console
from rich.tree import Tree
from rich.filesize import decimal


def create_table(
    terminal: Console, 
    headers: dict, 
    link: str
):
    req = Request(
        link,
        headers=headers
    )

    content = urlopen(req)
    soup = BeautifulSoup(content.read(), 'html.parser')

    # NOTE: Extrai base de titulos
    def add_row_title(soup):
        nomes = (
            soup
            .find(
                lambda tag: tag.has_attr('href') 
                and tag.parent.name == 'span'
            ).parent
        )

        clubes = tuple(
            map(
                lambda tag: tag.get_text().strip(), 
                nomes.find_all('a', href=compile_link_clube)
            )
        )
        pontos = (nomes.span.get_text().strip(), )
        periodo = (
            get_period(
                nomes.find('span', {'data-dt': True})
                .attrs['data-dt']
            ), 
        )

        return clubes + pontos + periodo


    titles = soup.find_all('h3', class_='card-title')
    tables = soup.find_all('table', class_='table table-sm')

    dfs = defaultdict(list)
    rows = add_row_title(soup)
    *__, day = rows

    for p, title in enumerate(titles):
        name = title.get_text().strip()

        data = [
            (link, name) + add_row_title(soup) +
            tuple(
                col.get_text().strip() 
                if 'data-dt' not in col.attrs 
                else get_period(col.attrs['data-dt']) 
                for col in row.find_all('td')
            )
            for row in tables[p].find_all('tr')
        ]

        dfs[name].append(data)
    
    terminal.rule(f'Arquivo {day}', style="magenta", characters='*')
    rows_total = file_totais = 0

    for j, [values] in dfs.items():
        file_totais += 1
        name = compile_c_path.sub('', j)
        file = f'{name}_{day:%Y%m%d_%H_%M_%S}.xlsx'

        if not os.path.isdir(name):
            os.mkdir(name)
        
        # NOTE: Arvore de diretorios
        tree = Tree(
            f":open_file_folder: {name}",
            guide_style="bold bright_blue",
        )
        
        to_file = os.path.join(name, file)
        df_to = pd.DataFrame(values)
        df_to.to_excel(to_file, index=False)
        
        file_size = os.stat(to_file).st_size
        tree.add(f'{file} [b red]({decimal(file_size)})[/]')

        rows_total += df_to.shape[0]
        terminal.print(tree)
    
    terminal.log(f'📝 Total de registros gerado {rows_total}, arquivos {file_totais}')

    return rows_total, file_totais


def main_tables(
    terminal: Console, 
    headers: dict,
    file_link: str
):

    with closing(
        open_pyxl(
            file_link, 
            data_only=True,
            read_only=True
        )
    ) as wb:
        
        ws = wb.active
        rows = ws.rows
        
        # Remove cabecalho
        __ = next(rows)

        links = (
            col.value 
            for row in rows 
            for col in islice(row, 6, 7)
            )
        
        totais = []
        for link in links:
            rows = create_table(terminal, headers, link)
            totais.append(rows)
            sleep(2.0)
        
        terminal.print()
        rows = sum([t[0] for t in totais])
        files = sum([t[1] for t in totais])

        terminal.log(f'⏰ Registros: {rows}, Arquivos: {files}')
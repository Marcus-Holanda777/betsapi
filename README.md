# Web scraping API BETSAPI

O aplicativo tem como objetivo coletar informações da página [https://pt.betsapi.com](https://pt.betsapi.com), 
como partidas, horários, odds e outros dados relevantes, utilizando técnicas de web scraping.

---

## Instalação

```bash
pip install "git+https://github.com/Marcus-Holanda777/betsapi.git"
```

## Como usar ?

```diff
- O site exige autenticação e gerenciamento de cookies. 
- A cada execução será gerado um novo arquivo `json` com o `Headers` atualizado.
```

Para usar, basta chamar o app `betsapi`, e depois digitar os comandos.

1. init
> Faz a configuração inicial do programa.
```bash
init options: --version -v, --obscure -o,--help -h

Digite seu email ✉: teste@init.com
Digite sua senha 😎:
```

2. page
> Exporta os dados a partir de uma liga e intervalo de paginas `paginas`.
```bash
page options: --start -s, --end -e, --version -v, --help -h
```

```bash
betsapi page "1234/Futebol" -s 1 -e 10
```

3. link
> Exporta os dados a partir de um link ou uma planilha.
```bash
link args: url [required], options: --version -v, --help -h
```

```bash
betsapi link "c:\links.xlsx"

betsapi link "https://url"
```
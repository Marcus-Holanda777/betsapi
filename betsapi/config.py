import json
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from time import sleep
from typing import Union, Callable
import typer
from betsapi import __app_name__
from pathlib import Path

WebDriverOrWebElement = Union[WebDriver, WebElement]


DEFAULT_RAIZ = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE = DEFAULT_RAIZ / 'start.json'
PAGE_AUTH = 'https://pt.betsapi.com/login/GitHub/'


def read_start_json() -> dict:
    with CONFIG_FILE.open('r') as fp:
        file = json.load(fp)
    
    return file


def is_start_json():
    is_file = CONFIG_FILE.is_file()
    
    if is_file:
        file = read_start_json()
    
    return all([k in ['email', 'login'] for k in file.keys()])


def init_start_json(email: str, login: str):
    data = {'email': email, 'login': login}

    try:
       DEFAULT_RAIZ.mkdir(exist_ok=True)

       with CONFIG_FILE.open('w') as fp:
            json.dump(data, fp, indent=4)

    except OSError:
        return
            
    return CONFIG_FILE


def wait_get_tag(
    driver: WebDriver,
    by: By,
    tag: str,
    *,
    timeout: float = 30.0,
    poll_frequency: float = 5.0,
    predicate: Callable = None
) -> WebDriverOrWebElement | None:
    """espera o elemento
    ficar disponivel no doom
    """

    conds = predicate((by, tag))

    elm = (
        WebDriverWait(
            driver=driver,
            timeout=timeout,
            poll_frequency=poll_frequency
        )
        .until(conds)
    )

    return elm


def create_headers(txt_email, txt_login):
    """Navegador no modo invisivel
    para logar no site e depois gerar os cookies
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=0, i",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    
    driver = webdriver.Chrome(options=options)
    driver.get(PAGE_AUTH)
    
    data = zip(['login', 'password'], [txt_email, txt_login])
    for tag, send in data:
        elm = wait_get_tag(
            driver, 
            By.XPATH, 
            f"//input[@name='{tag}']", 
            predicate=EC.presence_of_element_located
        )
        elm.send_keys(send)
    elm.submit()
    
    # NOTE: ESPERAR CARREGAR COOKIES
    sleep(5.0)

    cookies = '; '.join(
        [
            f"{cook['name']}={cook['value']}" 
            for cook in driver.get_cookies()
        ]
    )

    headers |= {'Cookie': cookies}

    with open('config.json', 'w') as fp:
        json.dump(headers, fp, indent=4)


def main_heades(email: str, login: str) -> dict:
    create_headers(
        email,
        login
    )

    with open('config.json', 'r') as fp:
        headers = json.load(fp)
    return headers
import re
import pytz
from datetime import datetime
from functools import reduce


compile_period = re.compile(
    r"""
    ^
    \d{4}-\d{2}-\d{2} # ano-mes-dia
    T                 # 
    \d{2}:\d{2}       # hora:minuto
    :\d{2}Z
    $
    """,
    re.VERBOSE
)

compile_link = re.compile(
    r"""
    ^
    /r/   # comeca com /r/
    \d+/  # pelo menos um numero e /
    .+    # pelo menos um caractere qualquer
    $
    """,
    re.VERBOSE
)

compile_link_clube = re.compile(
    r"""
    ^
    /t/   # comeca com /t/
    \d+/  # pelo menos um numero e /
    .+    # pelo menos um caractere qualquer
    $
    """,
    re.VERBOSE
)


def compose(*funcs):
    def inner(f, g):
        return lambda x: g(f(x))
    return reduce(inner, funcs, lambda x: x)


def get_period(dt: str) -> datetime:
    fuso = pytz.timezone('America/Fortaleza')
    dt_to = (
        datetime.strptime(dt, '%Y-%m-%dT%H:%M:%SZ')
        .replace(tzinfo=pytz.UTC)
        .astimezone(fuso)
        .replace(tzinfo=None)
    )

    return dt_to
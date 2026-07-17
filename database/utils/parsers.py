import re
from datetime import date, datetime
from typing import Optional


def parse_float(valor) -> float:
    """Converte uma string para float, tratando formatos brasileiros (vírgula/ponto) e internacionais."""
    if valor is None or valor == "":
        return 0.0
    try:
        return float(valor)
    except (ValueError, TypeError):
        pass

    valor = re.sub(r'[^\d,.-]', '', str(valor))

    if valor.count(',') and valor.count('.'):
        if valor.rfind(',') > valor.rfind('.'):
            valor = valor.replace('.', '').replace(',', '.')
        else:
            valor = valor.replace(',', '')
    elif valor.count(',') == 1 and not valor.count('.'):
        valor = valor.replace(',', '.')
    else:
        valor = valor.replace('.', '').replace(',', '.')

    try:
        return float(valor)
    except ValueError:
        return 0.0


def parse_date(value) -> Optional[str]:
    """Converte um valor para string de data no formato YYYY-MM-DD."""
    if isinstance(value, datetime):
        return value.strftime('%Y-%m-%d')
    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')
    if value is None:
        return None
    return str(value)

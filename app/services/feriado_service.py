import json
from datetime import datetime

FERIADOS_PATH = 'static/data/feriados.json'

def verificar_feriado(data_str):
    """
    Verifica se a data informada (dd/mm/yyyy) é feriado nacional.
    Retorna o nome do feriado se existir, senão None.
    """
    try:
        with open(FERIADOS_PATH, 'r', encoding='utf-8') as file:
            feriados = json.load(file)

        dia, mes, ano = data_str.split("/")
        mes_dia = f"{mes}-{dia}"

        for feriado in feriados["feriados_nacionais"].get(ano, []):
            if feriado["data"] == mes_dia:
                return feriado["nome"]
        
        return None
    except Exception as e:
        print(f"Erro ao verificar feriado: {e}")
        return None

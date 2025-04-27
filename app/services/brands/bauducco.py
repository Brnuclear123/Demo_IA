import openai
import json
import os
import re
from datetime import datetime
from app.services.slogan_service import criar_gif_slogan_combinado, js_read

conf_json_path = "static/data/env_variables.json"
env_data = js_read(conf_json_path)
openai.api_key = env_data["OPENAI_API_KEY"]

def gerar_slogans_bauducco(estado, cidade, bairro, data_campanha, momento, real_time_data):
    regex_patterns = [
        r'(.+?)\\s{2,}',
        r'\"([^\"]+)\",?',
        r'\\d+\\.\\s*(.+?)(?=\\n|$)',
        r'^(.+?)$',
        r'(.+?)(?:\\s{2,}|(?=\\n|$))'
    ]

    prompt = (
        f"Crie quatro slogans criativos para a marca Balduco.\\n"
        f"Localização: Estado {estado}, Cidade {cidade}, Bairro {bairro}.\\n"
        f"Clima atual: {real_time_data['weather']}.\\n"
        f"Turno do dia: {momento}.\\n"
        "Slogans devem transmitir sensação de aconchego, tradição e família.\\n"
        "Curto, até 70 caracteres.\\n"
        "Não use aspas, nem enumeração.\\n"
        "Se possível, faça pequenos trocadilhos com café da manhã ou lanche da tarde.\\n"
        "Sempre mencionar Balduco."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um especialista em slogans publicitários para marcas de tradição e família."},
                {"role": "user", "content": prompt}
            ]
        )
        resposta_texto = response.choices[0].message.content
        slogans = extrair_slogans(resposta_texto, regex_patterns)

        imagens = []
        for slogan in slogans:
            img = criar_gif_slogan_combinado(slogan, "bauducco")
            imagens.append(img)

        return slogans[:4], imagens

    except Exception as e:
        print("Erro ao gerar slogans Balduco:", e)
        return ["Slogan não disponível"] * 4, []

def extrair_slogans(texto, padroes):
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.MULTILINE)
        if len(matches) >= 4:
            return matches
    return ["Slogan não disponível"] * 4

def dia_da_semana(date_str: str) -> str:
    """Converte data para dia da semana (ex: '25/12/2023' -> 'Segunda-feira')."""
    dias = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 
            'Sexta-feira', 'Sábado', 'Domingo']
    try:
        data = datetime.strptime(date_str.split("to")[0].strip(), '%d/%m/%Y').date()
        return dias[data.weekday()]
    except Exception as e:
        print(f"Erro ao converter data: {e}")
        return ""

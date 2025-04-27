import openai
import json
import os
import re
from datetime import datetime
from app.services.slogan_service import criar_gif_slogan_combinado, js_read

conf_json_path = "static/data/env_variables.json"
env_data = js_read(conf_json_path)
openai.api_key = env_data["OPENAI_API_KEY"]

def gerar_slogans_corona(estado, cidade, bairro, data_campanha, momento, real_time_data):
    regex_patterns = [
        r'(.+?)\\s{2,}',
        r'\"([^\"]+)\",?',
        r'\\d+\\.\\s*(.+?)(?=\\n|$)',
        r'^(.+?)$',
        r'(.+?)(?:\\s{2,}|(?=\\n|$))'
    ]

    prompt = (f"""
        Você é uma inteligência criativa especializada em redigir mensagens curtas, impactantes e sensoriais para a marca de cerveja Corona no Brasil.

        Sua tarefa:
        → Crie 4 variações de slogans publicitários para exibição em telas digitais no ponto de venda.
        → Cada slogan deve ter entre 30 e 75 caracteres.
        → Não enumere, não use aspas e evite pontuação desnecessária.

        Diretrizes de estilo:
        → Mensagens leves, inspiradoras, sensoriais.
        → Evocar elementos da natureza: sol, mar, brisa, céu, areia, limão.
        → Estilo de vida livre, descontraído e ao ar livre.
        → Público-alvo: jovens de 18 a 35 anos, ligados à música, sunset, esportes e natureza.
        → Sem emojis. 
        → Evitar soar como propaganda direta: as mensagens devem parecer falas espontâneas de alguém relaxando com uma Corona gelada.

        Contexto para inspiração:
        - Temperatura: {real_time_data['weather']}°C
        - Horário: {momento}
        - Dia da semana: {dia_da_semana(data_campanha)}
        - Localização: {estado}, {cidade}, {bairro}

        Instruções específicas:
        - Adapte o tom dos slogans conforme o dia da semana ({dia_da_semana(data_campanha)}).
        - Se houver algum evento cultural ou mundial relevante no período, use-o de forma natural (sem forçar datas comemorativas aleatórias).
        - Não repita o nome da cidade, estado ou bairro nos slogans. Use outros recursos para criar conexão com o local.
        - Como Corona é uma marca bem pra frente, carregue os slogans de animação, frescor e otimismo.

        Referência conceitual: "Corona é inspirada na natureza, não feita da natureza."

        Exemplos de boas saídas:
        - Sol na pele, limão na garrafa, e o tempo jogando a favor
        - O pôr-do-sol é só o começo Brinde com o que vem depois
        """)




    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um redator publicitário especialista em slogans sensoriais e inspiradores."},
                {"role": "user", "content": prompt}
            ]
        )
        resposta_texto = response.choices[0].message.content
        slogans = extrair_slogans(resposta_texto, regex_patterns)

        imagens = []
        for slogan in slogans:
            img = criar_gif_slogan_combinado(slogan, "Corona")
            imagens.append(img)

        return slogans[:4], imagens

    except Exception as e:
        print("Erro ao gerar slogans Corona:", e)
        return ["Slogan não disponível"] * 4, []

def extrair_slogans(texto, padroes):
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.MULTILINE)
        if len(matches) >= 4:
            return matches
    return ["Slogan não disponível"] * 4

def dia_da_semana(date_str):
    dias = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
    date = datetime.strptime(date_str.split("to")[0].strip(), '%d/%m/%Y').date()
    return dias[date.weekday()]

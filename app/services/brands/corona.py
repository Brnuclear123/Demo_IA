import openai
import json
import os
import re
from datetime import datetime
from app.services.slogan_service import js_read
from app.services.utils.slogan_static_generator import SloganStaticGenerator

conf_json_path = "static/data/env_variables.json"
env_data = js_read(conf_json_path)
openai.api_key = env_data["OPENAI_API_KEY"]

def gerar_slogans_corona(estado, cidade, bairro, data_campanha, momento, real_time_data, usar_feriado=None):
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
        →  Evite iniciar as mensagens com numeração, como "1." ou "2.". Mesmo que a ideia seja boa, como em "1. UMA NOITE COM CORONA E PÉS NA AREIA", o número transmite uma sensação de instrução ou passo a passo — o que contradiz o espírito leve, livre e fluido da marca Corona. Também evite iniciar frases com traços ("-"), pois isso reforça a sensação de que a mensagem faz parte de uma lista. Com Corona, cada frase deve parecer um convite espontâneo a viver o momento, não um item a ser lido em sequência.

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

        # Usar o novo gerador de imagens estáticas
        generator = SloganStaticGenerator("Corona")
        imagens = generator.generate_static_images(slogans)

        return slogans[:4], imagens

    except Exception as e:
        # print("Erro ao gerar slogans Corona:", e)
        # TODO: remover for dedebuging
        print("Retornando slogans fictícios para teste")
        
        # Dados fictícios para teste quando a API falha
        slogans_ficticios = [
            "Sol na pele, limão na garrafa, e o tempo jogando a favor",
            "O pôr-do-sol é só o começo Brinde com o que vem depois",
            "Brisa do mar, amigos de sempre, momentos que duram para sempre",
            "Cada gole é uma nova aventura em um dia perfeito"
        ]
        
        # Usar o novo gerador de imagens estáticas
        generator = SloganStaticGenerator("Corona")
        imagens = generator.generate_static_images(slogans_ficticios)
            
        return slogans_ficticios, imagens

def extrair_slogans(resposta_texto, regex_patterns):
    slogans = []
    for pattern in regex_patterns:
        matches = re.findall(pattern, resposta_texto, re.MULTILINE)
        if matches:
            slogans.extend(matches)

    # Agora tratamos: remover enumeração e passar tudo para MAIÚSCULO
    slogans_tratados = []
    for slogan in slogans:
        slogan = re.sub(r'^\s\d+.\s', '', slogan)  # remove o "1. ", "2. ", etc no começo
        slogans_tratados.append(slogan.upper())       # coloca o slogan todo em maiúsculo

    return slogans_tratados

def dia_da_semana(date_str):
    dias = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
    date = datetime.strptime(date_str.split("to")[0].strip(), '%d/%m/%Y').date()
    return dias[date.weekday()]

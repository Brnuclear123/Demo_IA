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

def gerar_slogans_bauducco(estado, cidade, bairro, data_campanha, momento, real_time_data):
    regex_patterns = [
        r'(.+?)\\s{2,}',
        r'\"([^\"]+)\",?',
        r'\\d+\\.\\s*(.+?)(?=\\n|$)',
        r'^(.+?)$',
        r'(.+?)(?:\\s{2,}|(?=\\n|$))'
    ]

    prompt = (f"""
        Você é uma inteligência criativa especializada em redigir mensagens curtas, impactantes e sensoriais para a marca de biscoitos Bauducco no Brasil.

        Sua tarefa:
        → Crie 4 variações de slogans publicitários para exibição em telas digitais no ponto de venda.
        → Cada slogan deve ter entre 30 e 75 caracteres.
        → Não enumere, não use aspas e evite pontuação desnecessária.

        Diretrizes de estilo:
        → Mensagens leves, inspiradoras, sensoriais.
        → Evocar elementos de prazer, momentos de alegria e compartilhamento.
        → Estilo de vida descontraído e momentos de pausa.
        → Público-alvo: jovens e adultos de 18 a 45 anos, que apreciam momentos de prazer com biscoitos.
        → Sem emojis. 
        → Evitar soar como propaganda direta: as mensagens devem parecer falas espontâneas de alguém desfrutando de um momento de prazer com Bauducco.

        Contexto para inspiração:
        - Temperatura: {real_time_data['weather']}°C
        - Horário: {momento}
        - Dia da semana: {dia_da_semana(data_campanha)}
        - Localização: {estado}, {cidade}, {bairro}

        Instruções específicas:
        - Adapte o tom dos slogans conforme o dia da semana ({dia_da_semana(data_campanha)}).
        - Se houver algum evento cultural ou mundial relevante no período, use-o de forma natural (sem forçar datas comemorativas aleatórias).
        - Não repita o nome da cidade, estado ou bairro nos slogans. Use outros recursos para criar conexão com o local.
        - Como Bauducco é uma marca bem pra frente, carregue os slogans de animação, prazer e otimismo.

        Referência conceitual: "Bauducco é inspirada no prazer, não feita do prazer."

        Exemplos de boas saídas:
        - Um momento de prazer, uma pausa para respirar, e o tempo jogando a favor
        - O prazer é só o começo Brinde com o que vem depois
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
        generator = SloganStaticGenerator("Bauducco")
        imagens = generator.generate_static_images(slogans)

        return slogans[:4], imagens

    except Exception as e:
        print("Erro ao gerar slogans Bauducco:", e)
        # TODO: remover for dedebuging
        print("Retornando slogans fictícios para teste")
        
        # Dados fictícios para teste quando a API falha
        slogans_ficticios = [
            "Um momento de prazer, uma pausa para respirar, e o tempo jogando a favor",
            "O prazer é só o começo Brinde com o que vem depois",
            "Brisa do mar, amigos de sempre, momentos que duram para sempre",
            "Cada gole é uma nova aventura em um dia perfeito"
        ]
        
        # Usar o novo gerador de imagens estáticas
        generator = SloganStaticGenerator("Bauducco")
        imagens = generator.generate_static_images(slogans_ficticios)
            
        return slogans_ficticios, imagens

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
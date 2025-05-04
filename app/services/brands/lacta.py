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

def gerar_slogans_lacta(estado, cidade, bairro, data_campanha, momento=[], real_time_data=[], dia_semana=[], usar_feriado=None):
    regex_patterns = [
        r'(.+?)\\s{2,}',
        r'\"([^\"]+)\",?',
        r'\\d+\\.\\s*(.+?)(?=\\n|$)',
        r'^(.+?)$',
        r'(.+?)(?:\\s{2,}|(?=\\n|$))'
    ]

    prompt = (f"""
        Você é uma inteligência criativa especializada em redigir mensagens curtas, impactantes e sensoriais para a marca de chocolate Lacta no Brasil. Quando referir-se à marca Lacta, faça sempre no feminino. 

        Sua tarefa:
        → Crie 4 variações de títulos publicitários para exibição em telas digitais no ponto de venda.
        → Cada título deve ter entre 30 e 75 caracteres.
        → Não enumere, não use aspas e evite pontuação desnecessária.

        Diretrizes de estilo:
        → Mensagens leves, inspiradoras, emocionais.
        → Evocar sempre sentimentos.
        → Lacta é sobre conexão, sentimento, emoção e o quanto um chocolate pode representar tudo isso.
        → Público-alvo: pessoas de 18 a 55 anos, emocionalmente conectadas com a família, os amigos, e parceiros de vida.
        → Sem emojis. 
        → Crie mensagens espontâneas, com induzam de forma sutil ao impulso de compra e sugestionem o consumidor a relaxar com uma Corona gelada 
        → Evite iniciar as mensagens com numeração, como "1." ou "2.". Mesmo que a ideia seja boa, como em "1. UMA NOITE COM CORONA E PÉS NA AREIA", o número transmite uma sensação de instrução ou passo a passo — o que contradiz o espírito leve, livre e fluido da marca Corona. Também evite iniciar frases com traços ("-"), pois isso reforça a sensação de que a mensagem faz parte de uma lista. Com Corona, cada frase deve parecer um convite espontâneo a viver o momento, não um item a ser lido em sequência.

        Instruções específicas:
        - Adapte a intenção do título conforme o dia da semana, cite o dia só quando for conveniente:
        - Quando o momento do dia for escolhido, adapte a intenção da mensagem também:
            De manhã, fale sobre como um "bom dia" fica mais gostoso com chocolate;
            De tarde, explore o fato de que um chocolate deixa qualquer tarde e relação mais doce;
            De noite, diga que boas companhias e chocolate sempre fazem um jantar maravilhoso.
        - Quando selecionado o Dia do Chocolate, em 07/07, aproveite para valorizar na mensagem o contexto de que o dia do chocolate também é dia de demonstrar carinho e emoções por quem se gosta. 
        - Não repita o nome da cidade, estado ou bairro nos slogans. Use outros recursos para criar conexão com o local.
        - Lacta é uma marca leve, calorosa, próxima, acolhedora e inspiradora. Fala de forma simples, direta e sempre buscando criar conexão emocional com o consumidor

        Referência conceitual: "Cada pedacinho aproxima"

        Exemplos de boas saídas:
        - Sextou com gostinho da melhor companhia. Não disse qual
        - O melhor pedacinho da segunda é com quem a gente divide ela
        
        Contexto para inspiração:
                - Localização: {estado}, {cidade}, {bairro}
        """)
    if real_time_data != []:
        prompt = prompt + f"\n                - Informações adicionais: {real_time_data}"
    if momento != []:
        prompt = prompt + f"\n                - Horário: {momento}"
    if dia_semana != []:
        prompt = prompt + f"\n                - Dia da semana: {dia_semana}"


    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você é um redator publicitário especialista em slogans sensoriais e inspiradores."},
                {"role": "user", "content": prompt}
            ]
        )
        resposta_texto = response.choices[0].message.content
        slogans = extrair_slogans(resposta_texto, regex_patterns)

        # Usar o novo gerador de imagens estáticas
        generator = SloganStaticGenerator("Lacta")
        imagens = generator.generate_static_images(slogans)

        return slogans[:4], imagens

    except Exception as e:
        print("Erro ao gerar slogans Lacta:", e)
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
        generator = SloganStaticGenerator("Lacta")
        imagens = generator.generate_static_images(slogans_ficticios)
            
        return slogans_ficticios, imagens

def extrair_slogans(resposta_texto, regex_patterns):

    slogans = []
    for pattern in regex_patterns:
        matches = re.findall(pattern, resposta_texto, re.MULTILINE)
        if matches:
            slogans.extend(matches)

    # Remover duplicatas
    seen = set()
    deduped = []
    for s in slogans:
        if s not in seen:
            seen.add(s)
            deduped.append(s)

    # Remover enumeração e passar tudo para MAIÚSCULO
    slogans_tratados = []
    for slogan in deduped:
        slogan = re.sub(r'^\s\d+.\s', '', slogan)  # remove o "1. ", "2. ", etc no começo
        slogans_tratados.append(slogan.upper())       # coloca o slogan todo em maiúsculo

    return slogans_tratados

def dia_da_semana(date_str):
    dias = ['segunda-feira', 'terça-feira', 'quarta-feira', 'quinta-feira', 'sexta-feira', 'sábado', 'domingo']
    date = datetime.strptime(date_str.split("to")[0].strip(), '%d/%m/%Y').date()
    return dias[date.weekday()]


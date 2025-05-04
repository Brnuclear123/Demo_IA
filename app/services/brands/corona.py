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

def gerar_slogans_corona(estado, cidade, bairro, data_campanha, momento=[], real_time_data=[], dia_semana=[], usar_feriado=None):
    regex_patterns = [
        r'(.+?)\\s{2,}',
        r'\"([^\"]+)\",?',
        r'\\d+\\.\\s*(.+?)(?=\\n|$)',
        r'^(.+?)$',
        r'(.+?)(?:\\s{2,}|(?=\\n|$))'
    ]

    prompt = (f"""
        Você é uma inteligência criativa especializada em redigir mensagens curtas, impactantes e sensoriais para a marca de cerveja Corona no Brasil. Refira-se sempre à Corona no feminino.

        Sua tarefa:
        → Crie 4 variações de títulos publicitários para exibição em telas digitais no ponto de venda.
        → Cada título deve ter entre 30 e 75 caracteres.
        → Não enumere, não use aspas e evite pontuação desnecessária.

        Diretrizes de estilo:
        → Mensagens leves, inspiradoras, sensoriais.
        → Evocar elementos da natureza: sol, por-do-sol, calor, frescor, refrescância.
        → Estilo de vida livre, descontraído e ao ar livre.
        → Público-alvo: jovens de 18 a 35 anos, ligados à música, sunset, esportes e natureza.
        → Sem emojis. 
        → Crie mensagens espontâneas, com induzam de forma sutil ao impulso de compra e sugestionem o consumidor a relaxar com uma Corona gelada 
        → Evite iniciar as mensagens com numeração, como "1." ou "2.". Mesmo que a ideia seja boa, como em "1. UMA NOITE COM CORONA E PÉS NA AREIA", o número transmite uma sensação de instrução ou passo a passo — o que contradiz o espírito leve, livre e fluido da marca Corona. Também evite iniciar frases com traços ("-"), pois isso reforça a sensação de que a mensagem faz parte de uma lista. Com Corona, cada frase deve parecer um convite espontâneo a viver o momento, não um item a ser lido em sequência.


        Instruções específicas:
        -  Adapte a intenção do título conforme o dia da semana, cite o dia só quando for conveniente:
            Na segunda, explore o contexto do início ou recomeço da semana;
            Na terça, fale sobre continuidade da semana, sobre já ser terça;
            Na quarta, o contexto de meio de semana é ótimo pra ser usado;
            Na quinta, usa a ideia de que falta pouco pro fim de semana;
            Na sexta, explore a expressão sextou e o fato de que o fim de semana já começou;
            No sábado e no domingo, use momentos no parque, de folga, de relaxamento para entregar as mensagens.
        - Quando o momento do dia for escolhido, adapte a intenção da mensagem também:
            De manhã, não faça referência nenhuma;
            De tarde, explore a ideia do entardecer e de que logo tem por-do-sol;
            De noite, diga que uma Corona sempre vai bem antes ou depois do jantar.
        - Quando selecionado o feriado de Corpus Christi, em 19/06, aproveite para valorizar na mensagem o contexto de feriadão, de viagem para a praia, de curtir a folga e explorar a natureza. 
        - Não repita o nome da cidade, estado ou bairro nos slogans. Use outros recursos para criar conexão com o local.
        - Corona é uma marca solar, animada, otimista, refrescante, que sempre vê a vida com um olhar otimista e positivo.

        Referência conceitual: "Corona. A vida é aqui fora" / "Corona. Há 100 anos fazendo da praia um palco"

        Exemplos de boas saídas:
        - Sol na pele, limão na garrafa, e um brinde à vida.
        - O pôr-do-sol é só o começo. Um brinde ao que vem depois.
        
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

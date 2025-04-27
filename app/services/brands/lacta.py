import openai
import json
import os
import re
from datetime import datetime
from app.services.slogan_service import criar_gif_slogan_combinado, js_read

conf_json_path = "static/data/env_variables.json"
env_data = js_read(conf_json_path)
openai.api_key = env_data["OPENAI_API_KEY"]

def gerar_slogans_lacta(estado, cidade, bairro, data_campanha, momento, real_time_data):
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
        → Crie mensagens espontâneas, com induzam de forma sutil ao impulso de compra e sugestionem o consumidor a presentear pessoas queridas com chocolate. 

        Contexto para inspiração:
        - Temperatura: {real_time_data['weather']}°C
        - Horário: {momento}
        - Dia da semana: {dia_da_semana(data_campanha)}

        Instruções específicas:
        - Adapte a intenção do título conforme o dia da semana ({dia_da_semana(data_campanha)}), cite o dia só quando for conveniente:
        Na segunda, explore falar de sentimentos que inspirem incentivo para o início da semana;
        Na terça, fale sobre a importância das parcerias e companhias para encarar o restante da semana;
        Na quarta, o contexto de meio de semana é ótimo pra gerar elogios;
        Na quinta, lembre as pessoas sobre convites para jantares, happy hours e afins;;
        Na sexta, explore a expressão sextou e o fato de que o fim de semana já começou para reforçar as conexões humanas;
        No sábado e no domingo, use momentos no parque, de folga, de encontro com os amigos e a família para entregar as mensagens.
        - Quando o momento do dia for escolhido, adapte a intenção da mensagem também:
            De manhã, fale sobre como um "bom dia" fica mais gostoso com chocolate;
            De tarde, explore o fato de quem um chocolate deixa qualquer tarde e relação mais doce;
            De noite, diga que boas companhias e chocolate sempre fazem um jantar maravilhoso.
        - Não repita o nome da cidade, estado ou bairro nos slogans. Use outros recursos para criar conexão com o local.
        - Lacta é uma marca leve, calorosa, próxima, acolhedora e inspiradora. Fala de forma simples, direta e sempre buscando criar conexão emocional com o consumidor

        Referência conceitual: "Cada pedacinho aproxima"

        Exemplos de boas saídas:
        - Sextou com gostinho da melhor companhia. Não disse qual
        - O melhor pedacinho da segunda é com quem a gente divide ela
        """)







    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um redator publicitário especialista em slogans afetivos e curtos."},
                {"role": "user", "content": prompt}
            ]
        )
        resposta_texto = response.choices[0].message.content
        slogans = extrair_slogans(resposta_texto, regex_patterns)

        imagens = []
        for slogan in slogans:
            img = criar_gif_slogan_combinado(slogan, "Lacta")
            imagens.append(img)

        return slogans[:4], imagens

    except Exception as e:
        print("Erro ao gerar slogans Lacta:", e)
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


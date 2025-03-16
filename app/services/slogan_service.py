from config import config
# Usaremos a configuração de desenvolvimento (ou a que preferir)
conf = config['development']

import os
import json
import re
import time
import requests
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageSequenceClip
import openai
import google.generativeai as genai

# CONSTANTES retiradas do config.py
WEATHER_JSON = conf.WEATHER_JSON            # ex.: 'static/data/weather-cd.json'
AVALIACOES_PATH = conf.AVALIACOES_PATH      # ex.: 'avaliacoes.json'
FONT_PATH = conf.FONT_PATH                  # ex.: 'static/fonte/Bison-Bold(PersonalUse).ttf'
FUNDO_IMAGEM_PATH = conf.FUNDO_IMAGEM_PATH  # ex.: 'static/frames/meu_fundo.png'
ENVIROMENT_DATA = conf.ENVIROMENT_DATA      

# Função para ler arquivos JSON
def js_read(filename: str):
    with open(filename) as j_file:
        return json.load(j_file)

# Carrega variáveis de ambiente (arquivo 'env_variables.json')
data = js_read(ENVIROMENT_DATA)
openai.api_key = data['OPENAI_API_KEY']

# Funções de avaliação
def carregar_avaliacoes():
    if os.path.exists(AVALIACOES_PATH):
        with open(AVALIACOES_PATH, 'r') as file:
            return json.load(file)
    return {}

def salvar_avaliacoes(avaliacoes):
    with open(AVALIACOES_PATH, 'w') as file:
        json.dump(avaliacoes, file, indent=4)

def ultimos_slogan():
    diretorio = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
    arquivos_png = [arquivo for arquivo in os.listdir(diretorio) if arquivo.endswith('.png')]
    return arquivos_png[-4:]

# Funções para processamento de texto e extração de slogans
def encontrar_slogans(string_response, regex_patterns):
    for regex_pattern in regex_patterns:
        slogans = re.findall(regex_pattern, string_response)
        print(f"Testando padrão: {regex_pattern}")
        print(f"Resultados encontrados: {slogans}\n\n")
        if len(slogans) == 4:
            return slogans
    return ["Slogan adicional não disponível."] * 4

def regex_info(string_response, regex_patterns):
    for regex_pattern in regex_patterns:
        info = re.findall(regex_pattern, string_response, re.DOTALL)
        print(f"Testando padrão: {regex_pattern}")
        print(f"Resultados encontrados: {info}\n\n")
        if len(info) == 4:
            return info
    return []

# Funções relacionadas ao Weather
def get_coordinates(city, state, country="Brasil"):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'city': city,
        'state': state,
        'country': country,
        'format': 'json'
    }
    headers = {
        'User-Agent': 'YourAppName/1.0 (your@email.com)'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
    return None, None

def get_weather_description(code):
    with open(WEATHER_JSON, 'r', encoding='utf-8') as file:
        weather_codes_dict = json.load(file)
    if str(code) in weather_codes_dict:
        return weather_codes_dict[str(code)]['description']
    else:
        return "Código não encontrado."

def get_weather_call(date_forecast: list, lag_lon=[-10, -55]):
    try:
        today_str = time.strftime("%Y-%m-%d", time.localtime())
        today = datetime.strptime(today_str, "%Y-%m-%d")
        input_date = datetime.strptime(date_forecast[0], "%Y-%m-%d")
        date_diff = (input_date - today).days
        if not (0 <= date_diff <= 7):
            print("Data do input está fora da faixa de previsão de 7 dias")
            return "null"
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lag_lon[0],
            "longitude": lag_lon[1],
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
            "timezone": "America/Sao_Paulo",
            "start_date": date_forecast[0],
            "end_date": date_forecast[1]
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        daily_data = data.get("daily", {})
        wc_hold = daily_data.get("weather_code", [])
        if not wc_hold:
            raise ValueError("Nenhum código de tempo encontrado")
        temperature_max = daily_data.get("temperature_2m_max", [])[0]
        temperature_min = daily_data.get("temperature_2m_min", [])[0]
        weather_description = get_weather_description(wc_hold[0])
        weather_output = f"Max: {temperature_max}°C / Min: {temperature_min}°C\n{weather_description}"
        return weather_output
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ou requisição falhou: {e}")
        return None
    except KeyError as e:
        print(f"Erro ao acessar o JSON retornado pela API. Chave não encontrada: {e}")
        return None
    except ValueError as e:
        print(f"Erro ao processar a resposta: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

# Função para criar GIF animado dos slogans
def criar_gif_slogan_combinado(slogan_texto, brand_name):
    dtnow = datetime.now()
    base_filename = f"slogan_animado{dtnow.strftime('%Y%m%d%H%M%S')}{str(dtnow.microsecond)[:2].zfill(2)}"
    largura, altura = 1920, 158
    
    if os.path.exists(FUNDO_IMAGEM_PATH):
        imagem_base = Image.open(FUNDO_IMAGEM_PATH).resize((largura, altura)).convert("RGBA")
    else:
        imagem_base = Image.new("RGBA", (largura, altura), "#333")
        
    text_color = "white" if brand_name in ["Corona", "Lacta"] else "black"
    
    try:
        font = ImageFont.truetype(FONT_PATH, 64)
    except IOError:
        font = ImageFont.load_default()
    
    frames = []
    temp_draw = ImageDraw.Draw(imagem_base)
    total_text_width = 0
    
    for letter in slogan_texto:
        bbox = font.getbbox(letter)
        letter_width = bbox[2] - bbox[0]
        total_text_width += letter_width
    
    final_x = (largura - total_text_width) / 2
    full_bbox = temp_draw.textbbox((0, 0), slogan_texto, font=font)
    text_height = full_bbox[3] - full_bbox[1]
    final_y = (altura - text_height) / 2
    
    letter_delay_gap = 1           # atraso (em frames) entre cada letra
    letter_animation_duration = 5  # duração da animação de cada letra (em frames)
    final_hold_frames = 30         # mantém o frame final por 30 frames (~3 segundos a 100ms/frame)
    total_frames = (len(slogan_texto) - 1) * letter_delay_gap + letter_animation_duration + final_hold_frames
    
    for frame in range(total_frames):
        frame_img = imagem_base.copy()
        overlay = Image.new("RGBA", (largura, altura), (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        current_x = final_x
        
        for idx, letter in enumerate(slogan_texto):
            bbox_letter = font.getbbox(letter)
            letter_width = bbox_letter[2] - bbox_letter[0]
            letter_delay = idx * letter_delay_gap
            
            if frame < letter_delay:
                pass  # A letra ainda não iniciou animação
            elif frame < letter_delay + letter_animation_duration:
                progress = (frame - letter_delay) / letter_animation_duration
                offset_y = int((1 - progress) * 30)
                alpha = int(progress * 255)
                fill = (255, 255, 255, alpha) if text_color == "white" else (0, 0, 0, alpha)
                draw_overlay.text((current_x, final_y + offset_y), letter, font=font, fill=fill)
            else:
                fill = (255, 255, 255, 255) if text_color == "white" else (0, 0, 0, 255)
                draw_overlay.text((current_x, final_y), letter, font=font, fill=fill)
                
            current_x += letter_width
        
        combined = Image.alpha_composite(frame_img, overlay)
        frames.append(combined.convert("RGB"))
    
    # Cria um clipe de vídeo a partir das imagens
    clip = ImageSequenceClip([np.array(frame) for frame in frames], fps=10)
    video_filename = os.path.join("static", f"{base_filename}.mp4")
    
    # Salva o vídeo
    clip.write_videofile(video_filename, codec="libx264", fps=24)
    
    return video_filename

# Função para gerar slogans e GIFs a partir do prompt
def gerar_slogans_e_gifs(estado, cidade, bairro, data_campanha, momento, brand_name):
    regex_patterns_gpt = [
        r'(.+?)\s{2,}',
        r'"([^"]+)"',
        r'\d+\.\s*(.+?)(?=\n|$)',
        r'^(.+?)$',
        r'(.+?)(?:\s{2,}|(?=\n|$))'
    ]
    
    if brand_name == "Corona":
        prompt = (
        f"Assuma que você é um redador publicitário especialista em mensagens curtas, rápidas e inteligentes para a marca Corona."
        f"Escreva 4 versões de uma mensagem publicitária para serem exibidas em uma tela de mídia localizada no ponto de venda de um supermercado. As opções de mensagem devem seguir as seguintes diretrizes."
        f"A mensagem deve ter um tom de voz que enfatiza a conexão da marca com a natureza e a experiência sensorial, especialmente relacionada ao sol e à praia."
        f"A mensagem deve explorar essa conexão que a marca tem com a natureza. Pois a cerveja Corona se apresenta como uma cerveja 'nascida na praia e feita da natureza', estabelecendo uma forte ligação com elementos naturais."
        f"O tom da mensagem deve provocar reflexões em seu público sobre o 'poder transformador do sol', criando uma associação entre o produto e experiências positivas ao ar livre."
        f"A mensagem pode sugerir um tom de voz que valoriza a responsabilidade ambiental, alinhando-se com tendências de consumo consciente."
        f"A mensagem é direcionada ao público de 18 a 35 anos, O público-alvo é composto majoritariamente por jovens, conectados com experiências sensoriais e culturais, como eventos de música e esportes."
        f"A mensagem é para o gênero predominante: masculino."
        f"Sempre tente colocar o nome da marca Corona nos slogans, para não ser confundido com outra marca de cerveja."
        f"Ajustar a linguagem e o seu apelo para se conectar efetivamente com esse público e coisas relacionadas a ele."
        f"Construa a mensagem relacionando ela ao momento do dia."
        f"Use o estado '{estado}, '{cidade}', '{bairro}' para criar frases que tenha contexto com a localidade."
        f"Mantenha a mensagem concisa, criativa e impactante usando até 70 caracteres."
        f"A mensagem não precisa necessariamente ter o nome da marca Corona na sua construção."
        f"Apesar de considerar a temperatura local, não precisa incluir o numero da temperatura na mensagem."
        f"Apesar de considerar o dia da semana, não precisa obrigatoriamente incluir ele na escrita da mensagem."
        f"Apesar de considerar a cidade e estado para a criação da mensagem, não precisa incluir isso necessariamente na escrita."
        f"não é para escrever as datas nos slogans, apenas use ela a seu favor."
        f"Utilize o tom de voz da marca de forma consistente."
        f"não coloque as informações de manha/tarde/noite nos slogans."
        f"quero apenas o slogan e nada mais, para podermos extrair o melhor de cada frase." 
        f"não use as informaçoes de 'localização e :'"
        f"Use '{data_campanha}' para poder te ajudar a gerar algumas frases de acordo com o periodo que os slogans vao ficar ao ar."
        f"Considere na criação do slogan o horario que vai ser consumido o produto: {momento}'"
        )
        
    elif brand_name == "Lacta":
        prompt = (
        f"Crie quatro slogans publicitários exclusivos e de alto impacto para a marca Lacta, "
        f"Use o estado '{estado}','{cidade}' e '{bairro} para criar slogans que tenha contexto com a localidade. Esta campanha é direcionada ao público de 18 a 35 anos com o tema, "
        f"utilizando um tom de voz de emocional e afetivo para transmitir uma sensação de prestígio, acolhimento e valor agregado positivo. "
        "precisamos que limite o uso de caracter para que não exceda, não pode passar de 70 caracteres"
        "Cada slogan deve ser envolvente, destacar a exclusividade da marca e incluir uma chamada para ação (CTA) que inspire desejo e urgência. "
        "Separe cada slogan com uma quebra de linha e garanta que sejam quatro slogans únicos."
        "slogans que pode ser rimados seria muito bom, para grudar na cabeça do cliente, mas mantendo a criatividade e os 45 caracteres "
        "vamos colocar mais criatividade nesses slogans, quero algo mais intuitivo de acordo com suas marcas."
        "não coloque datas nos slogans, use as datas para indentificar o dia da semana e aproveite para usar a seu favor."
        "quero apenas o slogans, não é para colocar corona:, isso não deixa os slogans profisionais, gere apenas slogans."
        "Regra basica, quando colocar a localização no slogam sempre açocie a marca, se não tiver a localização apenas o slogam com a marca."
        "nunca deixe de mencionar a marca Lacta."
        "criativo da marca frequentemente utiliza jogos de palavras, trocadilhos e referencias culturais, criatividade na forma de se comunicar"
        "eu quero concordancia nas frases dos slogans, sempre tenta manter uma concordancia verbal para um maior entendimento do publico."
        f"No caso de o '{data_campanha}'selecionado for Quarta feira subistitua para Quartou, Quinta feira subistitua para Quintou e se for Sexta feira subistitua para Sextou."
        f"Considere na criação do slogan o horario que vai ser consumido o produto: {momento}'"
        )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Assuma que você é um redator publicitário especialista em mensagens curtas, rápidas e inteligentes."},
                {"role": "user", "content": prompt}
            ]
        )
        string_response = str(response.choices[0].message.content)
        print(string_response)
        slogans = encontrar_slogans(string_response, regex_patterns_gpt)
        imgs = []
        for slogan in slogans:
            file_img = criar_gif_slogan_combinado(slogan, brand_name)
            imgs.append(file_img)
        print("Mensagem GPT\n\n", slogans)
        return slogans[:4], imgs
    except Exception as e:
        print("Erro ao gerar slogans:", e)
        try:
            genai.configure(api_key=data['GEMINI_API_KEY'])
            genai.GenerationConfig(
                temperature=1,
                candidate_count=1,
                top_k=10
            )
            model_gemini = genai.GenerativeModel(
                model_name="gemini-1.5-flash"
            )
            response = model_gemini.generate_content(prompt)
            string_response = str(response.text)
            slogans = encontrar_slogans(string_response, regex_patterns_gpt)
            imgs = []
            for slogan in slogans:
                file_img = criar_gif_slogan_combinado(slogan, brand_name)
                imgs.append(file_img)
            print("Mensagem GPT\n\n", slogans)
            return slogans[:4], imgs
        except Exception as e:
            print("Erro gemini------\n\n", e)
            slogans = ['Slogan 1 é na bump',
                       'Slogan 2 é na bump_media',
                       'Slogan 3 é na media',
                       'Slogan 4 é na bump media',
                       'Slogan 5 é na media_bump']
            imgs = []
            for slogan in slogans:
                file_img = criar_gif_slogan_combinado(slogan, brand_name)
                imgs.append(file_img)
            return slogans[:4], imgs

# Função para gerar dados em tempo real usando a OpenAI
def gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha):
    regex_patterns = [
        r"\d+\.\s*(.*)",
        r"\d+\.\s*([^\d\n]+)(?=\n\d+|\n\n|$)",
        r"\d+\.\s*([^\d]+)"
    ]
    dates = [datetime.strptime(d.strip(), '%d/%m/%Y').strftime('%Y-%m-%d') for d in data_campanha.split("to")]
    weather_response = get_weather_call(dates, get_coordinates(cidade, estado))
    print(weather_response)
    prompt = (
        f"Baseado na localização '{estado}', '{cidade}', '{bairro}', forneça:\n"
        "1. Clima atual\n"
        "2. Hashtags de tendências\n"
        "3. Um evento local relevante\n"
        "4. Um tópico popular de cultura pop atual.\n"
        "Retorne algo similar a: 1. Ensolarado / 2. #rock&rio #sextou / 3. Festa de são joão / 4. Novo albúm da Taylor Swift"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você está puxando informações baseado no nome de estado."},
                {"role": "user", "content": prompt}
            ]
        )
        resposta = str(response['choices'][0]['message']['content'])
        print("Resposta do CLIMA GPT")
        dados = regex_info(resposta, regex_patterns)
        if weather_response:
            weather_value = weather_response
        elif len(dados) > 0:
            weather_value = dados[0]
        else:
            weather_value = "Não disponível"
        conjunto_add_info = {
            "weather": weather_value,
            "trending": dados[1] if len(dados) > 1 else "Não disponível",
            "local_events": dados[2] if len(dados) > 2 else "Não disponível",
            "pop_culture": dados[3] if len(dados) > 3 else "Não disponível",
        }
        print(conjunto_add_info)
        return conjunto_add_info
    except Exception as e:
        print("Erro ao gerar dados em tempo real:", e)
        return {
            "weather": "Erro ao obter dados.",
            "trending": "Erro ao obter dados.",
            "local_events": "Erro ao obter dados.",
            "pop_culture": "Erro ao obter dados.",
        }

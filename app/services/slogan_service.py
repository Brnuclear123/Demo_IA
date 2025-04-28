from config import config 
conf = config['development']

import os
import json
import re
import time
import requests
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip
import openai


# ======================================================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================================================
WEATHER_JSON = conf.WEATHER_JSON            # 'static/data/weather-cd.json'
AVALIACOES_PATH = conf.AVALIACOES_PATH      # 'avaliacoes.json'

FONT_PATH = conf.FONT_PATH                  # 'static/fonte/Bison-Bold.ttf'
LOGOS_PATH = conf.LOGOS_PATH
VIDEOS_PATH = conf.VIDEOS_PATH
FUNDO_IMAGEM_PATH = conf.FUNDO_IMAGEM_PATH  # 'static/frames/meu_fundo.png'
IMAGEM_FINAL_PATH = conf.IMAGEM_FINAL_PATH

ENVIROMENT_DATA = conf.ENVIROMENT_DATA      # 'env_variables.json'

# ======================================================================
# FUNÇÕES UTILITÁRIAS (GENÉRICAS)
# ======================================================================

def tudo_maiusculo(texto):
    """Transforma o texto inteiro em maiúsculo."""
    return texto.upper()

def remover_enum(texto):
    """Remove a enumeração no formato '1. ', '2. ', etc."""
    return re.sub(r'^\d+\.\s*', '', texto)
    
def gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha):
    """
    Gera dados em tempo real (clima, tendências, eventos) para campanhas.
    
    Args:
        estado (str): Estado da campanha (ex: "SP").
        cidade (str): Cidade da campanha (ex: "São Paulo").
        bairro (str): Bairro da campanha (ex: "Centro").
        data_campanha (str): Data no formato "DD/MM/YYYY" ou "DD/MM/YYYY to DD/MM/YYYY".
    
    Returns:
        dict: Dados formatados com:
            - weather (str): Clima atual.
            - trending (str): Hashtags em tendência.
            - local_events (str): Eventos locais.
            - pop_culture (str): Tópico de cultura pop.
    """
    # --- 1. Tratamento da Data ---
    dates = []
    try:
        if "to" in data_campanha:
            date_parts = data_campanha.split("to")
            for date_part in date_parts:
                date_obj = datetime.strptime(date_part.strip(), '%d/%m/%Y')
                dates.append(date_obj.strftime('%Y-%m-%d'))
        else:
            date_obj = datetime.strptime(data_campanha.strip(), '%d/%m/%Y')
            dates.append(date_obj.strftime('%Y-%m-%d'))
    except Exception as e:
        print(f"Erro ao processar datas: {e}")
        dates = [datetime.now().strftime('%Y-%m-%d')]  # Fallback para data atual

    # --- 2. Obter Dados de Clima (API Externa) ---
    weather_data = None
    try:
        coordinates = get_coordinates(cidade, estado)  # Função fictícia (substitua pela sua)
        weather_data = get_weather_call(dates, coordinates)  # Função fictícia
        print(f"Dados do clima obtidos: {weather_data}")
    except Exception as e:
        print(f"Erro ao buscar clima: {e}")

    # --- 3. Gerar Prompt para o GPT ---
    prompt = f"""
    Para a localização: {cidade}, {bairro}, {estado}, retorne EXATAMENTE no formato:
    TEMPERATURA: Max [valor]°C e Min [valor]°C [clima] /
    HASHTAGS: #[tag1] #[tag2] /
    EVENTO: [nome do evento] /
    CULTURA POP: [tópico]

    Dados reais do clima (se disponível): {weather_data}
    """

    # --- 4. Chamada ao GPT-4 ---
    gpt_response = None
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Siga estritamente o formato solicitado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        gpt_response = str(response['choices'][0]['message']['content'])
        print(f"Resposta do GPT: {gpt_response}")

          # Aplica os tratamentos
        gpt_response = remover_enum(gpt_response)
        gpt_response = tudo_maiusculo(gpt_response)
        
    except Exception as e:
        print(f"Erro ao chamar GPT: {e}")
        return {
            "weather": "Erro: Dados indisponíveis",
            "trending": "Erro: Dados indisponíveis",
            "local_events": "Erro: Dados indisponíveis",
            "pop_culture": "Erro: Dados indisponíveis"
        }

    # --- 5. Parsear Resposta do GPT ---
    def parse_gpt_response(response_text):
        weather = trending = local_events = pop_culture = "Dados indisponíveis"

        try:
            temp_match = re.search(r"TEMPERATURA:\s*(.*?)\s*/", response_text)
            hashtags_match = re.search(r"HASHTAGS:\s*(.*?)\s*/", response_text)
            evento_match = re.search(r"EVENTO:\s*(.*?)\s*/", response_text)
            cultura_match = re.search(r"CULTURA POP:\s*(.*)", response_text)

            if temp_match:
                weather = temp_match.group(1).strip()
            if hashtags_match:
                trending = hashtags_match.group(1).strip()
            if evento_match:
                local_events = evento_match.group(1).strip()
            if cultura_match:
                pop_culture = cultura_match.group(1).strip()

        except Exception as e:
            print(f"Erro ao parsear resposta do GPT: {e}")

        return {
            "weather": weather,
            "trending": trending,
            "local_events": local_events,
            "pop_culture": pop_culture
        }

    return parse_gpt_response(gpt_response)

def js_read(filename: str) -> dict:
    """Lê arquivos JSON."""
    with open(filename, 'r', encoding='utf-8') as j_file:
        return json.load(j_file)

def carregar_avaliacoes() -> dict:
    """Carrega avaliações salvas."""
    if os.path.exists(AVALIACOES_PATH):
        with open(AVALIACOES_PATH, 'r') as file:
            return json.load(file)
    return {}

def salvar_avaliacoes(avaliacoes: dict) -> None:
    """Salva avaliações no arquivo JSON."""
    with open(AVALIACOES_PATH, 'w') as file:
        json.dump(avaliacoes, file, indent=4)

def ultimos_slogans() -> list:
    """Retorna os últimos 4 slogans gerados (arquivos PNG)."""
    diretorio = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static')
    arquivos_png = [f for f in os.listdir(diretorio) if f.endswith('.png')]
    return arquivos_png[-4:]

# ======================================================================
# FUNÇÕES DE WEATHER (GENÉRICAS)
# ======================================================================
def get_coordinates(city: str, state: str, country: str = "Brasil") -> tuple:
    """Obtém coordenadas geográficas via OpenStreetMap."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {'city': city, 'state': state, 'country': country, 'format': 'json'}
    headers = {'User-Agent': 'YourAppName/1.0 (your@email.com)'}

    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return (data['lat'], data['lon'])
    except Exception as e:
        print(f"Erro ao obter coordenadas: {e}")
    return (None, None)

def get_weather_description(code: int) -> str:
    """Traduz código de clima para descrição."""
    with open(WEATHER_JSON, 'r', encoding='utf-8') as file:
        weather_codes = json.load(file)
    return weather_codes.get(str(code), {}).get('description', "Código não encontrado.")

def get_weather_call(date_forecast: list, lat_lon: list = [-10, -55]) -> str:
    """Obtém previsão do tempo para uma data específica."""
    try:
        today = datetime.now().date()
        target_date = datetime.strptime(date_forecast[0], '%Y-%m-%d').date()
        days_diff = (target_date - today).days

        if not 0 <= days_diff <= 7:
            return "Previsão disponível apenas para os próximos 7 dias."

        params = {
            "latitude": lat_lon[0],
            "longitude": lat_lon[1],
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min"],
            "timezone": "America/Sao_Paulo",
            "start_date": date_forecast[0],
            "end_date": date_forecast[1]
        }

        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        response.raise_for_status()

        daily = response.json().get('daily', {})
        weather_code = daily.get('weather_code', [None])[0]
        temp_max = daily.get('temperature_2m_max', [None])[0]
        temp_min = daily.get('temperature_2m_min', [None])[0]

        if None in [weather_code, temp_max, temp_min]:
            raise ValueError("Dados meteorológicos incompletos.")

        description = get_weather_description(weather_code)
        return f"Max: {temp_max} °C / Min: {temp_min} °C\n{description}"

    except Exception as e:
        print(f"Erro na API de clima: {e}")
        return "Dados meteorológicos indisponíveis."

# ======================================================================
# FUNÇÕES DE GIF (GENÉRICAS)
# ======================================================================
def criar_gif_slogan_combinado(slogan_texto: str, brand_name: str) -> str:
    # = = = = = = = = = = = = = = = =
    # Config da variavel de ambiente
    # = = = = = = = = = = = = = = = =
    
    if brand_name == "Corona":
        path_FONT = FONT_PATH['corona']
        path_LOGOS = LOGOS_PATH['corona']
        path_VIDEOS = VIDEOS_PATH['corona']
        path_FUNDO_IMAGEM = FUNDO_IMAGEM_PATH['corona']
        path_IMAGEM_FINAL = IMAGEM_FINAL_PATH['corona']
    elif brand_name == "Lacta":
        path_FONT = FONT_PATH['lacta']
        path_LOGOS = LOGOS_PATH['lacta']
        path_VIDEOS = VIDEOS_PATH['lacta']
        path_FUNDO_IMAGEM = FUNDO_IMAGEM_PATH['lacta']
        path_IMAGEM_FINAL = IMAGEM_FINAL_PATH['lacta']
    elif brand_name == "Bauducco":
        path_FONT = FONT_PATH['bauducco']
        path_LOGOS = LOGOS_PATH['bauducco']
        path_VIDEOS = VIDEOS_PATH['bauducco']
        path_FUNDO_IMAGEM = FUNDO_IMAGEM_PATH['bauducco']
        path_IMAGEM_FINAL = IMAGEM_FINAL_PATH['bauducco']


    """Gera GIF animado com o slogan."""
    dt_now = datetime.now()
    base_filename = f"slogan_animado{dt_now.strftime('%Y%m%d%H%M%S')}{str(dt_now.microsecond)[:2].zfill(2)}"
    largura, altura = 1920, 158

    # Configuração de cores por marca
    bg_color = "#333333" if brand_name in ["Corona", "Lacta", "Bauducco"] else "#FFFFFF"
    text_color = "white" if brand_name in ["Corona", "Lacta", "Bauducco"] else "black"

    # Carrega imagem de fundo ou cria uma padrão
    if os.path.exists(path_FUNDO_IMAGEM):
        print(path_FUNDO_IMAGEM)
        imagem_base = Image.open(path_FUNDO_IMAGEM).resize((largura, altura)).convert("RGBA")
    else:
        imagem_base = Image.new("RGBA", (largura, altura), bg_color)

    # Imagem de final de vídeo
    if os.path.exists(path_IMAGEM_FINAL):
        baseplate_img = Image.open(path_IMAGEM_FINAL).resize((largura, altura)).convert("RGBA")
    else:
        baseplate_img = None

    # Configuração de fonte
    try:
        font = ImageFont.truetype(path_FONT, 64)
    except IOError:
        font = ImageFont.load_default()

    # Cálculo de posição do texto
    temp_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    total_width = sum(font.getbbox(char)[2] - font.getbbox(char)[0] for char in slogan_texto)
    pos_x = (largura - total_width) // 2
    pos_y = (altura - (font.getbbox(slogan_texto)[3] - font.getbbox(slogan_texto)[1])) // 2

    # Animação letra por letra
    frames = []
    for frame_idx in range(len(slogan_texto) * 5 + 160):  # 5 frames por letra + 160 frames finais
        frame = imagem_base.copy()
        overlay = Image.new("RGBA", (largura, altura), (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        current_x = pos_x
        for char_idx, char in enumerate(slogan_texto):
            if frame_idx >= char_idx * 5 and frame_idx < char_idx * 5 + 10:
                alpha = min(255, (frame_idx - char_idx * 5) * 25)
                offset_y = int(10 * (1 - (frame_idx - char_idx * 5) / 5))
                draw.text(
                    (current_x, pos_y + offset_y),
                    char,
                    font=font,
                    fill=((255, 255, 255, alpha) if text_color == "white" else (0, 0, 0, alpha))
                )
            elif frame_idx >= char_idx * 5 + 10:
                draw.text(
                    (current_x, pos_y),
                    char,
                    font=font,
                    fill=text_color
                )

            current_x += font.getbbox(char)[2] - font.getbbox(char)[0]

        frame.paste(overlay, (0, 0), overlay)
        frames.append(np.array(frame.convert("RGB")))

    # Salva como vídeo
    clip = ImageSequenceClip(frames, fps=24)
    video_path = os.path.join("static", f"{base_filename}.mp4")
    clip.write_videofile(video_path, codec="libx264", fps=24, logger=None)
    return video_path

# ======================================================================
# FUNÇÕES AUXILIARES
# ======================================================================
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

def extrair_slogans(texto: str) -> list:
    """Extrai slogans de texto usando regex."""
    padroes = [
        r'"([^"]+)"',
        r'^\d+\.\s*(.+)$',
        r'^-\s*(.+)$'
    ]
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.MULTILINE)
        if len(matches) >= 4:
            return matches[:4]
    return ["Slogan não disponível"] * 4


#service_checado
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
from moviepy.editor import ImageSequenceClip, VideoFileClip, concatenate_videoclips, vfx, CompositeVideoClip, ImageClip
from moviepy.editor import vfx  # Add this line to import vfx
import openai
import google.generativeai as genai
import cv2

# CONSTANTES retiradas do config.py
WEATHER_JSON = conf.WEATHER_JSON            # ex.: 'static/data/weather-cd.json'
AVALIACOES_PATH = conf.AVALIACOES_PATH      # ex.: 'avaliacoes.json'
FONT_PATH = conf.FONT_PATH                  # ex.: 'static/fonte/Bison-Bold(PersonalUse).ttf'
FUNDO_IMAGEM_PATH = "static/frames/fundo_1.mp4" # ex.: 'static/frames/meu_fundo.png'
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
    print(date_forecast,"\n\n","data do dia")
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

def dia_da_semana(date_str):
    dates = [datetime.strptime(d.strip(), '%d/%m/%Y').strftime('%Y-%m-%d') for d in date_str.split("to")]
    print(dates)
    dayofweek = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
    date = datetime.strptime(dates[0], '%Y-%m-%d').date()
    return dayofweek[date.weekday()]

def evento_social():
    #função do evento social
    pass

# Função para criar GIF animado dos slogans
def criar_gif_slogan_combinado(slogan_texto, brand_name):
    print("Slogan Texto: ", slogan_texto)

    # TODO: change this refernce
    base_path_clip_1 = "static/frames/fundo_1.mp4"
    image_path_clip_2 = "static/src/corona_baseplate.png"

    base_path_clip_2 = create_image_clip(image_path_clip_2, 5)
     
    # TODO: write this function
    processed_clip_path = process_and_add_text(base_path_clip_1, slogan_texto)

    return concatenate_videos(processed_clip_path, base_path_clip_2)

def create_image_clip(baseplate_path, duration):
    from PIL import Image
    import numpy as np
    from moviepy.editor import ImageClip
    import os
    
    # Create directory if it doesn't exist
    os.makedirs("temp", exist_ok=True)
    
    output_filename = "temp/final_video_baseplace_final.mp4"
    
    # Manually resize the image with PIL first
    try:
        # For newer versions of Pillow
        pil_image = Image.open(baseplate_path).resize((1920, 158), Image.LANCZOS)
    except AttributeError:
        try:
            # For newer versions with different naming
            pil_image = Image.open(baseplate_path).resize((1920, 158), Image.Resampling.LANCZOS)
        except AttributeError:
            # For older versions of Pillow
            pil_image = Image.open(baseplate_path).resize((1920, 158), Image.ANTIALIAS)
    
    # Convert PIL image to numpy array
    img_array = np.array(pil_image)
    
    # Create image clip from numpy array
    image_clip = ImageClip(img_array).set_duration(duration)
    
    # Set fps explicitly when writing the video file
    fps = 24  # Standard video frame rate
    image_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac", fps=fps)
    
    return output_filename

def concatenate_videos(base_path_clip_1, base_path_clip_2):
    output_filename = "output_video_final.mp4";

    clip1 = VideoFileClip(base_path_clip_1)
    clip2 = VideoFileClip(base_path_clip_2)

    # Set the duration for the fade effect
    fade_duration = 2  # seconds

    # Create fade-out effect for the first clip
    clip1_fadeout = clip1.fx(vfx.fadeout, fade_duration)

    # Create fade-in effect for the second clip
    clip2_fadein = clip2.fx(vfx.fadein, fade_duration)

    # Concatenate the clips with the transitions
    final_clip = concatenate_videoclips([clip1_fadeout, clip2_fadein], method="compose")

    # Write the result to a file
    final_clip.write_videofile(output_filename, codec="libx264", audio_codec="aac")

    return output_filename

def process_and_add_text(first_clip_path, slogan_text):
    # Create output directory if it doesn't exist
    output_dir = "static/processed"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique output filename
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = f"{output_dir}/video_with_text_{timestamp}.mp4"
    
    # Font path
    font_path = 'static/fonte/Bison-Bold(PersonalUse).ttf'
    if not os.path.exists(font_path):
        # Fallback to a system font if the specific font doesn't exist
        font_path = cv2.FONT_HERSHEY_SIMPLEX
        use_pil_font = False
    else:
        use_pil_font = True
    
    # Open the video
    cap = cv2.VideoCapture(first_clip_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {first_clip_path}")
        return first_clip_path  # Return original path if can't process
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Configure output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Font settings
    font_size = height // 4  # Adjust font size based on video height
    if use_pil_font:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            print(f"Error loading font {font_path}, using default")
            font = ImageFont.load_default()
    
    # Calculate how many frames to show text (10 seconds or entire video if shorter)
    text_duration_seconds = 10
    max_text_frames = min(int(fps * text_duration_seconds), total_frames)
    
    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Add text only for the first 10 seconds
        if frame_number < max_text_frames:
            # Convert OpenCV frame to PIL Image for better text rendering
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw = ImageDraw.Draw(pil_img)
            
            # Center the text
            text_size = draw.textbbox((0, 0), slogan_text, font=font)
            text_width = text_size[2] - text_size[0]
            text_height = text_size[3] - text_size[1]
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            
            # Add text with animation effect (fade in/out)
            alpha = 255
            if frame_number < fps:  # Fade in during first second
                alpha = int(255 * (frame_number / fps))
            elif frame_number > max_text_frames - fps:  # Fade out during last second
                alpha = int(255 * (max_text_frames - frame_number) / fps)
            
            # Draw text with calculated alpha
            draw.text((text_x, text_y), slogan_text, font=font, fill=(255, 255, 255, alpha))
            
            # Convert back to OpenCV format
            frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        # Write the frame
        out.write(frame)
        frame_number += 1
    
    # Release resources
    cap.release()
    out.release()
    
    print(f"✅ Video with text successfully generated: {output_path}")
    return output_path

# Função para gerar slogans e GIFs a partir do prompt
def gerar_slogans_e_gifs(estado, cidade, bairro, data_campanha, momento, brand_name, real_time_data):
    #real_time_data.weather
    regex_patterns_gpt = [
        r'(.+?)\s{2,}',
        r'"([^"]+)"',
        r'\d+\.\s*(.+?)(?=\n|$)',
        r'^(.+?)$',
        r'(.+?)(?:\s{2,}|(?=\n|$))'
    ]
    
    if brand_name == "Corona":
        prompt = (f"""
            Você é uma inteligência criativa especializada em redigir mensagens curtas, impactantes e sensoriais para a marca de cerveja Corona no Brasil.
            Crie 4 variações de mensagens publicitárias com no máximo 75 caracteres para exibição em tela digital no ponto de venda.
            Não enumere os slogans, não use aspas nos slogans e evite usar pontuações desnecesarias para não ficar carregado.
            Use {dia_da_semana(data_campanha)} para criar slogans com dias especiais como pro exemplo 5 de junho dia mundial do meio ambiente.
            evite repetir o nome do {estado}, '{cidade}', '{bairro} nos slogans, seja mais criativo e use de outros recursos para elaborar o slogan.
            Use os seguintes dados dinâmicos como contexto de inspiração:
            - Temperatura: {real_time_data['weather']}°C
            - Horário: {momento}
            - Dia da semana: {dia_da_semana(data_campanha)}
            - Localização: '{estado}, '{cidade}', '{bairro}'

            A mensagem deve refletir o estilo e tom de voz da marca Corona:
            → Leve, sensorial, inspirador
            → Evocar natureza: sol, mar, brisa, céu, areia, limão
            → Estilo de vida livre, ao ar livre, com frescor e pausa
            → Público jovem (18-35), ligado à música, sunset, esportes, natureza
            → Não pode conter emojis

            Frase-conceito de fundo: "Corona é inspirada na natureza, não feita da natureza."

            Importante: evite soar como propaganda direta. A mensagem deve parecer uma fala espontânea de alguém relaxando ao ar livre com uma cerveja gelada.

            Exemplos de boas saídas:
            - "O pôr-do-sol é só o começo. Brinde com o que vem depois."
            - "Sol na pele, limão na garrafa, e o tempo jogando a favor."
            """)
        
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
            # model="gpt-4-turbo",
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Assuma que você é um redador publicitário especialista em mensagens curtas, rápidas e inteligentes sem precisar que enumere os slogans, sem a utilização de aspas e evita pontuações desnecesarias, um publicitario que é atento aos calendadriaos festivos que fazem sentido para a marcas"},
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
        r"^- (.+)$",
        r"^\d+\.\s(.+)$",
        r"^\d+-\s(.+)$",
        r"^\d+:\s(.+)$",
        r"^- (.+)$",
        r"([^/]+)"
    ]
    dates = [datetime.strptime(d.strip(), '%d/%m/%Y').strftime('%Y-%m-%d') for d in data_campanha.split("to")]
    weather_response = get_weather_call(dates, get_coordinates(cidade, estado))
    print(weather_response)
    prompt = (
        f"Baseado na localização '{estado}', '{cidade}', '{bairro}', forneça:\n"
        "- Temperatura máxima e mínima e clima atual\n"
        "- Hashtags de tendências\n"
        "- Um evento local relevante\n"
        "- Um tópico popular de cultura pop atual.\n"
        "Retorne algo similar a: Max 25°C e Max 20°C Ensolarado / #rock&rio #sextou / Festa de são joão & Festa de aniversário da cidade / Novo albúm da Taylor Swift"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Você está puxando informações baseado no nome de estado. O retorno é feito com tópicos e separado por '/'"},
                {"role": "user", "content": prompt}
            ]
        )
        resposta = str(response['choices'][0]['message']['content'])
        print("Resposta do CLIMA GPT")
        print(resposta)
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
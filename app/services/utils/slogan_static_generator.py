import os
import re
import numpy as np
import string
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from config import config

conf = config['development']

# ======================================================================
# CONSTANTES E CONFIGURAÇÕES
# ======================================================================
FONT_PATH = conf.FONT_PATH
FUNDO_IMAGEM_PATH = conf.FUNDO_IMAGEM_PATH
IMAGEM_FINAL_PATH = conf.IMAGEM_FINAL_PATH

class SloganStaticGenerator:
    """
    Classe responsável por gerar imagens estáticas com slogans para diferentes marcas.
    """
    
    def __init__(self, brand_name):
        """
        Inicializa o gerador com as configurações específicas da marca.
        
        Args:
            brand_name (str): Nome da marca (Corona, Lacta, Bauducco)
        """
        self.brand_name = brand_name
        self._load_brand_config()
        
    def _load_brand_config(self):
        """Carrega as configurações específicas da marca."""
        if self.brand_name == "Corona":
            self.path_font = FONT_PATH['corona']
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH['corona']
            self.path_imagem_final = IMAGEM_FINAL_PATH['corona']
            self.bg_color = "#333333"
            self.text_color = "white"
            self.font_size = 73.68
        elif self.brand_name == "Lacta":
            self.path_font = FONT_PATH['lacta']
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH['lacta']
            self.path_imagem_final = IMAGEM_FINAL_PATH['lacta']
            self.bg_color = "#333333"
            self.text_color = "white"
            self.font_size = 55
        elif self.brand_name == "Bauducco":
            self.path_font = FONT_PATH['bauducco']
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH['bauducco']
            self.path_imagem_final = IMAGEM_FINAL_PATH['bauducco']
            self.bg_color = "#333333"
            self.text_color = "#FFEE70"
            self.font_size = 55
        else:
            self.path_font = FONT_PATH.get('default', 'static/fonte/default.ttf')
            self.path_fundo_imagem = FUNDO_IMAGEM_PATH.get('default', 'static/frames/default.png')
            self.path_imagem_final = IMAGEM_FINAL_PATH.get('default', 'static/frames/default_final.png')
            self.bg_color = "#FFFFFF"
            self.text_color = "black"
    
    def _clean_slogan(self, text):
        # remove leading enumeration (e.g., '1. ', '2) ')
        text = re.sub(r'^\s*\d+[\.\)\-]\s*', '', text)
        # remove emojis and non-standard punctuation
        text = text.encode('ascii', 'ignore').decode()  # strip non-ascii
        # remove unwanted punctuation
        text = text.translate(str.maketrans('', '', string.punctuation.replace('&', '')))
        # collapse whitespace and uppercase
        return ' '.join(text.split()).upper()


    def generate_static_image(self, slogan_text, output_path=None):
        """
        Gera uma imagem estática com o slogan.
        
        Args:
            slogan_text (str): Texto do slogan
            output_path (str, optional): Caminho para salvar a imagem. Se None, gera um nome baseado na data/hora.
            
        Returns:
            str: Caminho da imagem gerada
        """
        # Definir dimensões
        largura, altura = 1920, 158
        
        # Gerar nome do arquivo se não fornecido
        if output_path is None:
            dt_now = datetime.now()
            base_filename = f"slogan_static_{self.brand_name.lower()}_{dt_now.strftime('%Y%m%d%H%M%S')}{str(dt_now.microsecond)[:2].zfill(2)}.png"
            output_path = os.path.join("static", base_filename)
        
        # Carrega imagem de fundo ou cria uma padrão
        if os.path.exists(self.path_fundo_imagem):
            imagem_base = Image.open(self.path_fundo_imagem).resize((largura, altura)).convert("RGBA")
        else:
            imagem_base = Image.new("RGBA", (largura, altura), self.bg_color)
        
        # Configuração de fonte inicial        
        horizontal_margin = int(largura * 0.05)  # 5% de margem em cada lado
        max_text_width = largura - (2 * horizontal_margin)
        max_text_height = int(altura * 0.7)  # 70% da altura máxima
        
        # Encontrar o tamanho de fonte ideal usando busca binária
        min_size = 10
        max_size = self.font_size 
        font = None
        font_size = max_size
        text_width = largura + 1  # Inicializar maior que o máximo para entrar no loop
        text_height = altura + 1
        
        print(f"Iniciando busca de tamanho de fonte: min={min_size}, max={max_size}")
        print(f"Texto a medir: '{slogan_text}'")
        
        while min_size <= max_size:
            mid_size = (min_size + max_size) // 2
            try:
                print(f"Testando tamanho de fonte: {mid_size}")
                test_font = ImageFont.truetype(self.path_font, mid_size)
                
                # Criar uma imagem temporária para medir o texto
                temp_img = Image.new("RGB", (1, 1))
                temp_draw = ImageDraw.Draw(temp_img)
                
                # Medir o texto
                bbox = temp_draw.textbbox((0, 0), slogan_text, font=test_font)
                current_width = bbox[2] - bbox[0]
                current_height = bbox[3] - bbox[1]
                
                print(f"Dimensões do texto: largura={current_width}, altura={current_height}")
                print(f"Máximo permitido: largura={max_text_width}, altura={max_text_height}")
                
                if current_width <= max_text_width and current_height <= max_text_height:
                    # Este tamanho cabe, tente um maior
                    font = test_font
                    font_size = mid_size
                    text_width = current_width
                    text_height = current_height
                    min_size = mid_size + 1
                    print(f"Tamanho de fonte {mid_size} cabe, tentando maior")
                else:
                    # Muito grande, tente menor
                    max_size = mid_size - 1
                    print(f"Tamanho de fonte {mid_size} muito grande, tentando menor")
            except Exception as e:
                print(f"Erro ao carregar fonte no tamanho {mid_size}, tentando menor")
                print(f"Erro: {e}")
                max_size = mid_size - 1
        
        # Se não encontramos uma fonte adequada, use a padrão
        if font is None:
            print("Não foi possível encontrar um tamanho de fonte adequado, usando padrão")
            font_size = min(20, altura // 4)  # Use um tamanho menor como padrão
            try:
                font = ImageFont.truetype(self.path_font, font_size)
            except Exception as e:
                print(f"Erro ao carregar fonte padrão: {e}")
                font = ImageFont.load_default()
        
        print(f"Tamanho de fonte selecionado: {font_size} para dimensões de texto: {text_width}x{text_height}")
        
        # Cálculo de posição do texto
        # Centralizar horizontalmente
        pos_x = (largura - text_width) // 2
        
        # Centralizar verticalmente
        pos_y = (altura - text_height) // 2
        
        # Desenhar o texto
        draw = ImageDraw.Draw(imagem_base)
        
        # Converter cor de texto para RGB se for uma string hexadecimal
        text_color = self.text_color
        if isinstance(text_color, str) and text_color.startswith('#'):
            # Converter hex para RGB
            text_color = text_color[1:]  # Remover o #
            r = int(text_color[0:2], 16)
            g = int(text_color[2:4], 16)
            b = int(text_color[4:6], 16)
            text_color = (r, g, b)
        
        draw.text(
            (pos_x, pos_y),
            slogan_text,
            font=font,
            fill=text_color
        )
        
        # Salvar a imagem
        imagem_base.save(output_path)
        
        return output_path
    
    def generate_static_images(self, slogans, output_dir=None):
        """
        Gera imagens estáticas para uma lista de slogans.
        
        Args:
            slogans (list): Lista de textos de slogans
            output_dir (str, optional): Diretório para salvar as imagens
            
        Returns:
            list: Lista de caminhos das imagens geradas
        """
        if output_dir is None:
            output_dir = "static"
            
        image_paths = []
        for slogan in slogans:
            image_path = self.generate_static_image(slogan)
            image_paths.append(image_path)
            
        return image_paths

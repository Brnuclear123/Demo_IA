import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

# Caminhos
video_path = 'static/frames/meu_fundo.mp4'
output_path = 'static/frames/video_com_texto.mp4'
font_path = 'static/fonte/Bison-Bold(PersonalUse).ttf'

slogan = "Onde o sol se põe, a Corona se abre. Refresque seu momento."

# Abrir vídeo original
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Erro ao abrir o vídeo.")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps)

# Configura saída
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

# Fonte
font_size = 40
font = ImageFont.truetype(font_path, font_size)

frame_number = 0
text_duration_seconds = 10
max_text_frames = int(fps * text_duration_seconds)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Desenhar texto só nos primeiros 10 segundos
    if frame_number <= max_text_frames:
        # Converte o frame do OpenCV para PIL
        pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(pil_img)

        # Centraliza o texto
        text_size = draw.textbbox((0, 0), slogan, font=font)
        text_width = text_size[2] - text_size[0]
        text_height = text_size[3] - text_size[1]
        text_x = (width - text_width) // 2
        text_y = (height - text_height) // 2

        # Desenha
        draw.text((text_x, text_y), slogan, font=font, fill=(255, 255, 255))

        # Converte de volta para OpenCV
        frame = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    out.write(frame)
    frame_number += 1

cap.release()
out.release()

print("✅ Vídeo com slogan gerado com sucesso!")

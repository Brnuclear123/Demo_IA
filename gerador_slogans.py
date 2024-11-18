import os
from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from werkzeug.security import generate_password_hash, check_password_hash

# Carregar a chave API do arquivo .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

app = Flask(__name__)
app.secret_key = 'secret_key'

# Simulação de um banco de dados de usuários
users = {
    'corona': {'password': generate_password_hash('1234'), 'brand': 'Corona'},
    'lacta': {'password': generate_password_hash('1234'), 'brand': 'Lacta'}
}

# Função para criar uma imagem de slogan
def criar_imagem_slogan(slogan_texto, brand_name, output_filename="slogan_imagem.png"):
    largura, altura = 960, 120
    
    # Definições de estilo específicas para cada marca
    if brand_name == "Corona":
        bg_color = "#004AAD"  # Cor de fundo da Corona
        text_color = "white"  # Cor do texto para Corona
        border_color = "black"  # Cor da borda
        font_path = "arial.ttf"  # Fonte padrão; altere conforme necessário
    elif brand_name == "Lacta":
        bg_color = "#4b2a6b"  # Cor de fundo da Lacta
        text_color = "white"  # Cor do texto para Lacta
        border_color = "black"  # Borda 
        font_path = "arial.ttf"  # Fonte para Lacta, altere se necessário
    else:
        bg_color = "#333"  # Cor padrão para outras marcas
        text_color = "white"
        border_color = "black"
        font_path = "arial.ttf"

    # Criação da imagem
    imagem = Image.new("RGB", (largura, altura), bg_color)
    draw = ImageDraw.Draw(imagem)

    # Carregar a fonte, ajustando o caminho conforme necessário
    try:
        font = ImageFont.truetype(font_path, 28)
    except IOError:
        font = ImageFont.load_default()

    # Calcular a posição do texto para centralizar
    bbox = draw.textbbox((0, 0), slogan_texto, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (largura - text_width) / 2
    y = (altura - text_height) / 2

    # Adicionar a borda ao redor da imagem
    border_thickness = 5
    draw.rectangle([(0, 0), (largura - 1, altura - 1)], outline=border_color, width=border_thickness)

    # Adicionar o texto à imagem
    draw.text((x, y), slogan_texto, font=font, fill=text_color)

    # Salvar a imagem na pasta `static`
    output_path = os.path.join("static", output_filename)
    os.makedirs("static", exist_ok=True)
    imagem.save(output_path)
    print(f"Imagem salva em {output_path}")


# Função para gerar slogans e criar imagens
def gerar_slogans(localizacao, tema, brand_name):
    # Prompt específico para cada marca
    if brand_name == "Corona":
        prompt = (
        f"Crie quatro slogans publicitários exclusivos e de alto impacto para a marca Corona, "
        f"Use o '{localizacao}' para criar slogans que tenha contexto com a localidade. Esta campanha é direcionada ao público de 18 a 35 anos com o tema '{tema}', "
        f"utilizando um tom de voz de alegria para transmitir uma sensação de prestígio, sofisticação e valor agregado. "
        "precisamos que limite o uso de caracter para que não exceda, não pode passar de 100 caracteres"
        "Cada slogan deve ser envolvente, destacar a exclusividade da marca e incluir uma chamada para ação (CTA) que inspire desejo e urgência. "
        "Separe cada slogan com uma quebra de linha e garanta que sejam quatro slogans únicos."
        "slogans que pode ser rimados seria muito bom, para grudar na cabeça do cliente, mas mantendo a criatividade e os 45 caracteres "
        "vamos colocar mais criatividade nesses slogans, quero algo mais intuitivo de acordo com suas marcas."
        "não coloque datas nos slogans, use as datas para indentificar o dia da semana e aproveite para usar a seu favor."
        "quero apenas o slogans, não é para colocar corona:, isso não deixa os slogans profisionais, gere apenas slogans."
        "Regra basica, quando colocar a localização no slogam sempre açocie a marca, se não tiver a localização apenas o slogam com a marca."
        "nunca deixe de mencionar a marca Corona."
        "eu quero concordancia nas frases dos slogans, sempre tenta manter uma concordancia verbal para um maior entendimento do publico."
        "No caso de o dia selecionado for Quarta feira subistitua para Quartou, Quinta feira subistitua para Quintou e se for Sexta feira subistitua para Sextou."
        " Coloque corona no cenario de natureza."
        )
    elif brand_name == "Lacta":
        prompt = (
        f"Crie quatro slogans publicitários exclusivos e de alto impacto para a marca Lacta, "
        f"Use o '{localizacao}' para criar slogans que tenha contexto com a localidade. Esta campanha é direcionada ao público de 18 a 35 anos com o tema '{tema}', "
        f"utilizando um tom de voz de emocional e afetivo para transmitir uma sensação de prestígio, acolhimento e valor agregado positivo. "
        "precisamos que limite o uso de caracter para que não exceda, não pode passar de 45 caracteres"
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
        "No caso de o dia selecionado for Quarta feira subistitua para Quartou, Quinta feira subistitua para Quintou e se for Sexta feira subistitua para Sextou."
        
        )

    try:
        response = genai.GenerativeModel(model_name='gemini-1.5-flash').generate_content(prompt)
        slogans = [slogan.strip() for slogan in response.text.split("\n") if slogan.strip()]

        # Garante que temos quatro slogans
        while len(slogans) < 4:
            slogans.append("Slogan adicional não disponível.")

        # Cria imagens para cada slogan com base na marca
        for i, slogan in enumerate(slogans, start=1):
            criar_imagem_slogan(slogan, brand_name, f"slogan_imagem_{i}.png")

        return slogans[:4]
    except Exception as e:
        print("Erro ao gerar slogans:", e)
        return ["Erro ao gerar o slogan. Tente novamente.", "", "", ""]

@app.route('/')
def index():
    return redirect(url_for('login'))

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['brand_name'] = user['brand']
            
            # Redireciona com base na marca do usuário
            if user['brand'] == 'Corona':
                return redirect(url_for('corona'))
            elif user['brand'] == 'Lacta':
                return redirect(url_for('lacta'))
        else:
            error = "Login falhou. Verifique suas credenciais."
    
    return render_template('login.html', error=error)


# Rota para a página exclusiva da Corona
@app.route('/corona', methods=['GET', 'POST'])
def corona():
    if 'username' in session and session['brand_name'] == 'Corona':
        if request.method == 'POST':
            tema = request.form.get('tema')
            localizacao = request.form.get('localizacao')
            slogans = gerar_slogans(localizacao, tema, "Corona")
            imagens = [f"slogan_imagem_{i}.png" for i in range(1, len(slogans) + 1)]
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('corona.html', slogans_imagens=slogans_imagens)
        return render_template('corona.html')
    else:
        return redirect(url_for('login'))

# Rota para a página exclusiva da Lacta
@app.route('/lacta', methods=['GET', 'POST'])
def lacta():
    if 'username' in session and session['brand_name'] == 'Lacta':
        if request.method == 'POST':
            tema = request.form.get('tema')
            localizacao = request.form.get('localizacao')
            slogans = gerar_slogans(localizacao, tema, "Lacta")
            imagens = [f"slogan_imagem_{i}.png" for i in range(1, len(slogans) + 1)]
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('lacta.html', slogans_imagens=slogans_imagens)
        return render_template('lacta.html')
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from dotenv import load_dotenv
import openai
#from openai import OpenAI 
import json
import os
import re

# Carregar a chave API do arquivo .env
def js_read(filename: str):
    with open(filename) as j_file:
        return json.load(j_file)

data = js_read('env_variables.json')    
        
openai.api_key = data['OPENAI_API_KEY']


app = Flask(__name__)
app.secret_key = 'secret_key'

# Simulação de um banco de dados de usuários
users = {
    'corona': {'password': generate_password_hash('1234'), 'brand': 'Corona'},
    'lacta': {'password': generate_password_hash('1234'), 'brand': 'Lacta'}
}

def encontrar_slogans(string_response, regex_patterns):
    for regex_pattern in regex_patterns:
        slogans = re.findall(regex_pattern, string_response)
        print(f"Testando padrão: {regex_pattern}")
        print(f"Resultados encontrados: {slogans}\n\n")
        if len(slogans) == 4:
            return slogans
    # Se nenhum padrão retornar 4 slogans, retorna uma lista padrão
    return ["Slogan adicional não disponível."] * 4

def regex_info(string_response, regex_patterns):
    for regex_pattern in regex_patterns:
        info = re.findall(regex_pattern, string_response, re.DOTALL)
        print(f"Testando padrão: {regex_pattern}")
        print(f"Resultados encontrados: {info}\n\n")
        if len(info) == 4:
            return info
    info = []
    return info

# Função para criar uma imagem de slogan
def criar_imagem_slogan(slogan_texto, brand_name, output_filename="slogan_imagem.png"):
    largura, altura = 960, 120
    # Definições de estilo específicas para cada marca
    if brand_name == "Corona":
        bg_color = "#004AAD"
        text_color = "white"
    elif brand_name == "Lacta":
        bg_color = "#4b2a6b"
        text_color = "white"
    else:
        bg_color = "#333"
        text_color = "white"

    imagem = Image.new("RGB", (largura, altura), bg_color)
    draw = ImageDraw.Draw(imagem)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except IOError:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), slogan_texto, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (largura - text_width) / 2
    y = (altura - text_height) / 2
    draw.text((x, y), slogan_texto, font=font, fill=text_color)

    output_path = os.path.join("static", output_filename)
    os.makedirs("static", exist_ok=True)
    imagem.save(output_path)
    #print(f"Imagem salva em {output_path}")

# Função para gerar slogans usando a OpenAI
def gerar_slogans(localizacao, tema, brand_name):
    slogans = []
    
    regex_patterns_gpt = [
        r'(.+?)\s{2,}',                   # Captura slogans separados por duas quebras de linha
        r'"([^"]+)"',                      # Captura slogans entre aspas
        r'\d+\.\s*(.+?)(?=\n|$)',          # Captura slogans após números e ponto (1. Slogan)
        r'^(.+?)$',                        # Captura cada linha separada, sem formatação especial
        r'(.+?)(?:\s{2,}|(?=\n|$))'        # Caso tudo falhar, essa regex captura sem numero e só com quebra de linha
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
        f"Use o '{localizacao}' para criar frases que tenha contexto com a localidade."
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
        f"Use '{tema}' para poder te ajudar a gerar algumas frases de acordo com o sendo proposto."
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
        client = openai
        
        response = client.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role":"system", "content": "Assuma que você é um redador publicitário especialista em mensagens curtas, rápidas e inteligentes"},
                {"role":"user", "content": prompt}
            ]
        )
        string_response = str(response.choices[0].message.content)
        print(string_response)

        slogans = encontrar_slogans(string_response, regex_patterns_gpt)

        # Criar imagens para cada slogan
        for i, slogan in enumerate(slogans, start=1):
            criar_imagem_slogan(slogan, brand_name, f"slogan_imagem_{i}.png")

        print("Mensagem GPT\n\n",slogans)

        return slogans[:4]
    except Exception as e:
        print("Erro ao gerar slogans:", e)
        #return ["Erro ao gerar o slogan. Tente novamente.", "", "", ""]

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
            
            # Criar imagens para cada slogan
            for i, slogan in enumerate(slogans, start=1):
                criar_imagem_slogan(slogan, brand_name, f"slogan_imagem_{i}.png")

            print("Mensagem gemini\n\n",slogans)

            return slogans[:4]

            
        except:
            print("Erro gemini------\n\n",e)
            
            slogans = ['Slogan 1 é na bump',
                    'Slogan 2 é na bump_media',
                    'Slogan 3 é na media',
                    'Slogan 4 é na bump media',
                    'Slogan 5 é na media_bump']
            
            for i, slogan in enumerate(slogans, start=1):
                criar_imagem_slogan(slogan, brand_name, f"slogan_imagem_{i}.png")

            return slogans[:4]

# Função para gerar dados em tempo real usando a OpenAI
def gerar_dados_em_tempo_real(localizacao):
    regex_patterns = [
        r"\d+\.\s*(.*)",
        r"\d+\.\s*([^\d\n]+)(?=\n\d+|\n\n|$)",
        r"\d+\.\s*([^\d]+)"
    ]
    
    
    prompt = (
        f"Baseado na localização '{localizacao}', forneça:\n"
        "1. Clima atual\n"
        "2. Hashtags de tendências\n"
        "3. Um evento local relevante\n"
        "4. Um tópico popular de cultura pop atual.\n"
        "Retorne algo similar a esse formato: 1. Ensolarado / 2. #rock&rio #sextou / 3. Festa de são joão / 4. Novo albúm da Taylor Swift"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role":"system", "content": "Você está puxando informações baseado no nome de estado"},
                {"role":"user", "content": prompt}
            ]
        )
        resposta = str(response['choices'][0]['message']['content'])
        print("Resposta do CLIMA GPT")
        
        dados = regex_info(resposta, regex_patterns)
        
        conjunto_add_info = {
            "weather": dados[0] if len(dados) > 0 else "Não disponível",
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
        real_time_data = None
        if request.method == 'POST':
            tema = request.form.get('tema')
            localizacao = request.form.get('localizacao')
            real_time_data = gerar_dados_em_tempo_real(localizacao)
            slogans = gerar_slogans(localizacao, tema, "Corona")
            imagens = [f"slogan_imagem_{i}.png" for i in range(1, len(slogans) + 1)]
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('corona.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('corona.html')
    else:
        return redirect(url_for('login'))

# Rota para a página exclusiva da Lacta
@app.route('/lacta', methods=['GET', 'POST'])
def lacta():
    if 'username' in session and session['brand_name'] == 'Lacta':
        real_time_data = None

        if request.method == 'POST':
            tema = request.form.get('tema')
            localizacao = request.form.get('localizacao')
            real_time_data = gerar_dados_em_tempo_real(localizacao)
            slogans = gerar_slogans(localizacao, tema, "Lacta")
            imagens = [f"slogan_imagem_{i}.png" for i in range(1, len(slogans) + 1)]
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('lacta.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('lacta.html', real_time_data=real_time_data)
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
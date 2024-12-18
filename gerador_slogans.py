from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from datetime import datetime
from time import sleep
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

AVALIACOES_PATH = 'avaliacoes.json'

def carregar_avaliacoes():
    if os.path.exists(AVALIACOES_PATH):
        with open(AVALIACOES_PATH, 'r') as file:
            return json.load(file)
    return {}

def salvar_avaliacoes(avaliacoes):
    with open(AVALIACOES_PATH, 'w') as file:
        json.dump(avaliacoes, file, indent=4)

def ultimos_slogan():    
    diretorio = f'{os.path.dirname(os.path.abspath(__file__))}/static/'
    
    arquivos_png = [arquivo for arquivo in os.listdir(diretorio) if arquivo.endswith('.png')]
    
    print("LISTA DE ARQUIVOS ATÉ O MOMENTO\n\n", arquivos_png)
    print("\n\nreturn: ",arquivos_png[-4:])
    
    return arquivos_png[-4:]

    

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
def criar_imagem_slogan(slogan_texto, brand_name):
    dtnow = datetime.now()
    output_filename = f"slogan_imagem{dtnow.strftime('%Y%m%d%H%M%S')}{str(dtnow.microsecond)[:2].zfill(2)}.png"
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
    sleep(0.05)
    return output_filename
    #print(f"Imagem salva em {output_path}")

# Função para gerar slogans usando a OpenAI
def gerar_slogans(estado, cidade, bairro, data_campanha, momento, brand_name):
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
        imgs = []
        for i, slogan in enumerate(slogans, start=1):
            file_img = criar_imagem_slogan(slogan, brand_name)
            imgs.append(file_img)
            
        print("Mensagem GPT\n\n",slogans)

        return slogans[:4], imgs
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
            imgs = []
            for i, slogan in enumerate(slogans, start=1):
                file_img = criar_imagem_slogan(slogan, brand_name)
                imgs.append(file_img)

            print("Mensagem GPT\n\n",slogans)

            return slogans[:4], imgs

            
        except:
            print("Erro gemini------\n\n",e)
            
            slogans = ['Slogan 1 é na bump',
                    'Slogan 2 é na bump_media',
                    'Slogan 3 é na media',
                    'Slogan 4 é na bump media',
                    'Slogan 5 é na media_bump']
            
            imgs = []
            for i, slogan in enumerate(slogans, start=1):
                file_img = criar_imagem_slogan(slogan, brand_name)
                imgs.append(file_img)

            return slogans[:4], imgs

# Função para gerar dados em tempo real usando a OpenAI
def gerar_dados_em_tempo_real(estado, cidade, bairro):
    regex_patterns = [
        r"\d+\.\s*(.*)",
        r"\d+\.\s*([^\d\n]+)(?=\n\d+|\n\n|$)",
        r"\d+\.\s*([^\d]+)"
    ]
    
    
    prompt = (
        f"Baseado na localização '{estado, cidade, bairro}', forneça:\n"
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
            momento = request.form.getlist('time_range')
            data_campanha= request.form.get('data_campanha')
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro)
            slogans, imagens = gerar_slogans(estado, cidade, bairro, data_campanha, momento, session['brand_name'])
            #imagens = ultimos_slogan()
            slogans_imagens = list(zip(slogans, imagens))
            print(slogans, '\n\n', imagens)
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
            momento = request.form.getlist('time_range')
            data_campanha= request.form.get('data_campanha')
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro)
            slogans, imagens = gerar_slogans(estado, cidade, bairro, data_campanha, momento, session['brand_name'])
            #imagens = ultimos_slogan()
            slogans_imagens = list(zip(slogans, imagens))
            print(slogans, '\n\n', imagens)
            return render_template('lacta.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('lacta.html')
    else:
        return redirect(url_for('login'))


@app.route('/avaliar_slogan', methods=['POST'])
def avaliar_slogan():
    # Obter a imagem e a avaliação (like/dislike)
    imagem = request.form['slogan_image']
    avaliacao = request.form['avaliacao']
    user = session.get('username', 'anon')

    # Carregar avaliações anteriores
    avaliacoes = carregar_avaliacoes()

    # Se o usuário não tiver um registro ainda, criar
    if user not in avaliacoes:
        avaliacoes[user] = {"like": [], "dislike": []}

    # Registrar a avaliação
    if avaliacao == 'like':
        if imagem not in avaliacoes[user]['like']:
            avaliacoes[user]['like'].append(imagem)
        # Remover da lista de dislikes, se existir
        if imagem in avaliacoes[user]['dislike']:
            avaliacoes[user]['dislike'].remove(imagem)
    elif avaliacao == 'dislike':
        if imagem not in avaliacoes[user]['dislike']:
            avaliacoes[user]['dislike'].append(imagem)
        # Remover da lista de likes, se existir
        if imagem in avaliacoes[user]['like']:
            avaliacoes[user]['like'].remove(imagem)

    # Salvar as avaliações no arquivo JSON
    salvar_avaliacoes(avaliacoes)

    return "Ok"  # Redireciona para a página inicial ou outra



@app.route('/avaliados', methods=['POST'])
def avaliados():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    avaliacoes = carregar_avaliacoes()
    
    # Obter a marca do usuário logado
    marca = session.get('brand_name', 'anon')

    # Passar apenas as avaliações da marca correspondente
    if marca == 'Corona':
        avaliacao_usuario = avaliacoes.get('corona', {'like': [], 'dislike': []})
    elif marca == 'Lacta':
        avaliacao_usuario = avaliacoes.get('lacta', {'like': [], 'dislike': []})
    else:
        avaliacao_usuario = {'like': [], 'dislike': []}

    # Exibir na página web as imagens de "like" e "dislike" para a marca do usuário
    return render_template('slogans_salvos.html', avaliacoes=avaliacao_usuario)

    return render_template('slogans_salvos.html', avaliacoes=avaliacoes)


if __name__ == '__main__':
    app.run(debug=True)

    #ngrok http 5000
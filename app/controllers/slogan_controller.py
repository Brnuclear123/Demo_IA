from flask import redirect, url_for, request, session, render_template, jsonify
from app.services.brands.corona import gerar_slogans_corona
from app.services.brands.lacta import  gerar_slogans_lacta
from app.services.brands.bauducco import gerar_slogans_bauducco
from app.services.slogan_service import gerar_dados_em_tempo_real, carregar_avaliacoes, salvar_avaliacoes, criar_gif_slogan_combinado


def corona():
    if 'username' in session and session['brand_name'] == 'Corona':
        real_time_data = None
        if request.method == 'POST':
            momento = request.form.getlist('time_range')
            data_campanha = request.form.get('data_campanha')
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha)
            slogans, imagens = gerar_slogans_corona(estado, cidade, bairro, data_campanha, momento, real_time_data)
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('corona.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('corona.html')
    else:
        return redirect(url_for('routes.login'))

def lacta():
    if 'username' in session and session['brand_name'] == 'Lacta':
        real_time_data = None
        if request.method == 'POST':
            momento = request.form.getlist('time_range')
            data_campanha = request.form.get('data_campanha')
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha)
            slogans, imagens = gerar_slogans_lacta(estado, cidade, bairro, data_campanha, momento, real_time_data)
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('lacta.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('lacta.html')
    else:
        return redirect(url_for('routes.login'))

def bauducco():
    if 'username' in session and session['brand_name'] == 'Bauducco':
        real_time_data = None
        if request.method == 'POST':
            momento = request.form.getlist('time_range')
            data_campanha = request.form.get('data_campanha')
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha)
            slogans, imagens = gerar_slogans_bauducco(estado, cidade, bairro, data_campanha, momento, real_time_data)
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('bauducco.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('bauducco.html')
    else:
        return redirect(url_for('routes.login'))

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


def avaliados():
    if 'username' not in session:
        return redirect(url_for('routes.login'))
    
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

def editar_slogan():
    data = request.get_json()
    video_path = data.get('video_path')
    novo_slogan = data.get('novo_slogan')
    brand_name = "Corona"  # ou recuperar dinamicamente se necessário

    try:
        # Gere o novo vídeo com base no novo slogan
        novo_video_path = criar_gif_slogan_combinado(novo_slogan, brand_name)
        # Se houver necessidade, atualize o registro do slogan no banco de dados ou arquivo
        
        return jsonify({
            'status': 'success',
            'novo_video_path': novo_video_path
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

#slogan_controller checado 
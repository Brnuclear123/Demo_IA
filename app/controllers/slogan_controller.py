from flask import redirect, url_for, request, session, render_template
from app.services.slogan_service import gerar_slogans_e_gifs, gerar_dados_em_tempo_real, carregar_avaliacoes, salvar_avaliacoes

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
            slogans, imagens = gerar_slogans_e_gifs(estado, cidade, bairro, data_campanha, momento, session['brand_name'], real_time_data)
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('corona.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('corona.html')
    else:
        return redirect(url_for('login'))

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
            slogans, imagens = gerar_slogans_e_gifs(estado, cidade, bairro, data_campanha, momento, session['brand_name'])
            slogans_imagens = list(zip(slogans, imagens))
            return render_template('lacta.html', slogans_imagens=slogans_imagens, real_time_date=real_time_data)
        return render_template('lacta.html')
    else:
        return redirect(url_for('login'))
    
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


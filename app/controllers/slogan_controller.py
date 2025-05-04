from flask import redirect, url_for, request, session, render_template, jsonify
from app.services.feriado_service import verificar_feriado
from app.services.brands.corona import gerar_slogans_corona
from app.services.brands.lacta import  gerar_slogans_lacta
from app.services.brands.bauducco import gerar_slogans_bauducco
from app.services.slogan_service import gerar_dados_em_tempo_real, carregar_avaliacoes, salvar_avaliacoes, criar_gif_slogan_combinado

from app.services.utils.slogan_static_generator import SloganStaticGenerator

from app.services.feriado_service import verificar_feriado

def corona():
    if 'username' in session and session['brand_name'].lower() == 'corona':
        real_time_data = None
        if request.method == 'POST':
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            momento = request.form.getlist('time_range')
            dia_da_semana = request.form.getlist('target_days')
            real_time_cards = request.form.getlist('data_cards')
            data_campanha = '06/05/2025 to 07/05/2025'

            # ✅ Verifica se há feriado
            feriado = verificar_feriado(data_campanha)
            usar_feriado = request.form.get("usar_feriado")

            # ✅ Gera dados em tempo real e os slogans
            #real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha)
            
            slogans, imagens = gerar_slogans_corona(
                estado, cidade, bairro, data_campanha, momento, real_time_cards, dia_da_semana, usar_feriado
            )

            slogans_imagens = list(zip(slogans, imagens))

            return render_template(
                'corona.html',
                slogans_imagens=slogans_imagens,
                real_time_date=real_time_data,
                feriado=feriado
            )

        return render_template('corona.html', feriado=None)
    else:
        return redirect(url_for('routes.login'))


def lacta():
    if 'username' in session and session['brand_name'].lower() == 'lacta':
        real_time_data = None
        if request.method == 'POST':
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            momento = request.form.getlist('time_range')
            dia_da_semana = request.form.getlist('target_days')
            real_time_cards = request.form.getlist('data_cards')
            data_campanha = '06/05/2025 to 07/05/2025'

            # ✅ Verifica se há feriado
            feriado = verificar_feriado(data_campanha)
            usar_feriado = request.form.get("usar_feriado")

            # ✅ Gera dados em tempo real e os slogans
            #real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha)
            
            slogans, imagens = gerar_slogans_lacta(
                estado, cidade, bairro, data_campanha, momento, real_time_cards, dia_da_semana, usar_feriado
            )

            slogans_imagens = list(zip(slogans, imagens))

            return render_template(
                'lacta.html',
                slogans_imagens=slogans_imagens,
                real_time_date=real_time_data,
                feriado=feriado
            )

        # GET (inicial)
        return render_template('lacta.html', feriado=None)
    else:
        return redirect(url_for('routes.login'))


from app.services.feriado_service import verificar_feriado

def bauducco():
    if 'username' in session and session['brand_name'].lower() == 'bauducco':
        real_time_data = None
        if request.method == 'POST':
            estado = request.form.get('estado')
            cidade = request.form.get('cidade')
            bairro = request.form.get('bairro')
            momento = request.form.getlist('time_range')
            dia_da_semana = request.form.getlist('target_days')
            real_time_cards = request.form.getlist('data_cards')
            data_campanha = '06/05/2025 to 07/05/2025'

            # ✅ Verifica se há feriado
            feriado = verificar_feriado(data_campanha)
            usar_feriado = request.form.get("usar_feriado")

            # ✅ Gera dados em tempo real e os slogans
            #real_time_data = gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha)
            
            slogans, imagens = gerar_slogans_bauducco(
                estado, cidade, bairro, data_campanha, momento, real_time_cards, dia_da_semana, usar_feriado
            )

            slogans_imagens = list(zip(slogans, imagens))

            return render_template(
                'bauducco.html',
                slogans_imagens=slogans_imagens,
                real_time_date=real_time_data,
                feriado=feriado
            )

        return render_template('bauducco.html', feriado=None)
    else:
        return redirect(url_for('routes.login'))


def avaliar_slogan():
    imagem = request.form['slogan_image']
    avaliacao = request.form['avaliacao']   # 'like' ou 'dislike'
    user = session.get('username', 'anon')

    avaliacoes = carregar_avaliacoes()
    avaliacoes.setdefault(user, {"like": [], "dislike": []})

    likes = avaliacoes[user]['like']
    dislikes = avaliacoes[user]['dislike']

    if avaliacao == 'like':
        if imagem in likes:
            # se já estava no like, tira (toggle off)
            likes.remove(imagem)
        else:
            # adiciona no like e garante que não fique no dislike
            likes.append(imagem)
            if imagem in dislikes:
                dislikes.remove(imagem)

    else:  # avaliacao == 'dislike'
        if imagem in dislikes:
            dislikes.remove(imagem)
        else:
            dislikes.append(imagem)
            if imagem in likes:
                likes.remove(imagem)

    salvar_avaliacoes(avaliacoes)

    # opcional: devolver status e as listas para o front atualizar UI
    return jsonify({
        'status':  'success',
        'message': 'Avaliação atualizada',
        'likes':    likes,
        'dislikes': dislikes
    })


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
    elif marca == 'Bauducco':
        avaliacao_usuario = avaliacoes.get('bauducco', {'like': [], 'dislike': []})
    else:
        avaliacao_usuario = {'like': [], 'dislike': []}

    # Exibir na página web as imagens de "like" e "dislike" para a marca do usuário
    return render_template('slogans_salvos.html', avaliacoes=avaliacao_usuario)

    return render_template('slogans_salvos.html', avaliacoes=avaliacoes)

def editar_slogan():
    data = request.get_json()
    video_path = data.get('video_path')
    novo_slogan = data.get('novo_slogan')
    brand_name = session.get('brand_name', 'anon')  # ou recuperar dinamicamente se necessário

    try:
        # Gere o novo vídeo com base no novo slogan
        generator = SloganStaticGenerator(brand_name)
        novo_image_path = generator.generate_static_image(novo_slogan)
        print(novo_image_path)
        #novo_video_path = criar_gif_slogan_combinado(novo_slogan, brand_name)
        # Se houver necessidade, atualize o registro do slogan no banco de dados ou arquivo
        
        return jsonify({
            'status': 'success',
            'novo_image_path': novo_image_path
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

#slogan_controller checado 
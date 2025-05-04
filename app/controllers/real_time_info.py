from flask import redirect, url_for, request, jsonify
from app.services.slogan_service import gerar_dados_em_tempo_real

def real_time_data():
    # Captura parâmetros da query string
    estado       = request.args.get('estado', '')
    cidade       = request.args.get('cidade', '')
    bairro       = request.args.get('bairro', '')
    data_campanha= "06/05/2025 to 07/05/2025"#request.args.get('data_campanha', '')
    # Gera os dados em tempo real
    real = gerar_dados_em_tempo_real(estado, cidade, bairro, data_campanha)
    # Retorna apenas o clima (ou todo o JSON, se desejar)
    return jsonify({ 'weather': real.get('weather', 'Não disponível') })

#real_time_checado
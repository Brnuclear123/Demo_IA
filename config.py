import os

class Config:
    # Configurações gerais
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')  # Chave secreta para segurança da sessão
    DEBUG = False

    # Caminhos e arquivos usados no projeto
    BEARER_TOKEN = os.getenv('BEARER_TOKEN', 'eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NDIxNTk1OTUsInRpbWVzdGFtcCI6MTc0MjE1NTk5NTg4N30.DGSalk0JOsbgkoit3BzWAijNcToW_wPb8dl1gd-h3fk')
    WEATHER_JSON = os.getenv('WEATHER_JSON', 'static/data/weather-cd.json')
    AVALIACOES_PATH = os.getenv('AVALIACOES_PATH', 'static/data/avaliacoes.json')
    FONT_PATH = os.getenv('FONT_PATH', 'static/fonte/Bison-Bold(PersonalUse).ttf')
    FUNDO_IMAGEM_PATH = os.getenv('FUNDO_IMAGEM_PATH', 'static/frames/meu_fundo.png')
    ENVIROMENT_DATA = os.getenv('ENVIROMENT_DATA', 'static/data/env_variables.json')

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

# Um dicionário para facilmente selecionar as configurações com base no ambiente
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

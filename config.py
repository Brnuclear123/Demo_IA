import os

class Config:
    # Configurações gerais
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')
    DEBUG = False
    BEARER_TOKEN = os.getenv('BEARER_TOKEN', 'your_token_here')
    
    # Configurações por marca
    
    FONT_PATH = {'lacta': 'static/brands/lacta/fonts/CircularStd-Bold.otf', 
                 'bauducco': 'static/brands/bauducco/fonts/Decoy-Black.otf',
                 'corona': 'static/brands/corona/fonts/Bison-Bold.ttf'}
    
    LOGOS_PATH = {'lacta': 'static/brands/lacta/logos/',
                 'bauducco': 'static/brands/bauducco/logos/',
                 'corona': 'static/brands/corona/logos/'}
    
    VIDEOS_PATH = {'lacta': 'static/brands/lacta/videos/',
                 'bauducco': 'static/brands/bauducco/videos/',
                 'corona': 'static/brands/corona/videos/'}
    
    FUNDO_IMAGEM_PATH = {'lacta': 'static/brands/lacta/frames/fundo_lct.jpeg',
                 'bauducco': 'static/brands/bauducco/frames/fundo_bdc.jpeg',
                 'corona': 'static/brands/corona/frames/fundo_crn.jpeg'}
    
    IMAGEM_FINAL_PATH = {'lacta': 'static/brands/lacta/frames/baseplate_lct.jpeg',
                 'bauducco': 'static/brands/bauducco/frames/baseplate_bdc.jpeg',
                 'corona': 'static/brands/corona/frames/baseplate_crn.jpeg'}

    BOTTOM_IMAGEM_PATH = {'lacta': 'static/brands/lacta/bottom/bottom_lct.jpeg',
                 'bauducco': 'static/brands/bauducco/bottom/bottom_bdc.jpeg',
                 'corona': 'static/brands/corona/bottom/bottom_crn.png'}
    
    # Arquivos compartilhados
    WEATHER_JSON = 'static/data/weather-cd.json'
    AVALIACOES_PATH = 'static/data/avaliacoes.json'
    ENVIROMENT_DATA = 'static/data/env_variables.json'

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
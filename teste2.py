
import os
from datetime import datetime


dtnow = datetime.now()
output_filename = f"slogan_imagem{dtnow.strftime('%Y%m%d%H%M%S')}{str(dtnow.microsecond)[:2]}.png"
print(datetime.now(),'\n',output_filename,'\n\n')

# Defina o diretório que deseja pesquisar
diretorio = f'{os.path.dirname(os.path.abspath(__file__))}/static/'

# Listar todos os arquivos .png no diretório
arquivos_png = [arquivo for arquivo in os.listdir(diretorio) if arquivo.endswith('.png')]

# Exibir os arquivos .png encontrados
print("Arquivos .png encontrados:")
for arquivo in arquivos_png:
    print(arquivo)

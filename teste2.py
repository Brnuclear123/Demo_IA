from dotenv import load_dotenv
import os

# Carregar o .env
load_dotenv()

# Obter a chave da API
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
if api_key:
    print(f"A chave foi carregada com sucesso: {api_key[:5]}...")  # Imprime os primeiros caracteres para verificar
else:
    print("Erro: A chave não foi encontrada no arquivo .env")

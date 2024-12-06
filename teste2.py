import openai

openai.api_key = ""

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Ou "gpt-4"
    messages=[
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Crie um slogan para uma empresa de tecnologia."}
    ],
    max_tokens=50
)

# Resultado
print(response['choices'][0]['message']['content'].strip())

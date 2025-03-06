from flask import Flask
from app.routes import routes
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])  # Use 'production' para produção

# Registrar as rotas
app.register_blueprint(routes)

if __name__ == '__main__':
    app.run(debug=True)

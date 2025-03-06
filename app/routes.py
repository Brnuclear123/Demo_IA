from flask import Blueprint
from app.controllers.auth_controller import login, logout, index
from app.controllers.slogan_controller import corona, lacta, avaliar_slogan, avaliados

routes = Blueprint('routes', __name__)

routes.add_url_rule('/', 'login_redirect', index)
routes.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
routes.add_url_rule('/logout', 'logout', logout)
routes.add_url_rule('/corona', 'corona', corona, methods=['GET', 'POST'])
routes.add_url_rule('/lacta', 'lacta', lacta, methods=['GET', 'POST'])
routes.add_url_rule('/avaliar_slogan', 'avaliar_slogan', avaliar_slogan, methods=['GET', 'POST'])
routes.add_url_rule('/avaliados', 'avaliados', avaliados, methods=['GET', 'POST'])

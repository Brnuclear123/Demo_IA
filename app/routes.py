from flask import Blueprint
from app.controllers.auth_controller import login, logout, index
from app.controllers.slogan_controller import corona, lacta, bauducco, avaliar_slogan, avaliados, editar_slogan
from app.controllers.zkong_controller import publish_content
from app.controllers.real_time_info import real_time_data

routes = Blueprint('routes', __name__)

routes.add_url_rule('/', 'login_redirect', index)
routes.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
routes.add_url_rule('/logout', 'logout', logout)
routes.add_url_rule('/corona', 'corona', corona, methods=['GET', 'POST'])
routes.add_url_rule('/lacta', 'lacta', lacta, methods=['GET', 'POST'])
routes.add_url_rule('/bauducco', 'bauducco', bauducco, methods=['GET', 'POST'])
routes.add_url_rule('/avaliar_slogan', 'avaliar_slogan', avaliar_slogan, methods=['GET', 'POST'])
routes.add_url_rule('/avaliados', 'avaliados', avaliados, methods=['GET', 'POST'])
routes.add_url_rule('/publish-content', 'publish-content', publish_content, methods=['POST'])
routes.add_url_rule('/editar_slogan', 'editar_slogan', editar_slogan, methods=['POST'])
routes.add_url_rule('/real_time_data', 'real_time_data', real_time_data, methods=['GET'])
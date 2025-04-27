from flask import session, redirect, url_for, request, render_template
from werkzeug.security import check_password_hash
from app.models.user import users

def index():
    return redirect(url_for('routes.login'))

def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['brand_name'] = user['brand']
            
            # Redireciona com base na marca do usuário
            if user['brand'] == 'Corona':
                return redirect(url_for('routes.corona'))
            elif user['brand'] == 'Lacta':
                return redirect(url_for('routes.lacta'))
            elif user['brand'] == 'Bauducco':
                return redirect(url_for('routes.bauducco'))
        else:
            error = "Login falhou. Verifique suas credenciais."
    
    return render_template('login.html', error=error)

def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

from werkzeug.security import generate_password_hash

users = {
    'corona': {'password': generate_password_hash('1234'), 'brand': 'Corona'},
    'lacta': {'password': generate_password_hash('1234'), 'brand': 'Lacta'},
    'bauducco': {'password': generate_password_hash('1234'), 'brand': 'Bauducco'}
}

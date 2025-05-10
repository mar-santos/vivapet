from app import create_app

app = create_app()

with app.app_context():  # Importante garantir o contexto!
    for rule in app.url_map.iter_rules():
        print(rule)
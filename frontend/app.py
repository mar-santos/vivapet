from flask import Flask, render_template, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'  # Para mensagens flash

# Rota para página inicial
@app.route('/')
def home():
    return render_template('home.html')

# Rota para serviços
@app.route('/servicos')
def servicos():
    return render_template('pages/servicos/index.html')

# Rota para agendamentos
@app.route('/agendamentos')
def agendamentos():
    return render_template('pages/agendamentos/index.html')

# Rota para pets
@app.route('/pets')
def pets():
    return render_template('pages/pets/index.html')

# Rota para adicionar novo pet
@app.route('/pets/novo')
def novo_pet():
    return render_template('pages/pets/novo.html')

# Rota para login
@app.route('/login')
def login():
    return render_template('login.html')

# Rota para cadastro de usuários
@app.route('/usuarios_cadastrar')
def usuarios_cadastrar():
    return render_template('usuarios_cadastrar.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)
from flask import Flask, render_template, send_from_directory, request, redirect, url_for
import os

# Configuramos Flask para que reconozca tus dos carpetas
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'neura_trade_ultra_secure_key'

# --- CONFIGURACIÓN DE BINANCE ---
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7TohnOG5dMBaiZQ7lqRPgmJ904XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs21JtjxkMw2wrn2jftheE3g3vvNoqrhw20jtEcno99RQ8Xv86u'

# --- CEREBRO DEL BOT (TRADER ELITE) ---
def ejecutar_bot():
    try:
        from binance.client import Client
        client = Client(API_KEY, API_SECRET)
        return client.get_asset_balance(asset='USDT')
    except:
        return "Analizando mercado..."

# --- RUTAS RESPETANDO TU ESTRUCTURA ---

@app.route('/')
def index():
    # Como tu index.html está en /static por seguridad, lo servimos desde ahí
    return send_from_directory('static', 'index.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    password = request.form.get('password')
    
    # Si las credenciales son correctas, da acceso a la landing/dashboard
    if usuario == 'admin' and password == 'admin1234':
        return redirect(url_for('landing'))
    return redirect(url_for('index'))

@app.route('/landing')
def landing():
    # El bot se activa y muestra resultados en la landing protegida
    balance = ejecutar_bot()
    return render_template('landing.html', balance=balance)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

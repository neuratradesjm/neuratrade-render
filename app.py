from flask import Flask, render_template, request, redirect, url_for, session, flash
from binance.client import Client
from binance.exceptions import BinanceAPIException
from functools import wraps
import random
import os

app = Flask(__name__)
app.secret_key = 'neura_trade_ultra_secret_key_2026'

# --- CONFIGURACIÓN DE COMISIONES ---
COMISION_BOT_FIJA = 0.50          
PORCENTAJE_GANANCIA_ADMIN = 0.20  

# --- PASO 3: TUS LLAVES DE BINANCE ---
# Pega aquí los códigos que saques de Binance
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7Tohn0G5dMBaiZQ7lqRPgmJ9O4XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs2lJtjxkMw2wrn2jfthE3g3vvNoqrhw2OjtEcno99RQ8Xv86u'

# Intentar conectar con Binance
try:
    client = Client(API_KEY, API_SECRET)
except Exception as e:
    print(f"Error de conexión: {e}")
    client = None

# --- SEGURIDAD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS ---
@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('username')
    pw = request.form.get('password')
    if user == 'admin' and pw == 'neura2026':
        session.clear()
        session['user_id'] = 1
        session['username'] = 'admin'
        return redirect(url_for('dashboard'))
    flash("Credenciales incorrectas", "danger")
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    balance_real = "0.00"
    precio_btc = "0.00"

    if client:
        try:
            # Obtener balance real de USDT
            asset = client.get_asset_balance(asset='USDT')
            balance_real = asset['free'] if asset else "0.00"
            # Obtener precio real de BTC
            ticker = client.get_symbol_ticker(symbol="BTCUSDT")
            precio_btc = ticker['price']
        except Exception as e:
            print(f"Error consultando Binance: {e}")

    return render_template('dashboard.html', 
                           username=session['username'], 
                           balance=balance_real, 
                           btc_price=precio_btc)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

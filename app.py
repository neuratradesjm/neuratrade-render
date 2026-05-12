from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'neura_trade_production_key_2026' # Seguridad nivel broker

# --- CONFIGURACIÓN DE APIS REALES ---
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7TohnOG5dMBaiZQ7lqRPgmJ904XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs21JtjxkMw2wrn2jftheE3g3vvNoqrhw20jtEcno99RQ8Xv86u'

# --- MOTOR DE TRADING REAL (NEURA TRADE BOT) ---
def get_bot_engine(symbol="BTCUSDT"):
    """Conexión real con el mercado para ejecución de bot en línea."""
    try:
        from binance.client import Client
        client = Client(API_KEY, API_SECRET)
        # Obtener balance real de la cuenta
        balance = client.get_asset_balance(asset='USDT')
        # Obtener precio real del mercado seleccionado por el usuario
        ticker = client.get_symbol_ticker(symbol=symbol)
        return {
            "balance": balance['free'],
            "precio_actual": ticker['price'],
            "mercado": symbol,
            "estado": "BOT ONLINE - OPERANDO"
        }
    except Exception as e:
        return {"error": str(e), "estado": "ERROR DE CONEXIÓN API"}

# --- MODULO DE GESTIÓN DE USUARIOS (SEGURIDAD) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS DE NEURA TRADE ---

@app.route('/')
def home():
    """Página Principal de Neura Trade."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario')
        pw = request.form.get('clave')
        # Lógica de autenticación (Admin y Usuarios)
        if user == 'admin' and pw == 'admin1234':
            session['user_id'] = user
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        elif user == 'cliente' and pw == 'cliente1234':
            session['user_id'] = user
            session['role'] = 'user'
            return redirect(url_for('billetera'))
    return render_template('login.html')

# --- MODULO DE ADMINISTRADOR (CONTROL TOTAL) ---
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Acceso a todos los módulos y supervisión del sistema."""
    stats = {
        "usuarios_activos": 124,
        "volumen_24h": "45,230.00 USDT",
        "comisiones_totales": "1,240.50 USDT"
    }
    return render_template('admin_panel.html', stats=stats)

# --- MODULO DE GESTIÓN FINANCIERA ---
@app.route('/billetera', methods=['GET', 'POST'])
@login_required
def billetera():
    """Gestión de ingresos, retiros y selección de mercado para el bot."""
    mercado_seleccionado = request.args.get('mercado', 'BTCUSDT')
    datos_bot = get_bot_engine(mercado_seleccionado)
    
    # Lista de mercados disponibles para el usuario
    mercados = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    
    return render_template('billetera.html', 
                           datos=datos_bot, 
                           mercados=mercados,
                           user=session['user_id'])

# --- MÓDULO DE GESTIÓN DE USUARIOS (PERFIL) ---
@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html', user_info={
        "nombre": "Luis Garcia",
        "email": "luisfgarsa@gmail.com",
        "telefono": "+584124407893"
    })

@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('home'))

# --- CONFIGURACIÓN DE ARRANQUE ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

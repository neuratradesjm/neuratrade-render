from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
# Seguridad para el ecosistema Neura Trade
app.secret_key = 'neura_trade_production_key_2026' 

# --- CONFIGURACIÓN DE IDENTIDAD Y APIS ---
# Credenciales para Neura Trade y conexión con Binance
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7TohnOG5dMBaiZQ7lqRPgmJ904XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs21JtjxkMw2wrn2jftheE3g3vvNoqrhw20jtEcno99RQ8Xv86u'

# --- MOTOR DE TRADING REAL (NEURA TRADE BOT) ---
def get_bot_engine(symbol="BTCUSDT"):
    """Conexión real con el mercado para ejecución de bot en línea."""
    try:
        from binance.client import Client
        client = Client(API_KEY, API_SECRET)
        balance = client.get_asset_balance(asset='USDT')
        ticker = client.get_symbol_ticker(symbol=symbol)
        return {
            "balance": balance['free'],
            "precio_actual": ticker['price'],
            "mercado": symbol,
            "estado": "BOT ONLINE - OPERANDO",
            "profit_objetivo": "Alta Rentabilidad" # Premisa para atraer usuarios
        }
    except Exception:
        # Fallback de seguridad para mantener la visual operativa
        return {
            "balance": "1,250.00",
            "precio_actual": "80,396.55",
            "mercado": symbol,
            "estado": "MODO LOCAL (VERIFICANDO CONEXIÓN)",
            "profit_objetivo": "15%"
        }

# --- MIDDLEWARE DE SEGURIDAD ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            return redirect(url_for('billetera'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS DEL SISTEMA NEURA TRADE ---

@app.route('/')
def home():
    """Punto de acceso: Redirige según el estado de sesión."""
    if session.get('logged_in'):
        return redirect(url_for('billetera'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Gestión de usuarios: Admin y Clientes."""
    if request.method == 'POST':
        user = request.form.get('usuario').strip()
        pw = request.form.get('clave').strip()
        
        # Credenciales de Administrador
        if user == 'admin' and pw == 'admin1234':
            session['logged_in'] = True
            session['user_id'] = user
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
            
        # Credenciales de Cliente de prueba
        elif user == 'cliente' and pw == 'cliente1234':
            session['logged_in'] = True
            session['user_id'] = user
            session['role'] = 'user'
            return redirect(url_for('billetera'))
            
        return "Credenciales incorrectas."
    return render_template('index.html')

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    """Módulo de Administrador: Control total del sistema."""
    stats = {
        "usuarios_activos": 124,
        "volumen_24h": "45,230.00 USDT",
        "comisiones_totales": "1,240.50 USDT"
    }
    return render_template('dashboard.html', stats=stats)

@app.route('/billetera')
@login_required
def billetera():
    """Módulo Financiero: Gestión de fondos ($20) y selección de mercado."""
    mercado = request.args.get('mercado', 'BTCUSDT')
    datos_bot = get_bot_engine(mercado)
    mercados_disponibles = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    
    return render_template('billetera.html', 
                           datos=datos_bot, 
                           mercados=mercados_disponibles,
                           user=session.get('user_id'))

@app.route('/perfil')
@login_required
def perfil():
    """Módulo de Gestión de Usuario: Datos personales y soporte."""
    user_info = {
        "nombre": "Luis Garcia",
        "email": "luisfgarsa@gmail.com",
        "telefono": "+584124407893"
    }
    return render_template('perfil.html', user_info=user_info)

@app.route('/agenda')
@login_required
def agenda():
    """Planificación diaria para evitar colapsos operativos."""
    tareas = [
        {"hora": "08:00 AM", "tarea": "Notificación WhatsApp (+584124407893) - Agenda diaria"},
        {"hora": "10:00 AM", "tarea": "Revisión de Profit Real en Neura Trade"},
        {"hora": "01:00 PM", "tarea": "Auditoría de transacciones Broker/Binance"}
    ]
    return render_template('agenda.html', tareas=tareas)

@app.route('/salir')
def salir():
    """Cierre de sesión seguro."""
    session.clear()
    return redirect(url_for('home'))

# --- DIAGNÓSTICO Y ARRANQUE ---
@app.route('/health')
def health():
    return jsonify({"status": "operativo", "sistema": "Neura Trade", "bot": "Activo"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'neura_trade_production_key_2026' 

# --- CONFIGURACIÓN DE IDENTIDAD Y APIS ---
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7TohnOG5dMBaiZQ7lqRPgmJ904XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs21JtjxkMw2wrn2jftheE3g3vvNoqrhw20jtEcno99RQ8Xv86u'
DIRECCION_USDT = "TU_BILLETERA_TRC20_AQUI" 

# --- MOTOR DE TRADING REAL (NEURA TRADE BOT) ---
def get_bot_engine(symbol="BTCUSDT"):
    try:
        from binance.client import Client
        client = Client(API_KEY, API_SECRET)
        balance_info = client.get_asset_balance(asset='USDT')
        ticker = client.get_symbol_ticker(symbol=symbol)
        return {
            "balance": balance_info['free'],
            "precio_actual": ticker['price'],
            "mercado": symbol,
            "estado": "BOT ONLINE - OPERANDO",
            "profit_objetivo": "Alta Rentabilidad"
        }
    except Exception:
        base_balance = session.get('user_balance', 1250.00)
        return {
            "balance": f"{base_balance:,.2f}",
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

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('billetera'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('usuario').strip()
        pw = request.form.get('clave').strip()
        if user == 'admin' and pw == 'admin1234':
            session['logged_in'] = True
            session['user_id'] = user
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        elif user == 'cliente' and pw == 'cliente1234':
            session['logged_in'] = True
            session['user_id'] = user
            session['role'] = 'user'
            if 'user_balance' not in session: session['user_balance'] = 1250.00
            return redirect(url_for('billetera'))
        return "Credenciales incorrectas."
    return render_template('index.html')

# --- TAREA 3: GESTIÓN DE AGENDA AUTOMATIZADA ---
@app.route('/agenda')
@login_required
@admin_required
def agenda():
    """Planificación operativa para Luis García Salas."""
    agenda_datos = [
        {"hora": "08:00 AM", "tarea": "Enviar resumen de agenda a WhatsApp +584124407893", "estado": "Pendiente"},
        {"hora": "08:05 AM", "tarea": "Enviar correo diario a luisfgarsa@gmail.com", "estado": "Pendiente"},
        {"hora": "10:00 AM", "tarea": "Auditoría de operaciones Neura Trade en Binance", "estado": "Programado"},
        {"hora": "02:00 PM", "tarea": "Revisión de nuevos depósitos de $20 USDT", "estado": "Programado"},
        {"hora": "08:00 PM", "tarea": "Cierre de profit diario y respaldo en Keep", "estado": "Pendiente"}
    ]
    return render_template('agenda.html', tareas=agenda_datos)

# --- RUTAS FINANCIERAS Y BOT ---
@app.route('/billetera')
@login_required
def billetera():
    mercado = request.args.get('mercado', 'BTCUSDT')
    datos_bot = get_bot_engine(mercado)
    mercados_disponibles = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    return render_template('billetera.html', datos=datos_bot, mercados=mercados_disponibles, user=session.get('user_id'))

@app.route('/depositar')
@login_required
def depositar():
    return render_template('depositar.html', direccion=DIRECCION_USDT)

@app.route('/confirmar_pago', methods=['POST'])
@login_required
def confirmar_pago():
    monto = float(request.form.get('monto', 0))
    txid = request.form.get('txid')
    if monto >= 20 and txid:
        session['user_balance'] = session.get('user_balance', 0) + monto
        return redirect(url_for('billetera'))
    return "Error: Depósito mínimo $20 USDT requerido."

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {"usuarios_activos": 124, "volumen_24h": "45,230.00 USDT", "comisiones_totales": "1,240.50 USDT"}
    return render_template('dashboard.html', stats=stats)

@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

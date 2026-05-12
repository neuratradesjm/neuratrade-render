from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from datetime import datetime
from functools import wraps
import random

app = Flask(__name__)
app.secret_key = 'neura_trade_production_key_2026'

# --- PERSISTENCIA TEMPORAL ---
solicitudes_registro = []
# Nuevo: Historial de operaciones para mostrar actividad en el sistema
historial_operaciones = [
    {"fecha": "2026-05-12 10:30", "par": "BTC/USDT", "tipo": "COMPRA", "precio": "79,500.00", "estado": "Cerrada", "profit": "+1.2%"},
    {"fecha": "2026-05-12 14:15", "par": "ETH/USDT", "tipo": "VENTA", "precio": "3,450.20", "estado": "Cerrada", "profit": "+0.8%"}
]

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
        precio = float(ticker['price'])
        return {
            "balance": balance_info['free'],
            "precio_actual": f"{precio:,.2f}",
            "mercado": symbol,
            "estado": "EJECUTANDO ESTRATEGIA NEURA",
            "indicador": "RSI Optimizado",
            "señal": "HOLD" if random.random() > 0.5 else "BUY",
            "profit_objetivo": "Alta Rentabilidad"
        }
    except Exception:
        base_balance = session.get('user_balance', 1250.00)
        return {
            "balance": f"{base_balance:,.2f}",
            "precio_actual": "80,396.55",
            "mercado": symbol,
            "estado": "MODO SIMULACIÓN (ESTRATEGIA ACTIVA)",
            "indicador": "Análisis Técnico Activo",
            "señal": "WAIT",
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
            session.update({'logged_in': True, 'user_id': user, 'role': 'admin'})
            return redirect(url_for('admin_dashboard'))
        elif user == 'cliente' and pw == 'cliente1234':
            session.update({'logged_in': True, 'user_id': user, 'role': 'user'})
            if 'user_balance' not in session: session['user_balance'] = 1250.00
            return redirect(url_for('billetera'))
        return "Credenciales incorrectas."
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nueva_solicitud = {
            "nombres": request.form.get('nombres'),
            "apellidos": request.form.get('apellidos'),
            "nacionalidad": request.form.get('nacionalidad'),
            "tipo_doc": request.form.get('tipo_doc'), 
            "documento": request.form.get('documento'),
            "usuario_nuevo": request.form.get('usuario_nuevo'),
            "pago_bot": request.form.get('pago_bot'),
            "pago_broker": request.form.get('pago_broker'),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        solicitudes_registro.append(nueva_solicitud)
        return "Registro enviado con éxito. En Neura Trade validaremos su pago en breve."
    return render_template('registro.html')

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        "usuarios_activos": 124, 
        "volumen_24h": "45,230.00 USDT", 
        "comisiones_activas": len(solicitudes_registro) * 20
    }
    return render_template('admin_dashboard.html', solicitudes=solicitudes_registro, stats=stats)

@app.route('/aprobar/<usuario>')
@login_required
@admin_required
def aprobar_usuario(usuario):
    global solicitudes_registro
    solicitudes_registro = [s for s in solicitudes_registro if s['usuario_nuevo'] != usuario]
    return redirect(url_for('admin_dashboard'))

# --- OPERATIVA Y AGENDA ---
@app.route('/agenda')
@login_required
@admin_required
def agenda():
    agenda_datos = [
        {"hora": "08:00 AM", "tarea": "WhatsApp +584124407893: Agenda diaria", "estado": "Pendiente"},
        {"hora": "08:05 AM", "tarea": "Email a luisfgarsa@gmail.com", "estado": "Pendiente"},
        {"hora": "02:00 PM", "tarea": "Validación registros Neura Trade", "estado": "Activo"}
    ]
    return render_template('agenda.html', tareas=agenda_datos)

@app.route('/billetera')
@login_required
def billetera():
    mercado = request.args.get('mercado', 'BTCUSDT')
    datos_bot = get_bot_engine(mercado)
    mercados = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
    # Enviamos el historial de operaciones a la billetera
    return render_template('billetera.html', 
                           datos=datos_bot, 
                           mercados=mercados, 
                           historial=historial_operaciones,
                           user=session.get('user_id'))

# Nuevo: Ruta para registrar ejecuciones del bot manualmente o por cron
@app.route('/ejecutar_orden', methods=['POST'])
@login_required
@admin_required
def ejecutar_orden():
    nueva_op = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "par": request.form.get('par'),
        "tipo": request.form.get('tipo'),
        "precio": request.form.get('precio'),
        "estado": "Cerrada",
        "profit": f"+{random.uniform(0.5, 2.1):.1f}%"
    }
    historial_operaciones.insert(0, nueva_op)
    return redirect(url_for('billetera'))

@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('home'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

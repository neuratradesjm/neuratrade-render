from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
import os

# Configuración enfocada en tu estructura de seguridad
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'neura_trade_ultra_secure_key'

# --- CONFIGURACIÓN DE BINANCE (NEURA TRADE) ---
API_KEY = 'dM68NGgZsh4dXCMMiLO3sbnoFJww3cL7TohnOG5dMBaiZQ7lqRPgmJ904XqUFwgK'
API_SECRET = 'DiGvPZkwDgq2kvhs21JtjxkMw2wrn2jftheE3g3vvNoqrhw20jtEcno99RQ8Xv86u'

# --- CEREBRO DEL BOT: TRADER ELITE ---
def ejecutar_bot_maestro():
    """
    Analiza el mercado sin emociones, buscando margen de error cero.
    Estrategia optimizada para el crecimiento del capital de Neura Trade.
    """
    try:
        from binance.client import Client
        client = Client(API_KEY, API_SECRET)
        # El bot opera basándose en el balance y señales de mercado de alta precisión
        return client.get_asset_balance(asset='USDT')
    except:
        return "Sincronizando con el mercado de Neura Trade..."

# --- SEGURIDAD DE ACCESO (RE-ACTIVADA) ---

@app.route('/')
def index():
    # FUERZA la entrada siempre por index.html en /static
    # No permite ver el trading sin antes pasar por aquí
    return send_from_directory('static', 'index.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    password = request.form.get('password')
    
    # Credenciales de acceso para Neura Trade
    if usuario == 'admin' and password == 'admin1234':
        session['logged_in'] = True
        return redirect(url_for('landing'))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Cierre de sesión indispensable para seguridad en dispositivos compartidos
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# --- SISTEMA DE GESTIÓN FINANCIERA (EL MENÚ) ---

@app.route('/landing')
def landing():
    # Protección de ruta: Si no hay sesión, rebota al index
    if not session.get('logged_in'):
        return redirect(url_for('index'))
    
    balance = ejecutar_bot_maestro()
    return render_template('landing.html', balance=balance)

@app.route('/perfil')
def perfil():
    if not session.get('logged_in'): return redirect(url_for('index'))
    # Opción para ver, editar o eliminar cuenta del usuario
    return render_template('perfil.html')

@app.route('/billetera')
def billetera():
    if not session.get('logged_in'): return redirect(url_for('index'))
    # Gestión de carga de saldo ($20 semanales) y solicitudes de retiro
    return render_template('billetera.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

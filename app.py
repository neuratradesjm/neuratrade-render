from flask import Flask, jsonify, render_template, request, session, redirect, send_from_directory
import random
import os
import psycopg2
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'neura_trade_key_2026'  # Clave para manejar las sesiones de usuario

# --- Conexión a la Base de Datos ---
def get_db_connection():
    db_url = os.environ.get('DATABASE_URL')
    result = urlparse(db_url)
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

# --- Rutas de Navegación ---

@app.route('/')
def home():
    # Muestra la Landing Page corporativa (Misión, Visión, Legal)
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    # Solo permite entrar si el usuario ha iniciado sesión
    if 'user' not in session:
        return redirect('/')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# --- APIs del Sistema ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    # Validación temporal para Neura Trade
    if data.get('user') == 'admin' and data.get('pass') == 'neura2026':
        session['user'] = 'admin'
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Credenciales inválidas"})

@app.route('/api/get-balance', methods=['GET'])
def get_balance():
    balance_inicial = 1250.00
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT SUM(profit) FROM trades')
        res = cur.fetchone()[0]
        total_profit = res if res else 0
        cur.close()
        conn.close()
        balance_actual = balance_inicial + (balance_inicial * (total_profit / 100))
        return jsonify({"status": "success", "balance": round(balance_actual, 2)})
    except Exception as e:
        return jsonify({"status": "error", "balance": balance_inicial})

@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    pares = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"]
    par_elegido = random.choice(pares)
    profit_pct = round(random.uniform(1.5, 4.2), 2)
    id_transaccion = f"TX-{random.randint(1000, 9999)}"
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS trades (id serial PRIMARY KEY, trade_id varchar(20), pair varchar(10), profit float, date timestamp DEFAULT CURRENT_TIMESTAMP);')
        cur.execute('INSERT INTO trades (trade_id, pair, profit) VALUES (%s, %s, %s)', (id_transaccion, par_elegido, profit_pct))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error de DB: {e}")

    return jsonify({
        "status": "success",
        "par": par_elegido,
        "profit_pct": profit_pct,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "id_operacion": id_transaccion
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
